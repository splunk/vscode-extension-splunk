import * as splunk from 'splunk-sdk';
import * as needle from 'needle'; // transitive dependency of splunk-sdk
import * as vscode from 'vscode';
import { SplunkMessage } from './utils/messages';
import { getModuleStatements } from './utils/parsing';

export function getClient(): any {
    const config = vscode.workspace.getConfiguration();
    const restUrl = config.get<string>('splunk.commands.splunkRestUrl');
    const token = config.get<string>('splunk.commands.token');

    let url = new URL(restUrl);
    const scheme = url.protocol.replace(':', '');
    const port = url.port || (scheme === 'https' ? '443' : '80');
    const host = url.hostname;

    let service = new splunk.Service({
        scheme: scheme,
        host: host,
        port: port,
        sessionKey: token,
        authorization: 'Bearer',
    });
    service._originalURL = restUrl;

    return service;
}

export function createSearchJob(jobs, query, options): Promise<any> {
    let request = jobs.create(query, options);
    return request;
}

/**
 * Helper function to create Authorization and Content-Type headers
 * @param service A Javascript SDK Service instance
 * @returns An object reflecting Authorization and Content-Type headers
 */
function makeHeaders(service: any): object {
    return {
        'Authorization': `Bearer ${service.sessionKey}`,
        'Content-Type': 'application/json',
    };
}

/**
 * Check to see if the SDK client is part of a search head cluster, if so return a new
 * client pointing to an individual search head member, such that any search ids created
 * will be immediately available for results rather than waiting for artifact replication
 * across the search head cluster.
 * @param service Instance of the Javascript SDK Service
 * 
 * @returns Promise<void> 
 */
export function getSearchHeadClusterMemberClient(service: any): Promise<any> {
    const shcUrl = `${service.prefix}/services/shcluster/member/members?output_mode=json`;
    console.log(`Attempting to determine SHC info if present using ${shcUrl}`);
    return needle(
        "GET",
        shcUrl,
        {
            'headers': makeHeaders(service),
            'followAllRedirects': true,
            'timeout': 0,
            'strictSSL': false,
            'rejectUnauthorized' : false,
        })
        .then((response) => {
            console.log(`Response from shcUrl status code: ${response.statusCode}`);
            console.log(`Response from shcUrl body: \n'${JSON.stringify(response.body)}'`);
            const data = response.body;
            if (response.statusCode >= 400 ||
                !Object.prototype.isPrototypeOf(data)
                || data.entry === undefined
                || !Array.isArray(data.entry)
                || data.entry.length === 0
                || data.entry[0].content === undefined
                || data.entry[0].content.mgmt_uri === undefined
            ) {
                console.warn("Unsuccessful response from /services/shcluster/member/members endpoint encountered, reverting to original service client.")
                return service;
            }
            // This is in the expected successful response format
            vscode.window.showInformationMessage(`Discovered search head cluster members. Attempting to communicate directly with SH ${data.entry[0].content.mgmt_uri}`);
            const url = new URL(data.entry[0].content.mgmt_uri);
            const scheme = url.protocol.replace(':', '');
            const port = url.port || (scheme === 'https' ? '443' : '80');
            const host = url.hostname;
            const newService = new splunk.Service({
                scheme: scheme,
                host: host,
                port: port,
                sessionKey: service.sessionKey,
                authorization: 'Bearer',
            });
            newService._originalURL = service._originalURL;
            return newService;
        });
}

/**
 * Update a module by calling the PUT /services/spl2/modules/<namespace>.<moduleName>
 * @param service Instance of the Javascript SDK Service
 * @param moduleName Name of the module to append to the namespace to form the request path
 * @param namespace Full namespace to be used directly to form the request path
 * @param module Full contents of the module to update with
 * @returns Promise<void> (or throw Error containing data.messages[])
 */
