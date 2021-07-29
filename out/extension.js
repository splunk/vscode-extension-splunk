"use strict";
Object.defineProperty(exports, "__esModule", { value: true });

const vscode = require("vscode");
const path = require("path");
const fs = require("fs");
const request = require("request");
const splunkSavedSearchProvider = require("./savedSearchProvider.js");
const splunkEmbeddedReportProvider = require("./embeddedReportProvider");
const splunkFoldingRangeProvider = require("./foldingRangeProvider.js");
const splunkModViz = require('./modViz.js');
const splunkCustomCommand = require('./customCommand.js');
const globalConfigPreview = require('./globalConfigPreview')
const splunkCustomRESTHandler = require('./customRESTHandler.js')
const splunkSpec = require("./spec.js");
const { get } = require("request");
const PLACEHOLDER_REGEX = /\<([^\>]+)\>/g
const DROPDOWN_PLACEHOLDER_REGEX = /(\[|{)\w+(\|\w+)+(]|})/g
const STANZA_REGEX = /^\[(?<stanza>[^\]].*?)\]/
const SETTING_REGEX = /^(?<setting>[\w\-_\<\>\.]+)\s*=\s*(?<value>[^\r\n]+)/
let specConfigs = {};
let timeout = undefined;
let diagnosticCollection = undefined;
let specConfig = undefined;

function getParentStanza(document, line) {
    // Start at the passed in line and go backwards
    // up the document until we find a line that starts with
    // '[' indicating a stanza.
    for (var i=line; i >= 0; i--) {
        if(document.lineAt(i).text.startsWith("[")) {
            return document.lineAt(i).text
        }
    }
    // No parent stanza, so any settings here apply to [default]
    return "[default]"
}

function getDocumentItems(document, PATTERN) {
    // Given a pattern, return line numbers that match that pattern

    let items = []

    for (var i=0; i < document.lineCount; i++) {
        if(PATTERN.test(document.lineAt(i).text)) {
            // If the parent line ends with a '\', this is a continuation line,
            // so do not add it.
            if(i>0 && PATTERN == SETTING_REGEX && document.lineAt(i-1) && document.lineAt(i-1).text.trim().endsWith("\\")) {
                continue
            }
            let item = {}
            item["text"] = document.lineAt(i).text
            item["line"] = i
            items.push(item)
        }
    }

    return items
}

