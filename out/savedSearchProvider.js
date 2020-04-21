"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = require("vscode");
const request = require("request");

class SavedSearchProvider {
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
        return Promise.resolve(this.getSavedSearches());
    }

    async getSavedSearches(filter="") {

        let splunkUrl = vscode.workspace.getConfiguration().get('splunk.commands.restUrl');
        let splunkToken = vscode.workspace.getConfiguration().get('splunk.commands.token');
        if ((!splunkUrl) || (!splunkToken)) {
            return [new vscode.TreeItem("Splunk URL and Token required. Check extension settings.")];
        }
        if(filter) {
            filter = `&search=${filter}`
        } 

        let savedSearches = new Promise(function(resolve, reject) {
            let savedSearchArray = []
            request(
                {
                    method: "GET",
                    uri: `${splunkUrl}/servicesNS/-/-/saved/searches?sort_key=name&f=acl*&count=0&output_mode=json${filter}`,
                    strictSSL: false,
                    headers : {
                        "Authorization": `Bearer ${splunkToken}`
                    },
                },
                function (error, response, body) {
                    if(error) {
                        vscode.window.showErrorMessage(error.message);
                        reject(Error("Could not enumerate saved searches. Check extension settings."))
                    } else {
                        JSON.parse(body)["entry"].forEach(search => {
                            savedSearchArray.push(new SavedSearch(search["name"], search["acl"]["app"], search["acl"]["owner"], search["links"]))
                        });

                        resolve(savedSearchArray)
                    }
                }
            )
        });
        return await(savedSearches);
    }

    async runSavedSearch(savedSearchItem) {

        let splunkUrl = vscode.workspace.getConfiguration().get('splunk.commands.restUrl');
        let splunkToken = vscode.workspace.getConfiguration().get('splunk.commands.token');
        let outputMode = vscode.workspace.getConfiguration().get('splunk.search.searchOutputMode');

        if (!splunkUrl) {
            let m = "The URL specified for the Splunk REST API is incorrect. Please check your settings."
            vscode.window.showErrorMessage(m);
            reject(Error(m))
        }

        if(!splunkToken) {
            let m = "A Splunk autorization token is required. Please check your settings."
            vscode.window.showErrorMessage(m);
            reject(Error(m))
        }

        let searchResults = new Promise(function(resolve, reject) {
            request(
                {
                    method: "POST",
                    uri: `${splunkUrl}/servicesNS/${savedSearchItem.owner}/${savedSearchItem.app}/search/jobs/export?output_mode=${outputMode}`,
                    strictSSL: false,
                    headers : {
                        "Authorization": `Bearer ${splunkToken}`
                    },
                    body: "search=" + encodeURIComponent(`| savedsearch "${savedSearchItem.label}"`)
                    
                },
                function (error, response, body) {
                    if(error) {
                        vscode.window.showErrorMessage(error.message);
                        reject(Error("Could not run saved search"))
                    } else {
                        resolve(body)
                    }
                }
            )
        });

        return await(searchResults);

    }
   
}
exports.SavedSearchProvider = SavedSearchProvider;

class SavedSearch extends vscode.TreeItem {
    constructor(searchName, app, owner, links) {
        super(searchName);
        this.label = searchName;
        this.app = app;
        this.owner = owner;
        this.links = links;
        this.contextValue = 'savedSearch';
    }
}
exports.SavedSearch = SavedSearch;

function getSearchEmbedToken(search) {
    
        request(
            {
                method: "POST",
                uri: `${splunkUrl}/services/search/jobs/export?output_mode=${outputMode}`,
                strictSSL: false,
                headers : {
                    "Authorization": `Bearer ${splunkToken}`
                },
                body: "search=" + encodeURIComponent(`search ${search}`)
                
            },
            function (error, response, body) {
                if(error) {
                    vscode.window.showErrorMessage(error.message)
                } else {
                    splunkOutputChannel.appendLine(body)
                }
            }
        )

    
} 

//# sourceMappingURL=SavedSearchProvider.js.map