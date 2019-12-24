"use strict";
Object.defineProperty(exports, "__esModule", { value: true });

const vscode = require("vscode");
const path = require("path");
const fs = require("fs");
const splunkFoldingRangeProvider = require("./foldingRangeProvider.js");
const splunkSpec = require("./spec.js");
const PLACEHOLDER_REGEX = /\<([^\>]+)\>/g
const DROPDOWN_PLACEHOLDER_REGEX = /\[\w+(\|\w+)+]/g
const STANZA_REGEX = /^\[(?<stanza>[^\]].*?)\]/
const SETTING_REGEX = /^(?<setting>[\w\-_\<\>\.]+)\s*=\s*(?<value>[^\r\n]+)/
let specConfigs = {}
let specConfig = undefined
let modularSpecFiles = ["inputs.conf.spec", "alert_actions.conf.spec"];
var timeout = undefined

function getSpecConfig(context) {
    // Given a spec file path, return a configuration of stanzas, settings, and document strings

    // Get the custom configuration options
    let baseSpecFilePath = vscode.workspace.getConfiguration().get('splunk.specFilePath', vscode.window.activeTextEditor.document.uri)
    let specFileVersion  = vscode.workspace.getConfiguration().get('splunk.specFileVersion', vscode.window.activeTextEditor.document.uri)

    // Get the currently open document
    let currentDocument = path.basename(vscode.window.activeTextEditor.document.uri.fsPath)
    let specFileName = currentDocument + ".spec"

    if(specConfigs.hasOwnProperty(specFileName)) {
        // Returned cached config
        return specConfigs[specFileName]
    }

    // Create a path to the spec file for the current document
    if(!baseSpecFilePath) {
        baseSpecFilePath = context.extensionPath
    }
    let specFilePath = path.join(baseSpecFilePath, "spec_files", specFileVersion, specFileName)

    // Check if the file exists
    if(!fs.existsSync(specFilePath)) return null

    let specFileContent = fs.readFileSync(specFilePath, "utf-8");
    let specConfig = splunkSpec.parse(specFileContent, specFileName);

    // Modular .spec files allow freeform stanzas, but this is denoted in the static .spec file/
    // So, overrice the freeform setting on these.
    if(modularSpecFiles.includes(specFileName)) {
        specConfig["allowsFreeformStanzas"] = true;
    }

    // Register Stanza completion items for this spec
    context.subscriptions.push(provideStanzaCompletionItems(specConfig));

    // Register Setting completion items for this spec
    context.subscriptions.push(provideSettingCompletionItems(specConfig));

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

    // No parent stanza found.  This line is an orphan :(
    return null
}

function getDocumentItems(document, PATTERN) {
    // Given a pattern, return line numbers that match that pattern

    let items = []

    for (var i=0; i < document.lineCount; i++) {
        if(PATTERN.test(document.lineAt(i).text)) {
            let item = {}
            item["text"] = document.lineAt(i).text
            item["line"] = i
            items.push(item)
        }
    }

    return items
}

function activate(context) {

    // Get the spec config on start up
    specConfig = getSpecConfig(context);

    // Set up diagnostics
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
            // Use a timer on onDidChangeTextDocument so we are not checking as often.
            triggerDiagnostics(specConfig, editor.document, diagnosticCollection);
        }
    }))

    // Set up listener for active editor changing
    context.subscriptions.push(vscode.window.onDidChangeActiveTextEditor(editor => {
        if (vscode.window.activeTextEditor && editor.document === vscode.window.activeTextEditor.document) {
            specConfig = getSpecConfig(context);
            triggerDiagnostics(specConfig, editor.document, diagnosticCollection);
        }
    }));
}

function provideStanzaCompletionItems(specConfig) {

    // Get the currently open document
    let currentDocument = path.basename(vscode.window.activeTextEditor.document.uri.fsPath)

    let stanzaCompletions = vscode.languages.registerCompletionItemProvider({ language: 'splunk', pattern: `**/${currentDocument}`}, {

        provideCompletionItems(document, position, token, context) {

            if(!document.lineAt(position.line).text.startsWith('[')) {
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

function provideSettingCompletionItems(specConfig) {

    // Get the currently open document
    let currentDocument = path.basename(vscode.window.activeTextEditor.document.uri.fsPath)

    let settingCompletions = vscode.languages.registerCompletionItemProvider({ language: 'splunk', pattern: `**/${currentDocument}`}, {

        provideCompletionItems(document, position, token, context) {

            if(!specConfig) {
                // No completion for you!
                return
            }

            if(document.lineAt(position.line).text.startsWith('[')) {
                // We are typing a stanza, so return.
                return
            }

            let completions = []
            let parentStanza = getParentStanza(document, position.line)

            if(parentStanza) {
                // Get settings for the current stanza
                let stanzaSettings = splunkSpec.getStanzaSettings(specConfig, parentStanza)
            
                // Create completion items for settings
                stanzaSettings.forEach(setting => {
                    let settingSnippet = `${setting.name} = ${setting.value}`
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
    timeout = setTimeout(updateDiagnostics, 500, specConfig, document, diagnosticCollection)
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