function activate(context) {

    let splunkOutputChannel = vscode.window.createOutputChannel("Splunk");

    // Setup globalConfig.json preview
    globalConfigPreview.init(context);
    
    // Set up Splunk report viewer
    const embeddedReportProvider = new splunkEmbeddedReportProvider.SplunkReportProvider();
    vscode.window.registerTreeDataProvider('embeddedReports', embeddedReportProvider);
    vscode.commands.registerCommand('splunk.embeddedReport.refresh', () => embeddedReportProvider.refresh());
    const viewRefreshInterval = vscode.workspace.getConfiguration('splunk').get('reports.viewRefreshInterval') * 1000;
    vscode.commands.registerCommand('splunk.embeddedReport.show', report => {
        const panel = vscode.window.createWebviewPanel(
            'splunkWebview', 
            'Splunk Report', 
            vscode.ViewColumn.One, 
            {
                enableScripts: true,
                retainContextWhenHidden: false
            }
        );
        const updateWebview = async () => {
            panel.webview.html = await splunkEmbeddedReportProvider.getWebviewContent(report);
        }

        updateWebview();
        const interval = setInterval(updateWebview, viewRefreshInterval);
        panel.onDidDispose( () => {
            clearInterval(interval);
        }, null, context.subscriptions);
        
    });

    // Set up Splunk saved search viewer
    const savedSearchProvider = new splunkSavedSearchProvider.SavedSearchProvider();
    vscode.window.registerTreeDataProvider('savedSearches', savedSearchProvider);
    vscode.commands.registerCommand('splunk.savedSearches.refresh', () => savedSearchProvider.refresh());
    vscode.commands.registerCommand('splunk.savedSearch.run', async search => {
        if(!search) {
            search = await vscode.window.showQuickPick(savedSearchProvider.getSavedSearches(), {canPickMany: false, placeHolder:'Saved Search'})
        }
        let searchResult = await savedSearchProvider.runSavedSearch(search);
        splunkOutputChannel.appendLine(searchResult);
        splunkOutputChannel.show()
    });

    // Set up Splunk ad-hoc search command
    context.subscriptions.push(vscode.commands.registerCommand('splunk.search.adhoc', async () => {
        let splunkUrl = vscode.workspace.getConfiguration().get('splunk.commands.splunkRestUrl')
        let splunkToken = vscode.workspace.getConfiguration().get('splunk.commands.token')
        let outputMode = vscode.workspace.getConfiguration().get('splunk.search.searchOutputMode')
        
        if (!splunkUrl) {
            vscode.window.showErrorMessage("The URL specified for the Splunk REST API is incorrect. Please check your settings.");
            return
        }
        if(!splunkToken) {
            vscode.window.showErrorMessage("A Splunk autorization token is required. Please check your settings.");
            return
        }
        let search = await vscode.window.showInputBox({
            prompt:'Search SPL'
        })
        if (search) {
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

            splunkOutputChannel.show()
        }
    }));

    // Set up Splunk modular visualization creator
    context.subscriptions.push(vscode.commands.registerCommand('splunk.new.modviz', async () => {
        let destFolder = await vscode.window.showOpenDialog({
            canSelectFiles: false,
            canSelectFolders: true,
            canSelectMany: false,
            openLabel: "Select project path"
        });

        let modVizName = await vscode.window.showInputBox({
            placeHolder: "Visualization name",
            prompt: "Specify a name for this custom visualization."
        })

        if((!destFolder) || (!modVizName)) {
            return
        } else {
            splunkModViz.createModViz(modVizName, destFolder, context);
            vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(path.join(destFolder[0].path, modVizName)), true);
            vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(path.join(destFolder[0].path, modVizName, "appserver", "static", "visualizations", modVizName, "src", "visualization_source.js")));
            vscode.env.openExternal(vscode.Uri.parse('https://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/CustomVizTutorial#Create_the_visualization_logic'));
        }

    }));

    // Set up Splunk custom search command creator
    context.subscriptions.push(vscode.commands.registerCommand('splunk.new.command', async () => {
        let destFolder = await vscode.window.showOpenDialog({
            canSelectFiles: false,
            canSelectFolders: true,
            canSelectMany: false,
            openLabel: "Select project path"
        });

        let commandAppName = await vscode.window.showInputBox({
            placeHolder: "App name",
            prompt: "Specify an app name for this custom command."
        })

        if((!destFolder) || (!commandAppName)) {
            return
        } else {
            splunkCustomCommand.createCommand(commandAppName, destFolder, context);
            vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(path.join(destFolder[0].path, commandAppName)), true);
            vscode.env.openExternal(vscode.Uri.parse('https://dev.splunk.com/enterprise/docs/developapps/customsearchcommands/createcustomsearchcmd'));
        }

    }));

    // Set up Splunk custom REST handler creator
    context.subscriptions.push(vscode.commands.registerCommand('splunk.new.resthandler', async () => {
        let destFolder = await vscode.window.showOpenDialog({
            canSelectFiles: false,
            canSelectFolders: true,
            canSelectMany: false,
            openLabel: "Select project path"
        });

        let handlerAppName = await vscode.window.showInputBox({
            placeHolder: "App name",
            prompt: "Specify an app name for this custom REST handler."
        })

        if((!destFolder) || (!handlerAppName)) {
            return
        } else {
            splunkCustomRESTHandler.createRESTHandler(handlerAppName, destFolder, context);
            vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(path.join(destFolder[0].path, handlerAppName)), true);
            // vscode.env.openExternal(vscode.Uri.parse('https://github.com/jrervin/splunk-rest-examples'));
        }

    }));

    // Set up stanza folding
    context.subscriptions.push(vscode.languages.registerFoldingRangeProvider([
        { language: 'splunk', pattern: '**/*.{conf,conf.spec}' }
    ], new splunkFoldingRangeProvider.confFoldingRangeProvider()));

    // If vscode was opened with an active .conf file, handle it.
    if(vscode.window.activeTextEditor && vscode.window.activeTextEditor.document.languageId === 'splunk') {
        handleSplunkConfFile(context);
    }

    // Set up listener for text document changes
    context.subscriptions.push(vscode.workspace.onDidChangeTextDocument(editor => {
        if(vscode.window.activeTextEditor && vscode.window.activeTextEditor.document.languageId === 'splunk') {
            // Use a timer on onDidChangeTextDocument so we are not linting as often.
            triggerDiagnostics(specConfig, editor.document, diagnosticCollection);
        }
    }));

    // Set up listener for active editor changing
    context.subscriptions.push(vscode.window.onDidChangeActiveTextEditor(editor => {
        if (vscode.window.activeTextEditor && vscode.window.activeTextEditor.document.languageId === 'splunk') {
            handleSplunkConfFile(context);
        }
    }));
}
exports.activate = activate;

