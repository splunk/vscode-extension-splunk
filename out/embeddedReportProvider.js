"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = require("vscode");
const splunkToken = vscode.workspace.getConfiguration().get('splunk.commands.token');
const splunkUrl = vscode.workspace.getConfiguration().get('splunk.commands.splunkRestUrl');
const enableCertificateVerification = vscode.workspace.getConfiguration().get('splunk.commands.enableCertificateVerification');
const https = require("https");
const axios = require("axios");

axios.defaults.headers.common["Authorization"] = `Bearer ${splunkToken}`;
const agent = new https.Agent({
    rejectUnauthorized: enableCertificateVerification
});

const splunkSavedSearchProvider = require("./searchProvider.js");

class SplunkReportProvider {
    constructor() {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }

    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren() {
        let savedSearchProvider = new splunkSavedSearchProvider.SavedSearchProvider();
        let search = encodeURIComponent("embed.enabled=1");
        return Promise.resolve(savedSearchProvider.getSavedSearches(search));
    }
   
}
exports.SplunkReportProvider = SplunkReportProvider;


async function getSavedSearchEmbedToken(searchLink) {
    
    if ((!splunkUrl) || (!splunkToken)) {
        return [new vscode.TreeItem("Splunk URL and Token required. Check extension settings.")];
    }

    let embedToken = null;
   
    await axios.get(`${splunkUrl}${searchLink}?output_mode=json&f=embed*`, {httpsAgent: agent})
        .then(response => {
            let search = response.data.entry[0];
            if((search) && (search["content"].hasOwnProperty("embed.token"))) {
                embedToken = search["content"]["embed.token"]
            }
        })
        .catch(error => {
            vscode.window.showErrorMessage(`Could not get saved search. Check extension settings. ${error.message}`);
        })
    return(embedToken);
}

async function getWebviewContent(search) {
    let splunkSHUrl = vscode.workspace.getConfiguration().get('splunk.reports.SplunkSearchHead');
    let embedToken = await getSavedSearchEmbedToken(search["links"]["list"]).then()
    let iframeSrc = `${splunkSHUrl}/en-US/embed?s=${encodeURIComponent(search["links"]["list"])}&oid=${embedToken}`;
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <title>Splunk Report</title>
</head>
<body>
<iframe width="100%" height="300px" frameborder="0" src="${iframeSrc}"></iframe>
</body>
</html>`;
}

exports.getWebviewContent = getWebviewContent