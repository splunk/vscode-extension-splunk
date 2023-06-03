import * as splunk from 'splunk-sdk';
import * as needle from 'needle'; // transitive dependency of splunk-sdk
import * as vscode from 'vscode';

export function getClient() {
    const config = vscode.workspace.getConfiguration();
    const restUrl = config.get<string>('splunk.commands.splunkRestUrl');
    const token = config.get<string>('splunk.commands.token');

    let url = new URL(restUrl);
    const scheme = url.protocol.replace(':', '');
    const port = url.port;
    const host = url.hostname;

    let service = new splunk.Service({
        scheme: scheme,
        host: host,
        port: port,
        sessionKey: token,
        version: '8',
        authorization: 'Bearer',
    });

    return service;
}

export function splunkLogin(service) {

    return new Promise(function(resolve, reject) {
        
        service.login(function(err, wasSuccessful) {
            if (err !== null || !wasSuccessful) {
                reject(err);
            } else {
                resolve(null);
            }
        });

    });


}


export function createSearchJob(jobs, query, options) {
    return new Promise(function(resolve, reject) {
        jobs.create(query, options, function(err, data) {
            if (err !== null) {
                reject(err);
            } else {
                resolve(data);
            }
        });

    });
}

export function dispatchSpl2Module(service: any, spl2Module: string) {
    // Get first statement assignment '$my_statement = ...' -> 'my_statement' 
    const statementMatch = spl2Module.match(/\$([a-zA-Z0-9_]+)[\s]*=/m);
    if (!statementMatch || statementMatch.length < 2) {
        throw new Error(
            'No statements found in SPL2. Please assign at least one statement name ' +
            'using "$". For example: `$my_statement = from _internal`'
        );
    }
    const statementIdentifier = statementMatch[1];

    // The Splunk SDK for Javascript doesn't currently support the spl2-module-dispatch endpoint
    // nor does it support sending requests in JSON format (only receiving responses), so
    // for now use the underlying needle library that the SDK uses for requests/responses
    return new Promise(function(resolve, reject) {
        needle.request(
            'POST',
            `${service.prefix}/services/search/spl2-module-dispatch?output_mode=json`,
            {
                'module': spl2Module,
                'namespace': '',
                'queryParameters': {
                    [statementIdentifier]: {
                        'timezone': 'Etc/UTC',
                        'collectFieldSummary': true,
                        'collectEventSummary': false,
                        'collectTimeBuckets': false,
                        'output_mode': 'json_cols',
                        'status_buckets': 300,
                    }
                }
            },
            {
                'headers': {
                    'Authorization': `Bearer ${service.sessionKey}`,
                    'Content-Type': 'application/json',
                },
                'followAllRedirects': true,
                'timeout': 0,
                'strictSSL': false,
                'rejectUnauthorized' : false,
            },
            async function(err, response, data) {
                if (err !== null) {
                    reject(err);
                } else {
                    if (!Array.prototype.isPrototypeOf(data) || data.length < 0) {
                        reject(`Invalid response: '${JSON.stringify(response.body)}'`);
                    } else {
                        const sid = data[0]['sid'];
                        try {
                            const job = await getSearchJobBySid(service, sid);
                            resolve(job);
                        } catch (err) {
                            reject(err);
                        }
                    }
                }
            }
        );
    });
}

export function getSearchJobBySid(service, sid) {
    return new Promise(function(resolve, reject) {
        service.getJob(sid, function(err, data) {
            if (err != null) {
                reject(err);
            } else {
                resolve(data);
            }
        });
    });
}


export function getSearchJob(job) {
    return new Promise(function(resolve, reject) {
        job.fetch(function(err, job) {
            if (err !== null) {
                reject(err);
            } else {
                resolve(job);
            }
        });

    });
}

export function getJobSearchLog(job) {
    return new Promise(function(resolve, reject) {
        job.searchlog(function(err, log) {
            if (err !== null) {
                reject(err);
            } else {
                resolve(log);
            }
        });

    });
}

export function getSearchJobResults(job) {
    return new Promise(function(resolve, reject) {
        job.get("results", {"output_mode": "json_cols"},function(err, results) {
            if (err !== null) {
                reject(err);
            } else {
                resolve(results);
            }
        });

    });
}

export function cancelSearchJob(job) {
    return new Promise(function(resolve, reject) {
        job.cancel(function(err, results) {
            if (err !== null) {
                reject(err);
            } else {
                resolve(results);
            }

        });
    });
}

export function wait(ms = 1000) {
    return new Promise(resolve => {
      setTimeout(resolve, ms);
    });
}