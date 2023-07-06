"use strict";
Object.defineProperty(exports, "__esModule", { value: true });

const vscode = require("vscode");
const path = require("path");
const fs = require("fs");
const splunkSearchProvider = require("./searchProvider.js");
const splunkEmbeddedReportProvider = require("./embeddedReportProvider");
const splunkFoldingRangeProvider = require("./foldingRangeProvider.js");
const splunkModViz = require('./modViz.js');
const splunkCustomCommand = require('./customCommand.js');
const globalConfigPreview = require('./globalConfigPreview')
const splunkCustomRESTHandler = require('./customRESTHandler.js')
const splunkSpec = require("./spec.js");
const reload = require("./commands/reload.js");

const { SplunkNotebookSerializer } = require('./notebooks/serializers');
const { SplunkController } = require('./notebooks/controller');
const { Spl2NotebookSerializer } = require('./notebooks/spl2/serializer');
const { Spl2Controller } = require('./notebooks/spl2/controller');
const { installMissingSpl2Requirements, getLatestSpl2Release } = require('./notebooks/spl2/installer');
const { startSpl2ClientAndServer } = require('./notebooks/spl2/initializer');
const notebookCommands = require('./notebooks/commands');
const { CellResultCountStatusBarProvider } = require('./notebooks/provider');