function handleSplunkConfFile(context) {

    if(diagnosticCollection === undefined) {
        diagnosticCollection = vscode.languages.createDiagnosticCollection('splunk');
    }

    let currentDocument = path.basename(vscode.window.activeTextEditor.document.uri.fsPath);
    let specFileName = currentDocument + ".spec";
    let specFilePath = getSpecFilePath(context.extensionPath, currentDocument);

    if(specConfigs.hasOwnProperty(specFileName)) {
        specConfig = specConfigs[specFileName];
    } else {
        specConfig = splunkSpec.getSpecConfig(specFilePath);

        // Register Stanza completion items for this spec
        context.subscriptions.push(provideStanzaCompletionItems(specConfig));

        // Register Setting completion items for this spec
        let trimWhitespace = vscode.workspace.getConfiguration().get('splunk.spec.trimEqualSignWhitespace')
        context.subscriptions.push(provideSettingCompletionItems(specConfig, trimWhitespace));
    }

    // Set up diagnostics (linting)
    updateDiagnostics(specConfig, vscode.window.activeTextEditor.document, diagnosticCollection);

    // Cache specConfig
    specConfigs[specFileName] = specConfig
}

function getSpecFilePath(basePath, filename) {

    // Get the custom configuration options
    let settingsSpecFilePath = vscode.workspace.getConfiguration('splunk').get('spec.FilePath');
    let settingsSpecFileVersion  = vscode.workspace.getConfiguration('splunk').get('spec.FileVersion');

    let specFileName = filename + ".spec";
    let specFilePath;

    // Create a path to the spec file for the current document
    if(!settingsSpecFilePath) {
        // No path was configured in settings, so create a path to the built-in spec files
        if(specFileName == "eventgen.conf.spec") {
            specFilePath = path.join(basePath, "spec_files", specFileName)
        } else {
            specFilePath = path.join(basePath, "spec_files", settingsSpecFileVersion, specFileName)
        }
    } else {
        specFilePath = path.join(specFilePath, specFileName)
    }

    // Check if the file exists
    if(!fs.existsSync(specFilePath)) {
        vscode.window.showErrorMessage(`Spec file path not found: ${specFilePath}`)
        return null
    }
    return specFilePath;
}

function provideStanzaCompletionItems(specConfig) {

    // Get the currently open document
    let currentDocument = path.basename(vscode.window.activeTextEditor.document.uri.fsPath)

    let stanzaCompletions = vscode.languages.registerCompletionItemProvider({ language: 'splunk', pattern: `**/${currentDocument}`}, {

        provideCompletionItems(document, position, token, context) {

            if((position.character != 1) || (!document.lineAt(position.line).text.startsWith('['))) {
                // We are not typing a stanza, so return.
                return
            }
        
            if(!specConfig) {
                // No completion for you!
                return
            }

            let completions = []

             // Create completion items for stanzas - you can create a stanza anywhere
            specConfig["stanzas"].forEach(stanza => {
                let stanzaSnippet = stanza.stanzaName
                let stanzaCompletionItem = new vscode.CompletionItem(stanzaSnippet);

                // Convert <foo> <bar> type things to placeholders
                // ${1:<foo>} ${2:<bar>}
                if(PLACEHOLDER_REGEX.test(stanzaSnippet)) {
                    let placeholders = stanzaSnippet.match(PLACEHOLDER_REGEX)
                    placeholders.forEach(function (placeholder, i) {
                        // vscode placeholder tab stops start at $1 since tab stop $0 is a special case
                        let placeholderTabStop = i + 1
                        let formattedPlaceholder = `\$\{${placeholderTabStop}:${placeholder}\}`
                        stanzaSnippet = stanzaSnippet.replace(placeholder, formattedPlaceholder)
                    })
                }
                stanzaCompletionItem.insertText = new vscode.SnippetString(stanzaSnippet);
                stanzaCompletionItem.documentation = new vscode.MarkdownString(stanza.docString);
                stanzaCompletionItem.kind = vscode.CompletionItemKind.Class;
                completions.push(stanzaCompletionItem)
            });

            return completions
        }

    }, '[' );

}