export function updateSpl2Module(service: any, moduleName: string, namespace: string, module: string): Promise<void> {
    // The Splunk SDK for Javascript doesn't currently support the spl2/modules endpoints
    // nor does it support sending requests in JSON format (only receiving responses), so
    // for now use the underlying needle library that the SDK uses for requests/responses
    console.log(`Request: [PUT] to ${service.prefix}/services/spl2/modules/${encodeURIComponent(namespace)}.${encodeURIComponent(moduleName)}`);
    console.log(`Request Body: \n'${JSON.stringify({
        'name': moduleName,
        'namespace': namespace,
        'definition': module,
    })}'`);
    console.log(`Request Headers: ${JSON.stringify(makeHeaders(service))}`);
    return needle(
        'PUT',
        // example: https://myhost.splunkcloud.com:8089/services/spl2/modules/apps.search._default
        `${service.prefix}/services/spl2/modules/${encodeURIComponent(namespace)}.${encodeURIComponent(moduleName)}`,
        {
            'name': moduleName,
            'namespace': namespace,
            'definition': module,
        },
        {
            'headers': makeHeaders(service),
            'followAllRedirects': true,
            'timeout': 0,
            'strictSSL': false,
            'rejectUnauthorized' : false,
        })
        .then((response) => {
            console.log(`Response status code: ${response.statusCode}`);
            console.log(`Response body: \n'${JSON.stringify(response.body)}'`);
            const data = response.body;
            if (response.statusCode >= 400 ||
                !Object.prototype.isPrototypeOf(data)
                || data.name === undefined
                || data.namespace === undefined
                || data.definition === undefined
                || data.updatedAt === undefined
            ) {
                handleErrorPayloads(data, response.statusCode);
                return;
            }
            // This is in the expected successful response format
            vscode.window.showInformationMessage(`Success! ${data.namespace}.${data.name} updated at ${data.updatedAt}`);
        });
}

/**
 * Dispatch a module to create a job using the POST /servicesNS/-/<app>/search/spl2-module-dispatch endpoint
 * @param service Instance of the Javascript SDK Service
 * @param spl2Module Full text of the SPL2 module to run (contents of a SPL2 notebook cell, for example)
 * @param app App namespace to run within, this will determine /servicesNS/-/<app>/search/spl2-module-dispatch endpoint
 * @param namespace Namespace _within_ the apps.<app> to run, this will be used directly in the body of the request
 * @param earliest Earliest time to be included in the body of the request
 * @param latest Latest time to be included in the body of the request
 * @returns A Promise containing the job information including sid created (or throw an Error containing data.messages[])
 */
export function dispatchSpl2Module(service: any, spl2Module: string, app: string, namespace: string, earliest: string, latest: string): Promise<any>  {
    // For now we're using /services/<app> which doesn't respect relative namespaces,
    // so for now hardcode this to '' but if/when /servicesNS/<app>
    namespace = '';
    app = app || 'search'; // default to search app
    // Get last statement assignment '$my_statement = ...' -> 'my_statement' 
    const statements = getModuleStatements(spl2Module);
    if (!statements || (statements.length < 1)) {
        throw new Error(
            'No statements found in SPL2. Please assign at least one statement name ' +
            'using "$". For example: `$my_statement = from _internal`'
        );
    }
    const statementIdentifier = statements[statements.length - 1];
    const params = {
        'timezone': 'Etc/UTC',
        'collectFieldSummary': true,
        'collectEventSummary': false,
        'collectTimeBuckets': false,
        'output_mode': 'json_cols',
        'status_buckets': 300,
    };
    if (earliest !== undefined) {
        params['earliest'] = earliest;
    }
    if (latest !== undefined) {
        params['latest'] = latest;
    }

    // The Splunk SDK for Javascript doesn't currently support the spl2-module-dispatch endpoint
    // nor does it support sending requests in JSON format (only receiving responses), so
    // for now use the underlying needle library that the SDK uses for requests/responses
    console.log(`Request: [POST] to ${service.prefix}/servicesNS/-/${encodeURIComponent(app)}/search/spl2-module-dispatch`);
    console.log(`Request Body: \n'${JSON.stringify({
        'module': spl2Module,
        'namespace': namespace,
        'queryParameters': {
            [statementIdentifier]: params
        }
    })}'`);
    console.log(`Request Headers: ${JSON.stringify(makeHeaders(service))}`);
    return needle(
        'POST',
        `${service.prefix}/servicesNS/-/${encodeURIComponent(app)}/search/spl2-module-dispatch`,
        {
            'module': spl2Module,
            'namespace': namespace,
            'queryParameters': {
                [statementIdentifier]: params
            }
        },
        {
            'headers': makeHeaders(service),
            'followAllRedirects': true,
            'timeout': 0,
            'strictSSL': false,
            'rejectUnauthorized': false,
        })
        .then((response) => {
            console.log(`Response status code: ${response.statusCode}`);
            console.log(`Response body: \n'${JSON.stringify(response.body)}'`);
            console.log(`Response headers: \n'${JSON.stringify(response.headers)}'`);
            const data = response.body;
            if (response.statusCode >= 400 || !Array.prototype.isPrototypeOf(data) || data.length < 1) {
                handleErrorPayloads(data, response.statusCode);
                return;
            }
            // This is in the expected successful response format
            const sid = data[0]['sid'];
            return getSearchJobBySid(service, sid);
        });
}

