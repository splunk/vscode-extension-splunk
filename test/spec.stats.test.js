const fs = require('fs');
const path = require('path');
const specFolderLocation = './spec_files';
const splunkSpec = require("../out/spec.js");
const extensionPath = path.resolve(__dirname, '../');
const specFileVersion = "9.2";

let stanzaCount = 0
let settingCount = 0

fs.readdir(path.join(specFolderLocation, specFileVersion), function(err, files) {
    let list = files.filter(item => !(/(^|\/)\.[^\/\.]/g).test(item))
    console.log('.spec file count: %d', list.length)
    list.forEach(function (file) {
        let specFilePath = path.join(specFolderLocation, specFileVersion, file)
	    let specConfig = splunkSpec.getSpecConfig(extensionPath, specFilePath);
        stanzaCount = stanzaCount + specConfig.stanzas.length
        specConfig.stanzas.forEach(function (stanza) {
            settingCount = settingCount + stanza.settings.length
        })
    })

    console.log('stanza count: %d', stanzaCount)
    console.log('setting count: %d', settingCount)
})