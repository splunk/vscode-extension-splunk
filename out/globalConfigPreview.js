const vscode = require("vscode");
const fs = require("fs")
const path = require("path")

function init(context) {
    vscode.commands.registerCommand('splunk.previewGlobalConfig', () => previewHanlder(path.join(context.extensionPath, 'resources', 'templates', 'globalConfig.html')))
}

function previewHanlder(templatePath) {
    const activeFile = vscode.window.activeTextEditor
    const configText = activeFile.document.getText()
    try {
        const configObject = JSON.parse(configText)
        const panel = vscode.window.createWebviewPanel(
            'splunkWebView',
            'Global Config Preview',
            vscode.ViewColumn.Beside,
            {
                enableScripts: true,
            }
        );
        const updateView = () => {
            const template = fs.readFileSync(templatePath, {
                encoding: "utf-8"
            });
            panel.webview.html = template
        }
        updateView();
        panel.webview.postMessage({ action: 'config-data', data: configObject })
    } catch (e) {
        console.error("Error Rendering preview. ", e.message)
    }
}

exports.init = init;
