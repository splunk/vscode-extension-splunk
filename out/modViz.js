"use strict";
const fs = require("fs");
const path = require("path");
const vscode = require("vscode");
const cp = require("child_process");

function createModViz(vizName, vizDestination, context) {

    // copy from source to dest folder
    let modVizSource = path.join(context.extensionPath, "resources", "projects", "modViz");
    let modVizDest = path.join(vizDestination[0].path, vizName);

    if(fs.existsSync(modVizDest)) {
        vscode.window.showWarningMessage(`Path for visualization already exists and will not be created. ${modVizDest}`)
        return
    }

    copyDirectoryRecursiveSync(modVizSource, modVizDest);

    // rename appserver/static/visualizations/(standin) directory to the new viz name
    try {
        fs.renameSync(
            path.join(vizDestination[0].path, vizName, "appserver", "static", "visualizations", "standin"),
            path.join(vizDestination[0].path, vizName, "appserver", "static", "visualizations", vizName)
        );
    } catch (err) {
        vscode.window.showErrorMessage(err.message);
        return
    }

    let package_json = path.join(vizDestination[0].path, vizName, "appserver", "static", "visualizations", vizName, "package.json");
    let visualizations_conf = path.join(vizDestination[0].path, vizName, "default", "visualizations.conf");
    let default_meta = path.join(vizDestination[0].path, vizName, "metadata", "default.meta");
    let app_conf = path.join(vizDestination[0].path, vizName, "default", "app.conf");

    try {
        // modify package.json "name": "standin"
        modifyFileContents(package_json, /"name": "standin"/, `"name": "${vizName}"`);

        // modify visualizations.conf [standin]
        modifyFileContents(visualizations_conf, /\[standin\]/, `[${vizName}]`);

        // modify default.meta  [visualizations/standin], export = system
        modifyFileContents(default_meta, 
            /# Un-comment the stanza below to make the standin visualization available to all apps.\n#\s+\[visualizations\/standin\]\n#\s+export\s+=\s+system/, 
            `# Un-comment the stanza below to make the ${vizName} visualization available to all apps.
[visualizations/${vizName}]
export = system`
            );

        // modify default/app.conf
        modifyFileContents(app_conf, /label\s+=\s+standin/, `label = ${vizName}`);

        // run npm install
        cp.exec('npm install', {
            cwd: path.join(vizDestination[0].path, vizName, "appserver", "static", "visualizations", vizName)
        });

    } catch (err) {
        vscode.window.showErrorMessage(err.message);
        return
    }

    vscode.window.showInformationMessage(`Successfully created visualization ${vizName}.`);
}
exports.createModViz = createModViz

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