"use strict";
const fs = require("fs");
const path = require("path");
const vscode = require("vscode");

function createCommand(commandName, commandDestination, context) {

    // copy from source to dest folder
    let commandSource = path.join(context.extensionPath, "resources", "projects", "searchcommands_template");
    let commandDest = path.join(commandDestination[0].fsPath, commandName);

    if(fs.existsSync(commandDest)) {
        vscode.window.showWarningMessage(`Path for command already exists and will not be created. ${commandDest}`)
        return
    }

    copyDirectoryRecursiveSync(commandSource, commandDest);

    let app_conf = path.join(commandDestination[0].fsPath, commandName, "default", "app.conf");

    try {

        // modify default/app.conf
        modifyFileContents(app_conf, /label\s+=\s+standin/, `label = ${commandName}`);
        modifyFileContents(app_conf, /id\s+=\s+standin/, `label = ${commandName}`);

    } catch (err) {
        vscode.window.showErrorMessage(err.message);
        return
    }

    vscode.window.showInformationMessage(`Successfully created custom command ${commandName}.`);
}
exports.createCommand = createCommand

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