function handleErrorPayloads(data: any, statusCode: number) {
    // Response is not in expected successful format, let's handle a
    // few different error cases and raise as expected messages format
    console.warn(`Error making request: ${JSON.stringify(data)}`);
    let messages:SplunkMessage[] = [];
    // Override error messages for common scenarios
    switch(statusCode) {
        case 401:
            data = {
                code: statusCode,
                message: 'Unauthenticated, make sure the Token and Splunk Rest\n' +
                    'Url settings are correct in the Splunk Extension Settings',
            };
            break;
        case 404:
            data = {
                code: statusCode,
                message: 'Endpoint not found, ensure that the Splunk deployment\n' +
                    'specified in Splunk Rest Url supports SPL2 and the namespace\n' +
                    'specified for the module is of the form apps.<myapp> where\n' +
                    '<myapp> is an app that has been created on the deployment.',
            }
            break;
    }
    if (Object.prototype.isPrototypeOf(data)) {
        if (data.name === 'response'
            && Array.prototype.isPrototypeOf(data.children)) {
            // Reformat messages for errors such as unauthorized
            messages = data.children
                .filter((child) => child.name === 'messages')
                .flatMap((msgs) => msgs.children)
                .map((msg) => new Object({
                        'type': msg?.attributes?.type,
                        'code': msg.name,
                        'text': msg.value,
                }));
        } else if (data.code !== undefined && data.message !== undefined) {
            // Reformat if returns a `code` and `message for errors such
            // as invalid request body format
            messages = [{
                'type': 'error',
                'code': data.code,
                'text': data.message,
            }];
        }
    }
    // If we still haven't handled this unsuccessful response then simply
    // output the body as an error message
    if (messages.length === 0) {
        messages = [{
            'type': 'error',
            'code': '',
            'text': `Error making request: ${JSON.stringify(data)}`,
        }];
    }
    throw new Object({
        'data': {
            'messages': messages,
        },
    });
}

export function getSearchJobBySid(service, sid): Promise<any> {
    let request = service.getJob(sid);
    return request;
}


export function getSearchJob(job): Promise<any> {
    let request = job.fetch();
    return request;
}

export function getJobSearchLog(job): Promise<any> {
    let request = job.searchlog();
    return request;
}

export function getSearchJobResults(job): Promise<any> {
    let request = job.get("results", {"output_mode": "json_cols"});
    return request;
}

export function cancelSearchJob(job): Promise<any> {
    let request = job.cancel();
    return request;
}

export function wait(ms = 1000): Promise<void> {
    return new Promise(resolve => {
      setTimeout(resolve, ms);
    });
}
