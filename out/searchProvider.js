"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = require("vscode");
const axios = require("axios");

class SearchProvider {
    constructor() {
        this.splunkUrl = vscode.workspace.getConfiguration().get('splunk.commands.splunkRestUrl');
        this.splunkToken = vscode.workspace.getConfiguration().get('splunk.commands.token');
        this.outputMode = vscode.workspace.getConfiguration().get('splunk.search.searchOutputMode');
        this.enableCertificateVerification = vscode.workspace.getConfiguration().get('splunk.commands.enableCertificateVerification');
        if (!this.enableCertificateVerification) {
            process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = 0;
        } else {
            process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = 1;
        }
        axios.defaults.headers.common["Authorization"] = `Bearer ${this.splunkToken}`;
    }

    async runSearch(search) {

        if (!this.splunkUrl) {
            let m = "The URL specified for the Splunk REST API is incorrect. Please check your settings."
            vscode.window.showErrorMessage(m);
            throw Error(m)
        }

        if(!this.splunkToken) {
            let m = "A Splunk autorization token is required. Please check your settings."
            vscode.window.showErrorMessage(m);
            throw Error(m)
        }

        let searchResults = "No results";
        await axios(
            {
                method: "POST",
                url: `${this.splunkUrl}/services/search/v2/jobs/export?output_mode=${this.outputMode}`,
                data: "search=" + encodeURIComponent(`search ${search}`)
            })
            .then(response => {
                if (response.data != '') {
                    searchResults = response.data;
                }
            })
            .catch(error => {
                vscode.window.showErrorMessage(`Could not run saved searched. ${error.message}\n${error.response.data}`);
            })
        return searchResults;
    }
}
exports.SearchProvider = SearchProvider;

class SavedSearchProvider {
    constructor() {
        this.splunkUrl = vscode.workspace.getConfiguration().get('splunk.commands.splunkRestUrl');
        this.splunkToken = vscode.workspace.getConfiguration().get('splunk.commands.token');
        this.outputMode = vscode.workspace.getConfiguration().get('splunk.search.searchOutputMode');
        this.enableCertificateVerification = vscode.workspace.getConfiguration().get('splunk.commands.enableCertificateVerification');
        if (!this.enableCertificateVerification) {
            process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = 0;
        } else {
            process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = 1;
        }
        axios.defaults.headers.common["Authorization"] = `Bearer ${this.splunkToken}`;
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
        return Promise.resolve(this.getSavedSearches());
    }

    async getSavedSearches(filter="") {

        if ((!this.splunkUrl) || (!this.splunkToken)) {
            return [new vscode.TreeItem("Splunk URL and Token required. Check extension settings.")];
        }
        if(filter) {
            filter = `&search=${filter}`
        }

        let savedSearchArray = [];
        await axios.get(`${this.splunkUrl}/servicesNS/-/-/saved/searches?sort_key=name&f=acl*&f=disabled&count=0&output_mode=json${filter}`)
            .then(response => {
                response.data.entry.forEach(search => {
                    if(!search.content.disabled) {
                        savedSearchArray.push(new SavedSearch(search["name"], search["acl"]["app"], search["acl"]["owner"], search["links"]));
                    }
                });
            })
            .catch(error => {
                if (error.code = 'ECONNREFUSED' ) {
                    vscode.window.showErrorMessage(`Could not connect to Splunk server. Please check extension settings. ${error.message}`);
                } else {
                    vscode.window.showErrorMessage(`Could not enumerate saved searches. ${error.message}`);
                }
            })
        return(savedSearchArray);
    }

    async runSavedSearch(savedSearchItem) {

        if (!this.splunkUrl) {
            let m = "The URL specified for the Splunk REST API is incorrect. Please check your settings."
            vscode.window.showErrorMessage(m);
        }

        if(!this.splunkToken) {
            let m = "A Splunk autorization token is required. Please check your settings."
            vscode.window.showErrorMessage(m);
        }

        let searchResults = "No results";
        await axios(
            {
                method: "POST",
                url: `${this.splunkUrl}/servicesNS/${savedSearchItem.owner}/${savedSearchItem.app}/search/v2/jobs/export?output_mode=${this.outputMode}`,
                data: "search=" + encodeURIComponent(`| savedsearch "${savedSearchItem.label}"`)
            })
            .then(response => {
                if (response.data != '') {
                    searchResults = response.data;
                }
            })
            .catch(error => {
                vscode.window.showErrorMessage(`Could not run saved searched. ${error.message}\n${error.response.data}`);
            })
        return searchResults;
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