function provideSettingCompletionItems(specConfig, trimWhitespace) {

    // Get the currently open document
    let currentDocument = path.basename(vscode.window.activeTextEditor.document.uri.fsPath)
    vscode.languages.registerCompletionItemProvider({ language: 'splunk', pattern: `**/${currentDocument}`}, {

        provideCompletionItems(document, position, token, context) {
            if((position.character > 1) || (!specConfig)) {
                // No completion for you!
                return
            }

            let completions = []
            let parentStanza = getParentStanza(document, position.line)

            if(parentStanza) {
                // Get settings for the current stanza
                let stanzaSettings = splunkSpec.getStanzaSettings(specConfig, parentStanza)
            
                // Create completion items for settings
                stanzaSettings.forEach(setting => {
                    
                    // a.k.a. the Sanford setting
                    let settingSnippet = trimWhitespace ? `${setting.name}=${setting.value}` : `${setting.name} = ${setting.value}`
                    let settingCompletionItem = new vscode.CompletionItem(settingSnippet);

                    // Convert <bool> to ${1|true,false|}
                    if(settingSnippet.indexOf("<boolean>")) {
                        settingSnippet = settingSnippet.replace("<boolean>", "${1|true,false|}")
                    }

                    // Convert <foo> <bar> type things to placeholders
                    // ${1:<foo>} ${2:<bar>}
                    if(PLACEHOLDER_REGEX.test(settingSnippet)) {
                        let placeholders = settingSnippet.match(PLACEHOLDER_REGEX)
                        placeholders.forEach(function (placeholder, i) {
                            // vscode placeholder tab stops start at 1 since tab stop $0 is a special case
                            let placeholderTabStop = i + 1
                            let formattedPlaceholder = `\$\{${placeholderTabStop}:${placeholder}\}`
                            settingSnippet = settingSnippet.replace(placeholder, formattedPlaceholder)
                        })
                    }

                    // Convert <enabled|disabled> to ${1|enabled,disabled|}
                    if(settingSnippet.indexOf("${2:<enabled|disabled>}")) {
                        settingSnippet = settingSnippet.replace("${2:<enabled|disabled>}", "${2|enabled,disabled|}")
                    }

                    // Convert [foo|bar|baz] or {foo|bar|baz} values to a dropdown placeholder
                    // ${1|foo,bar,baz|}
                    if(DROPDOWN_PLACEHOLDER_REGEX.test(settingSnippet)) {
                        settingSnippet = settingSnippet.replace(/\|/g, ',')
                        settingSnippet = settingSnippet.replace(/\[|{/, '${1|')
                        settingSnippet = settingSnippet.replace(/]|}/, '|}')
                    }

                    settingCompletionItem.insertText = new vscode.SnippetString(settingSnippet);
                    settingCompletionItem.documentation = new vscode.MarkdownString(setting.docString);
                    settingCompletionItem.kind = vscode.CompletionItemKind.Value;
                    completions.push(settingCompletionItem)
                });
            }

            // return all completion items as array
            return completions
        
        }
    });
}

function triggerDiagnostics(specConfig, document, diagnosticCollection) {
    if(timeout) {
        clearTimeout(timeout)
        timeout = undefined
    }
    timeout = setTimeout(updateDiagnostics, 2000, specConfig, document, diagnosticCollection)
}

function updateDiagnostics(specConfig, document, diagnosticCollection) {
    let diagnostics = getDiagnostics(specConfig, document);
    diagnosticCollection.set(document.uri, diagnostics);
}

function getDiagnostics(specConfig, document) {

    let diagnostics = []

    // Make sure stanzas are valid
    let docStanzas = getDocumentItems(document, STANZA_REGEX)
    docStanzas.forEach(stanza => {
        if(!splunkSpec.isStanzaValid(specConfig, stanza.text)) {
            let range = new vscode.Range(new vscode.Position(stanza.line, 0), new vscode.Position(stanza.line, stanza.text.length))
            let message = `Stanza ${stanza.text} does not seem to be a valid stanza.`
            let severity = vscode.DiagnosticSeverity.Error
            diagnostics.push(new vscode.Diagnostic(range, message, severity))
        }
    });

    // Make sure settings are valid
    let docSettings = getDocumentItems(document, SETTING_REGEX)
    docSettings.forEach(setting => {
        let parentStanza = getParentStanza(document, setting.line)
        if(!splunkSpec.isSettingValid(specConfig, parentStanza, setting.text)) {
            let range = new vscode.Range(new vscode.Position(setting.line, 0), new vscode.Position(setting.line, setting.text.length))
            let message = `Invalid key in stanza ${parentStanza} in ${path.basename(vscode.window.activeTextEditor.document.uri.fsPath)}, line ${setting.line + 1}: ${setting.text}.`
            let severity = vscode.DiagnosticSeverity.Error
            diagnostics.push(new vscode.Diagnostic(range, message, severity))
        }
    });

    return diagnostics;
}

function deactivate() { }
exports.deactivate = deactivate;