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
const splunkCustomCommand = require('./customCommand.js')
const splunkCustomRESTHandler = require('./customRESTHandler.js')
const splunkSpec = require("./spec.js");
const PLACEHOLDER_REGEX = /\<([^\>]+)\>/g
const DROPDOWN_PLACEHOLDER_REGEX = /\[\w+(\|\w+)+]/g
const STANZA_REGEX = /^\[(?<stanza>[^\]].*?)\]/
const SETTING_REGEX = /^(?<setting>[\w\-_\<\>\.]+)\s*=\s*(?<value>[^\r\n]+)/
let specConfigs = {}
let specConfig = undefined
let modularSpecFiles = ["inputs.conf.spec", "alert_actions.conf.spec", "indexes.conf.spec"];
var timeout = undefined

function getSpecConfig(context) {
    // Given a spec file path, return a configuration of stanzas, settings, and document strings

    // Get the custom configuration options
    let specFilePath = vscode.workspace.getConfiguration().get('splunk.spec.FilePath', vscode.window.activeTextEditor.document.uri)
    let specFileVersion  = vscode.workspace.getConfiguration().get('splunk.spec.FileVersion', vscode.window.activeTextEditor.document.uri)

    // Get the currently open document
    let currentDocument = path.basename(vscode.window.activeTextEditor.document.uri.fsPath)
    let specFileName = currentDocument + ".spec"

    if(specConfigs.hasOwnProperty(specFileName)) {
        // Returned cached config
        return specConfigs[specFileName]
    }

    // Create a path to the spec file for the current document
    if(!specFilePath) {
        // No path was configured in settings, so create a path to the built-in spec files
        let baseSpecFilePath = context.extensionPath
        specFilePath = path.join(baseSpecFilePath, "spec_files", specFileVersion, specFileName)
    } else {
        specFilePath = path.join(specFilePath, specFileName)
    }

    // Check if the file exists
    if(!fs.existsSync(specFilePath)) {
        vscode.window.showErrorMessage(`Spec file path not found: ${specFilePath}`)
        return null
    }

    let specFileContent = fs.readFileSync(specFilePath, "utf-8");
    let specConfig = splunkSpec.parse(specFileContent, specFileName);

    // Modular .spec files allow freeform stanzas, but this is not denoted in the static .spec file.
    // So, override the freeform setting on these.
    if(modularSpecFiles.includes(specFileName)) {
        specConfig["allowsFreeformStanzas"] = true;
    }

    // Register Stanza completion items for this spec
    context.subscriptions.push(provideStanzaCompletionItems(specConfig));

    // Register Setting completion items for this spec
    let trimWhitespace = vscode.workspace.getConfiguration().get('splunk.spec.trimEqualSignWhitespace')
    context.subscriptions.push(provideSettingCompletionItems(specConfig, trimWhitespace));

    // Cache specConfig before returning
    specConfigs[specFileName] = specConfig
    
    return specConfig
}

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

    let splunkOutputChannel = vscode.window.createOutputChannel("Splunk")
    
    const embeddedReportProvider = new splunkEmbeddedReportProvider.SplunkReportProvider();
    vscode.window.registerTreeDataProvider('embeddedReports', embeddedReportProvider);
    vscode.commands.registerCommand('splunk.embeddedReport.refresh', () => embeddedReportProvider.refresh());
    const viewRefreshInterval = vscode.workspace.getConfiguration().get('splunk.reports.viewRefreshInterval') * 1000;
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

    context.subscriptions.push(vscode.commands.registerCommand('splunk.search.adhoc', async () => {
        let splunkUrl = vscode.workspace.getConfiguration().get('splunk.commands.slkunkRestUrl')
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

    // Editing a .conf file?
    let currentDocument = path.basename(vscode.window.activeTextEditor.document.uri.fsPath)
    if(currentDocument.endsWith(".conf")) {
        specConfig = getSpecConfig(context);

        // Set up diagnostics (linting)
        let diagnosticCollection = vscode.languages.createDiagnosticCollection('splunk');
        if (vscode.window.activeTextEditor) {
            updateDiagnostics(specConfig, vscode.window.activeTextEditor.document, diagnosticCollection);
        }

         // Set up stanza folding
        context.subscriptions.push(vscode.languages.registerFoldingRangeProvider([
            { language: 'splunk', pattern: '**/*.{conf,conf.spec}' }
        ], new splunkFoldingRangeProvider.confFoldingRangeProvider()));

        // Set up listener for text document changes
        context.subscriptions.push(vscode.workspace.onDidChangeTextDocument(editor => {
            if(vscode.window.activeTextEditor && editor.document === vscode.window.activeTextEditor.document) {
                // Use a timer on onDidChangeTextDocument so we are not linting as often.
                triggerDiagnostics(specConfig, editor.document, diagnosticCollection);
            }
        }));

        // Set up listener for active editor changing
        context.subscriptions.push(vscode.window.onDidChangeActiveTextEditor(editor => {
            if (vscode.window.activeTextEditor && editor.document === vscode.window.activeTextEditor.document) {
                if(editor.document.fileName.endsWith(".conf")) {
                    specConfig = getSpecConfig(context);
                    diagnosticCollection.clear();
                    triggerDiagnostics(specConfig, editor.document, diagnosticCollection);
                }
            }
        }));

    }

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

                    // Convert [foo|bar|baz] values to a dropdown placeholder
                    // ${1|foo,bar,baz|}
                    if(DROPDOWN_PLACEHOLDER_REGEX.test(settingSnippet)) {
                        // Look to see if there are existing placeholders
                        // If so, increment
                        // Example: <integer>[KB|MB|GB]
                        //    This would translate to ${1:<integer>} first
                        //    So, we need to start with tabstop 2 for the [KB|MB|GB] stuff
                        //    Do a regex match for ${n: (extracting n)
                        //    Cast that to a number
                        //    Start from there and to 
                        settingSnippet = settingSnippet.replace(/\|/g, ',')
                        settingSnippet = settingSnippet.replace('[', '${1|')
                        settingSnippet = settingSnippet.replace(']', '|}')
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

    if (!(document && path.basename(document.uri.fsPath).endsWith('.conf'))) {
        diagnosticCollection.clear();
        return
    }

    let diagnostics = []

    // Make sure stanzas are valid
    let docStanzas = getDocumentItems(document, STANZA_REGEX)
    docStanzas.forEach(stanza => {
        if(!splunkSpec.isStanzaValid(specConfig, stanza.text)) {
            let diagnostic = new vscode.Diagnostic()
            diagnostic.range = new vscode.Range(new vscode.Position(stanza.line, 0), new vscode.Position(stanza.line, stanza.text.length))
            diagnostic.message = `Stanza ${stanza.text} does not seem to be a valid stanza.`
            diagnostic.severity = vscode.DiagnosticSeverity.Error
            diagnostics.push(diagnostic)
        }
    });

    // Make sure settings are valid
    let docSettings = getDocumentItems(document, SETTING_REGEX)
    docSettings.forEach(setting => {
        let parentStanza = getParentStanza(document, setting.line)
        if(!splunkSpec.isSettingValid(specConfig, parentStanza, setting.text)) {
            let diagnostic = new vscode.Diagnostic()
            diagnostic.range = new vscode.Range(new vscode.Position(setting.line, 0), new vscode.Position(setting.line, setting.text.length))
            // Invalid key in stanza [my:stanza] in /Applications/Splunk/etc/apps/TA-test/local/app.conf, line 26: this  (value:  that).
            diagnostic.message = `Invalid key in stanza ${parentStanza} in ${path.basename(vscode.window.activeTextEditor.document.uri.fsPath)}, line ${setting.line + 1}: ${setting.text}.`
            diagnostic.severity = vscode.DiagnosticSeverity.Error
            diagnostics.push(diagnostic)
        }
    });


    diagnosticCollection.set(document.uri, diagnostics);
}

exports.activate = activate;

function deactivate() { }
exports.deactivate = deactivate;

//# sourceMappingURL=extension.js.map