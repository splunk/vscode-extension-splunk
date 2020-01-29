"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = require("vscode");
const request = require("request");
const splunkSavedSearchProvider = require("./savedSearchProvider.js");

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
    getChildren(element) {
        let savedSearchProvider = new splunkSavedSearchProvider.SavedSearchProvider();
        let search = encodeURIComponent("embed.enabled=1");
        return Promise.resolve(savedSearchProvider.getSavedSearches(search));
    }
   
}
exports.SplunkReportProvider = SplunkReportProvider;


async function getSavedSearchEmbedToken(searchLink) {

    let splunkUrl = vscode.workspace.getConfiguration().get('splunk_conf.commands.splunk REST Url');
    let splunkToken = vscode.workspace.getConfiguration().get('splunk_conf.commands.token');
    if ((!splunkUrl) || (!splunkToken)) {
        return [new vscode.TreeItem("Splunk URL and Token required. Check extension settings.")];
    }
    
    let embedToken = new Promise(function(resolve, reject){
        request(
            {
                method: "GET",
                uri: `${splunkUrl}${searchLink}?output_mode=json&f=embed*`,
                strictSSL: false,
                headers : {
                    "Authorization": `Bearer ${splunkToken}`
                },
            },
            function (error, response, body) {
                if(error) {
                    vscode.window.showErrorMessage(error.message);
                    reject(Error("Could not get saved search. Check extension settings."))
                } else {
                    let search = JSON.parse(body)["entry"][0];
                    if((search) && (search["content"].hasOwnProperty("embed.token"))) {
                        resolve(search["content"]["embed.token"]);
                    }
                }
            }
        );
    })

    return await(embedToken);
}

async function getWebviewContent(search) {
    let splunkSHUrl = vscode.workspace.getConfiguration().get('splunk_conf.reports.SplunkSearchHead');
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

//# sourceMappingURL=embeddedReportProvider.js.map