const vscode = require("vscode");
const fs = require("fs")
const path = require("path")

function init(context) {
    vscode.commands.registerCommand('splunk.previewGlobalConfig', () => previewHanlder(path.join(context.extensionPath, 'resources', 'templates', 'globalConfig.html')))
}

function render(text, panel) {
    try {
        const configObject = JSON.parse(text)
        panel.webview.postMessage({ action: 'config-data', data: configObject })
    } catch (e) {
        console.error("Error Rendering preview. ", e.message)
    }
}

function previewHanlder(templatePath) {
    const panel = vscode.window.createWebviewPanel(
        'splunkWebView',
        'Global Config Preview',
        vscode.ViewColumn.Beside,
        {
            enableScripts: true,
        }
    );
    const template = fs.readFileSync(templatePath, {
        encoding: "utf-8"
    });
    panel.webview.html = template
    const configText = vscode.window.activeTextEditor.document.getText()
    render(configText, panel);
    vscode.workspace.onDidChangeTextDocument((e) => {
        const doc = e.document
        if (doc.fileName.endsWith("globalConfig.json")) {
            render(doc.getText(), panel)
        }
    })
}

exports.init = init;