//const { transpileModule } = require("typescript");
//const { AsyncLocalStorage } = require("async_hooks");
const PLACEHOLDER_REGEX = /\<([^\>]+)\>/g
let specConfigs = {};
let timeout;
let diagnosticCollection;
let specConfig;
let snippets = {};
let spl2Client;
let spl2PortToAttempt = 59143; // 59143 ~ SPLNK if you squint really hard :)

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
            if(i>0 && PATTERN == splunkSpec.SETTING_REGEX && document.lineAt(i-1) && document.lineAt(i-1).text.trim().endsWith("\\")) {
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

async function activate(context) {

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

    // Set up Splunk search viewer
    const savedSearchProvider = new splunkSearchProvider.SavedSearchProvider();
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
    const searchProvider = new splunkSearchProvider.SearchProvider();
    context.subscriptions.push(vscode.commands.registerCommand('splunk.search.adhoc', async () => {
        let search = await vscode.window.showInputBox({
            prompt:'Search SPL'
        })
        if (search) {
            let searchResult = await searchProvider.runSearch(search);
            splunkOutputChannel.appendLine(searchResult);
            splunkOutputChannel.show();
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

    // Setup progress bar for install
    const progressBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    context.subscriptions.push(progressBar);
    progressBar.hide();

    // Register Utility Commands
    context.subscriptions.push(vscode.commands.registerCommand('splunk.fullDebugRefresh', async () => {reload.fullDebugRefresh(splunkOutputChannel)}))

    // Set up stanza folding
    context.subscriptions.push(vscode.languages.registerFoldingRangeProvider([
        { language: 'splunk', pattern: '**/*.{conf,conf.spec}' }
    ], new splunkFoldingRangeProvider.confFoldingRangeProvider()));

    // If vscode was opened with an active Splunk file, handle it.
    vscode.commands.registerCommand('splunk.restartSpl2LanguageServer', async () => {
        try {
            if (spl2Client) {
                await spl2Client.deactivate();
            }
            spl2Client = undefined;
            await handleSpl2Document(context, progressBar);
        } catch (err) {
            console.warn(`Error restarting SPL2 language server, err: ${err}`);
        }
    });
    if(vscode.window.activeTextEditor) {
        if (isSplunkDocument(vscode.window.activeTextEditor.document)) {
            handleSplunkDocument(context);
        } else if (isSpl2Document(vscode.window.activeTextEditor.document)) {
            await handleSpl2Document(context, progressBar);
        }
    }

    // Set up listener for text document changes
    context.subscriptions.push(vscode.workspace.onDidChangeTextDocument(editor => {
        if(vscode.window.activeTextEditor && vscode.window.activeTextEditor.document.languageId === 'splunk') {
            // Use a timer on onDidChangeTextDocument so we are not linting as often.
            triggerDiagnostics(specConfig, editor.document, diagnosticCollection);
        }
    }));

    // Set up listener for active editor changing
    context.subscriptions.push(vscode.window.onDidChangeActiveTextEditor( async () => {
        if (!vscode.window.activeTextEditor) {
            return;
        }
        if (isSplunkDocument(vscode.window.activeTextEditor.document)) {
            handleSplunkDocument(context);
        } else if (isSpl2Document(vscode.window.activeTextEditor.document)) {
            await handleSpl2Document(context, progressBar);
        }
    }));

    // Notebook
    context.subscriptions.push(vscode.workspace.registerNotebookSerializer('splunk-notebook', new SplunkNotebookSerializer(), {transientCellMetadata: {inputCollapsed: true, outputCollapsed: true}, transientOutputs: false}));
	context.subscriptions.push(vscode.workspace.registerNotebookSerializer('spl2-notebook', new Spl2NotebookSerializer(), {transientCellMetadata: {inputCollapsed: true, outputCollapsed: true}, transientOutputs: false}));
    const controller = new SplunkController();
    context.subscriptions.push(controller);
    const spl2Controller = new Spl2Controller();
    context.subscriptions.push(spl2Controller);
    context.subscriptions.push(vscode.notebooks.registerNotebookCellStatusBarItemProvider('splunk-notebook', new CellResultCountStatusBarProvider(splunkOutputChannel)));
    context.subscriptions.push(vscode.notebooks.registerNotebookCellStatusBarItemProvider('spl2-notebook', new CellResultCountStatusBarProvider(splunkOutputChannel)));
    notebookCommands.registerNotebookCommands([controller, spl2Controller], splunkOutputChannel, context);
}
exports.activate = activate;

function isSplunkDocument(document) {
    let splunkFileExtensions = [".conf", "default.meta", "local.meta", "globalconfig.json"];
    for (let i=0; i < splunkFileExtensions.length; i++) {
        if(document.fileName.toLowerCase().endsWith(splunkFileExtensions[i])) {
            return true;
        }
    }
    return false;
}

function handleSplunkDocument(context) {

    if(diagnosticCollection === undefined) {
        diagnosticCollection = vscode.languages.createDiagnosticCollection('splunk');
    }

    let currentDocument = path.basename(vscode.window.activeTextEditor.document.uri.fsPath);

    // Any snippets for this file?
    let snippetFilePath = path.join(context.extensionPath, "snippets", currentDocument);
    if(fs.existsSync(snippetFilePath) && !snippets.hasOwnProperty(currentDocument)) {
        context.subscriptions.push(provideSnippetCompletionItems(snippetFilePath));
        // Cache snippets for this file so we do not regenerate them.
        snippets[currentDocument] = snippetFilePath;
    }

    // If this file is globalConfig.json, return as there is not a spec file for it.
    if(currentDocument.toLowerCase() == "globalconfig.json") { 
        return; 
    }
    let specFilePath = getSpecFilePath(context.extensionPath, currentDocument);

    if(specConfigs.hasOwnProperty(currentDocument)) {
        specConfig = specConfigs[currentDocument];
    } else {
        specConfig = splunkSpec.getSpecConfig(context.extensionPath, specFilePath);

        // Register Stanza completion items for this spec
        context.subscriptions.push(provideStanzaCompletionItems(specConfig));

        // Register Setting completion items for this spec
        let trimWhitespace = vscode.workspace.getConfiguration().get('splunk.spec.trimEqualSignWhitespace')
        context.subscriptions.push(provideSettingCompletionItems(specConfig, trimWhitespace));
    }

    // Set up diagnostics (linting)
    updateDiagnostics(specConfig, vscode.window.activeTextEditor.document, diagnosticCollection);

    // Cache specConfig
    specConfigs[currentDocument] = specConfig
}

function isSpl2Document(document) {
    return document.languageId == 'splunk_spl2';
}

async function handleSpl2Document(context, progressBar) {
    if (spl2Client) {
        // Client and server are already running, try refreshing for case of new document
        const range = new vscode.Range(new vscode.Position(0, 0), new vscode.Position(0, 1));
        const text = vscode.window.activeTextEditor.document.getText(range) || " ";
        vscode.window.activeTextEditor.edit((editBuilder) => {
            // To refresh language server make a harmless edit by replacing the first character
            editBuilder.replace(range, text);
        });
        return;
    }
    try {
        const installedLatestLsp = await installMissingSpl2Requirements(context, progressBar);
        if (!installedLatestLsp) {
            await getLatestSpl2Release(context, progressBar);
        }
        const onSpl2Restart = async (nextPort) => {
            await spl2Client.deactivate();
            spl2PortToAttempt = nextPort;
            spl2Client = await startSpl2ClientAndServer(context, progressBar, spl2PortToAttempt, onSpl2Restart);
        };
        spl2Client = await startSpl2ClientAndServer(context, progressBar, spl2PortToAttempt, onSpl2Restart);
    } catch (err) {
        vscode.window.showErrorMessage(`Issue setting up SPL2 environment: ${err}`);
    }
}

function getSpecFilePath(basePath, filename) {

    // Get the custom configuration options
    let settingsSpecFilePath = vscode.workspace.getConfiguration('splunk').get('spec.FilePath');
    let settingsSpecFileVersion  = vscode.workspace.getConfiguration('splunk').get('spec.FileVersion');
    let specFileName = filename + ".spec";

    // Special case spec files
    let specialSpecFiles = ["eventgen.conf.spec", "default.meta.spec", "local.meta.spec"]
    if(specialSpecFiles.indexOf(specFileName) > -1) {
        if (specFileName == "local.meta.spec") { specFileName = "default.meta.spec" }
        return checkSpecFilePath(path.join(basePath, "spec_files", specFileName))
    }

    // Create a path to the spec file for the current document
    if(!settingsSpecFilePath) {
        // No path was configured in settings, so create a path to the built-in spec files
        return checkSpecFilePath(path.join(basePath, "spec_files", settingsSpecFileVersion, specFileName))
    } else {
        return checkSpecFilePath(path.join(settingsSpecFilePath, specFileName))
    }
}

function checkSpecFilePath(specFilePath) {
    if(!fs.existsSync(specFilePath)) {
        vscode.window.showErrorMessage(`Spec file path not found: ${specFilePath}`)
        return null
    }
    return specFilePath;
}

function provideStanzaCompletionItems(specConfig) {

    // Get the currently open document
    let currentDocument = path.basename(vscode.window.activeTextEditor.document.uri.fsPath);

    vscode.languages.registerCompletionItemProvider({ language: 'splunk', pattern: `**/${currentDocument}`}, {

        provideCompletionItems(document, position) {

            if((position.character != 1) || (!document.lineAt(position.line).text.startsWith('['))) {
                // We are not typing a stanza, so return.
                return
            }
        
            if(!specConfig) {
                // No completion for you!
                return
            }

            let completions = [];

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
                completions.push(stanzaCompletionItem);
            });

            return completions
        }

    }, '[' );

}

function provideSettingCompletionItems(specConfig, trimWhitespace) {

    // Get the currently open document
    let currentDocument = path.basename(vscode.window.activeTextEditor.document.uri.fsPath);
    vscode.languages.registerCompletionItemProvider({ language: 'splunk', pattern: `**/${currentDocument}`}, {

        provideCompletionItems(document, position) {
            if((position.character > 1) || (!specConfig)) {
                // No completion for you!
                return
            }

            let completions = [];
            let parentStanza = getParentStanza(document, position.line);

            if(parentStanza) {
                // Get settings for the current stanza
                let stanzaSettings = splunkSpec.getStanzaSettings(specConfig, parentStanza)
            
                // Create completion items for settings
                stanzaSettings.forEach(setting => {
                    
                    // a.k.a. the Sanford setting
                    let settingSnippet = trimWhitespace ? `${setting.name}=${setting.value}` : `${setting.name} = ${setting.value}`
                    let settingCompletionItem = new vscode.CompletionItem(settingSnippet);

                    // Convert <boolean> to ${1|true,false|}
                    if(settingSnippet.indexOf("<boolean>") > -1) {
                        settingSnippet = settingSnippet.replace("<boolean>", "${1|true,false|}")
                    }

                    // Convert 'true | false' to ${1|true,false|}
                    if(settingSnippet.indexOf("true | false") > -1) {
                        settingSnippet = settingSnippet.replace("true | false", "${1|true,false|}")
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
                    if(settingSnippet.indexOf("${1:<enabled|disabled>}") > -1) {
                        settingSnippet = settingSnippet.replace("${1:<enabled|disabled>}", "${1|enabled,disabled|}")
                    }
                    if(settingSnippet.indexOf("${2:<enabled|disabled>}") > -1) {
                        settingSnippet = settingSnippet.replace("${2:<enabled|disabled>}", "${2|enabled,disabled|}")
                    }

                    // Convert [foo|bar|baz] or {foo|bar|baz} values to a dropdown placeholder
                    // ${1|foo,bar,baz|}
                    if(splunkSpec.DROPDOWN_PLACEHOLDER_REGEX.test(settingSnippet)) {
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
            return completions;
        }
    });
}

function provideSnippetCompletionItems(snippetPath) {

    // Get the currently open document
    let currentDocument = path.basename(vscode.window.activeTextEditor.document.uri.fsPath);
    vscode.languages.registerCompletionItemProvider({ pattern: `**/${currentDocument}`}, {

        provideCompletionItems() {

            let completions = [];
            let snippets = JSON.parse(fs.readFileSync(snippetPath));
            for (let i in snippets) {
                let snippet = snippets[i];
                let snippetCompletionItem = new vscode.CompletionItem(snippet.prefix);
                let snippetString = snippet.body.join("\n");
                snippetCompletionItem.insertText = new vscode.SnippetString(snippetString);
                snippetCompletionItem.documentation = new vscode.MarkdownString(snippet.description);
                snippetCompletionItem.kind = vscode.CompletionItemKind.Snippet;
                completions.push(snippetCompletionItem);
            }
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
    let docStanzas = getDocumentItems(document, splunkSpec.STANZA_REGEX)
    docStanzas.forEach(stanza => {
        if(!splunkSpec.isStanzaValid(specConfig, stanza.text)) {
            let range = new vscode.Range(new vscode.Position(stanza.line, 0), new vscode.Position(stanza.line, stanza.text.length))
            let message = `Stanza ${stanza.text} does not seem to be a valid stanza.`
            let severity = vscode.DiagnosticSeverity.Error
            diagnostics.push(new vscode.Diagnostic(range, message, severity))
        }
    });

    // Make sure settings are valid
    let docSettings = getDocumentItems(document, splunkSpec.SETTING_REGEX)
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

async function deactivate() {
    if (spl2Client) {
        return await spl2Client.deactivate();
    }
}

exports.deactivate = deactivate;