const vscode = require('vscode');

const splunkUrl = vscode.workspace.getConfiguration().get('splunk.commands.splunkRestUrl');
const splunkToken = vscode.workspace.getConfiguration().get('splunk.commands.token');
const enableCertificateVerification = vscode.workspace
    .getConfiguration()
    .get('splunk.commands.enableCertificateVerification');
const https = require('https');
const axios = require('axios');

axios.defaults.headers.common['Authorization'] = `Bearer ${splunkToken}`;

const agent = new https.Agent({
    rejectUnauthorized: enableCertificateVerification,
});

async function fullDebugRefresh(splunkOutputChannel) {
    /* Similar to debug/refresh - this command reloads all reloadable EAI handlers minus auth-services */

    const outputMode = 'json';

    try {
        /* Query for all /services/admin handlers */
        const adminResponse = await axios({
            method: 'GET',
            url: `${splunkUrl}/services/admin?output_mode=${outputMode}`,
            httpsAgent: agent,
        });
        /* Query for all UI handlers */
        const dataResponse = await axios({
            method: 'GET',
            url: `${splunkUrl}/services/data/ui?output_mode=${outputMode}`,
            httpsAgent: agent,
        });

        let jsonResult = await adminResponse.data;
        const dataResult = await dataResponse.data;
        jsonResult['entry'] = jsonResult['entry'].concat(dataResult['entry']);

        /* Identify which handlers can be reloaded */
        const reloadable = jsonResult['entry'].filter((entry) => {
            return '_reload' in entry['links'] && entry['name'] !== 'auth-services';
        });

        const reloadRequests = reloadable.map(async (entry) => {
            return await axios({
                method: 'POST',
                url: `${splunkUrl}${entry['links']['_reload']}`,
                httpsAgent: agent,
            });
        });

        /* Reload all handlers */
        const results = await Promise.allSettled(reloadRequests);
        vscode.window.showInformationMessage(`Performed _reload on ${results.length} EAI handlers`);
    } catch (error) {
        vscode.window.showErrorMessage(
            `Could not enumerate handlers to refresh. ${error.message}`
        );
        return
    }
    /* Log results to Output */
    splunkOutputChannel.appendLine(
        results
            .map((entry) => {
                const status = entry.status == 'fulfilled' ? 'OK' : 'ERROR';
                let endpoint =
                    status == 'OK' ? entry.value.request.path : entry.reason.request.path;
                endpoint = endpoint.replace('/services/', '').replace('/_reload', '');
                return `Refreshing ${endpoint}: ${status}\n`;
            })
            .join('')
    );

    splunkOutputChannel.show();
}

exports.fullDebugRefresh = fullDebugRefresh;
