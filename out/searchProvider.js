"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = require("vscode");
const splunkUrl = vscode.workspace.getConfiguration().get('splunk.commands.splunkRestUrl');
const splunkToken = vscode.workspace.getConfiguration().get('splunk.commands.token');
const outputMode = vscode.workspace.getConfiguration().get('splunk.search.searchOutputMode');
const enableCertificateVerification = vscode.workspace.getConfiguration().get('splunk.commands.enableCertificateVerification');
const https = require("https");
const axios = require("axios");

axios.defaults.headers.common["Authorization"] = `Bearer ${splunkToken}`;
const agent = new https.Agent({  
    rejectUnauthorized: enableCertificateVerification
});

class SearchProvider {
    constructor() {}

    async runSearch(search) {
        if (!splunkUrl) {
            let m = "A URL for the Splunk REST API is required. Please check your settings."
            vscode.window.showErrorMessage(m);
            throw Error(m)
        }

        if(!splunkToken) {
            let m = "A Splunk autorization token is required. Please check your settings."
            vscode.window.showErrorMessage(m);
            throw Error(m)
        }

        let searchResults = "No results";
        await axios(
            {
                method: "POST",
                url: `${splunkUrl}/services/search/jobs/export?output_mode=${outputMode}`,
                httpsAgent: agent,
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

        if ((!splunkUrl) || (!splunkToken)) {
            return [new vscode.TreeItem("Splunk URL and Token required. Check extension settings.")];
        }
        if(filter) {
            filter = `&search=${filter}`
        }

        let savedSearchArray = [];
        await axios.get(`${splunkUrl}/servicesNS/-/-/saved/searches?sort_key=name&f=acl*&f=disabled&count=0&output_mode=json${filter}`, {httpsAgent: agent})
            .then(response => {
                response.data.entry.forEach(search => {
                    if(!search.content.disabled) {
                        savedSearchArray.push(new SavedSearch(search["name"], search["acl"]["app"], search["acl"]["owner"], search["links"]));
                    }
                });
            })
            .catch(error => {
                vscode.window.showErrorMessage(`Could not enumerate saved searches. ${error.message}`);
            })
        return(savedSearchArray);
    }

    async runSavedSearch(savedSearchItem) {

        if (!splunkUrl) {
            let m = "The URL specified for the Splunk REST API is incorrect. Please check your settings."
            vscode.window.showErrorMessage(m);
            throw Error(m)
        }

        if(!splunkToken) {
            let m = "A Splunk autorization token is required. Please check your settings."
            vscode.window.showErrorMessage(m);
            throw Error(m)
        }

        let searchResults = "No results";
        await axios(
            {
                method: "POST",
                url: `${splunkUrl}/servicesNS/${savedSearchItem.owner}/${savedSearchItem.app}/search/jobs/export?output_mode=${outputMode}`,
                httpsAgent: agent,
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