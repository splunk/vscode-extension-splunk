"use strict";
Object.defineProperty(exports, "__esModule", { value: true });

const vscode = require("vscode");
const path = require("path");
//const splunkDocumentSymbolProvider = require("./docSymbolProvider.js");
const splunkFoldingRangeProvider = require("./foldingRangeProvider.js")


function getConfFileStanzas() {
    // Reads the conf file spec and creates a collection of stanza objects
    // Stanza object example:
    /*
        {
            stanzaName: string,
            docString: string,
            parameters: [
                {
                    parameterName: string
                    valueType: string
                    docString: string
                }
            ]
        }
    */
}

function activate(context) {

    let activeEditor = vscode.window.activeTextEditor;

    // Note: this will extract the setting name
    // line.match(/^(?<setting>[\w\-_\<\>]+\s*)=\s*(?<value>[^\r\n]+)/).groups['setting']

    // For linting, read each line.
    // Find settings - settings will be lines that:
    //    - do not start with a comment (#)
    //    - are not stanzas [my_stanza]
    //    - are not blank lines
    //    - name = value - this regex -> ^\s*(?<setting>[\w\-_\<\>]+)\s*=\s*(?<value>[^\r\n]+)
    //    - text on a line by itself is invalid

    // Completition Items
    // 1 - get global parameters for the current file - read from the .spec file
    //     - these parameters can be in any stanza

    
    let provider1 = vscode.languages.registerCompletionItemProvider('splunk', {

        provideCompletionItems(document, position, token, context) {

            // a completion item that inserts its text as snippet,
            // the `insertText`-property is a `SnippetString` which will be
            // honored by the editor.
            const snippetCompletion = new vscode.CompletionItem('Good part of the day');
            snippetCompletion.insertText = new vscode.SnippetString('Good ${1|morning,afternoon,evening|}. It is ${1}, right?');
            snippetCompletion.documentation = new vscode.MarkdownString("Inserts a snippet that lets you select the _appropriate_ part of the day for your greeting.");

            // a completion item that can be accepted by a commit character,
            // the `commitCharacters`-property is set which means that the completion will
            // be inserted and then the character will be typed.
            const commitCharacterCompletion = new vscode.CompletionItem('console');
            commitCharacterCompletion.commitCharacters = ['.'];
            commitCharacterCompletion.documentation = new vscode.MarkdownString('Press `.` to get `console.`');

            // return all completion items as array
            return [
                snippetCompletion,
                commitCharacterCompletion
            ];
        }
    });


    context.subscriptions.push(provider1);

    context.subscriptions.push(vscode.languages.registerFoldingRangeProvider([
        { language: 'splunk', pattern: '**/*.{conf,conf.spec}' }
    ], new splunkFoldingRangeProvider.confFoldingRangeProvider()));

}

exports.activate = activate;

// this method is called when your extension is deactivated
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map