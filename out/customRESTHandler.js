"use strict";
const fs = require("fs");
const path = require("path");
const vscode = require("vscode");

function createRESTHandler(handlerName, handlerDestination, context) {

    // copy from source to dest folder
    let handlerSource = path.join(context.extensionPath, "resources", "projects", "resthandler_template");
    let handlerDest = path.join(handlerDestination[0].fsPath, handlerName);

    if(fs.existsSync(handlerDest)) {
        vscode.window.showWarningMessage(`Path for REST handler already exists and will not be created. ${handlerDest}`)
        return
    }

    copyDirectoryRecursiveSync(handlerSource, handlerDest);

    let app_conf = path.join(handlerDestination[0].fsPath, handlerName, "default", "app.conf");

    try {

        // modify default/app.conf
        modifyFileContents(app_conf, /label\s+=\s+standin/, `label = ${handlerName}`);
        modifyFileContents(app_conf, /id\s+=\s+standin/, `label = ${handlerName}`);

    } catch (err) {
        vscode.window.showErrorMessage(err.message);
        return
    }

    vscode.window.showInformationMessage(`Successfully created custom REST handler ${handlerName}.`);
}
exports.createRESTHandler = createRESTHandler

function modifyFileContents(file, regexMatch, newValue) {
    try {
        let fileContent = fs.readFileSync(file, 'utf-8');
        let newfileContent = fileContent.replace(regexMatch, newValue);
        fs.writeFileSync(file, newfileContent, 'utf-8');
    } catch (err) {
        throw err
    }
}

function copyDirectoryRecursiveSync(source, target) {
    if (!fs.lstatSync(source).isDirectory()) return;
    
    fs.readdirSync(source).forEach( itemName => {
        let sourcePath = path.join(source, itemName);
        let targetPath = path.join(target, itemName);
    
        if (fs.lstatSync(sourcePath).isDirectory()) {
            fs.mkdirSync(targetPath, { recursive: true });
            copyDirectoryRecursiveSync(sourcePath, targetPath);
        }
        else {
            fs.copyFileSync(sourcePath, targetPath);
        }
    });
}