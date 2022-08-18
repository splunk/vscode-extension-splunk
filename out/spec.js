"use strict";
const path = require("path");
const fs = require("fs");
const PREAMBLE_REGEX = /^.*?((GLOBAL\sSETTINGS)|(Global\sstanza[^\[]*))/s
// Start the match at the beginning of the string ^
// Lazily match anything .*?
// Match GLOBAL SETTINGS literally 
// OR match Global stanza until a [ is encountered (refer to serverclass.conf.spec for an example of this case)
// Enable multiline /s

const SECTION_REGEX = /^.*?(?=\n\[|$)/s
// Start the match at the beginning of the string ^
// Lazily match anything .*?
// Positive lookahead to match until a newline followed by a [ or the end of the string $
// Enable multiline /s

const COMMENT_REGEX = /^#/
const BLANK_LINE_REGEX = /^\s*\n/gm
const DEFAULT_STANZA_REGEX = /^# Use the \[(default)\] stanza/
const STANZA_REGEX = /^\[(?<stanza>|[^\]].*?)\]/
const STANZA_PREFIX_REGEX = /^\[(?<prefix>[^\]].*?(=|:|::|::...|_|\/))[\<|\w|\/]/   // matches things like [author=<name>], [tcp:<port>], [tcp:123], [source::...a...], [tcp://<remote server>:<port>], [tcp://123], [views/<view_name>]
const STANZA_FREEFORM_REGEX = /^\[\<(?<stanza>.*?)\>\]/           // matches things like [<spec>] or [<custom_alert_action>]
const STANZA_ABSOLUTE_REGEX = /^\[(?<stanza>|[^\<\>\:\/]+)\]/      // matches things like [tcp] or [SSL] (does not allow <, >, :, or /)
//const SETTING_REGEX = /^(?<setting>\w.*?)\s*=\s*(?<value>[^\r\n]+)/
const SETTING_REGEX = /^(?<setting>((\w)|\<name\>|\<tag\d\>|\<.+\>).*?)\s*=\s*(?<value>[^\r\n]+)/
const SETTING_PREFIX_REGEX = /^(?<prefix>[^-\.].*?)\<.*?\>/
const SETTING_FREEFORM_REGEX = /^\<(?<setting>.*?)\>/
const modularSpecFiles = ["inputs.conf.spec", "alert_actions.conf.spec", "indexes.conf.spec", "searchbnf.conf.spec"];
const DROPDOWN_PLACEHOLDER_REGEX = /(\[|{)\w+(\|\w+)+(]|})/g

const lineTypes = {
    DEFAULT_STANZA: 'defaultStanza',
    STANZA: 'stanza',
    SETTING: 'setting',
    DOC_STRING: 'docString',
    COMMENT: 'comment',
    UNKNOWN: 'unknown'
}
const stanzaTypes = {
    ABSOLUTE: 'absolute',
    PREFIX: 'prefix',
    FREEFORM: 'freeform',
    UNKNOWN: 'unknown'
}

/**
 * Given a spec file path, return a configuration of stanzas, settings, and document strings
 * @param  {String} specFilePath    The path to the spec file
 * @return {Object}                 An object representing the spec file stanzas, settings, and documentation
                                    {
                                        specName: string,
                                        allowsFreeformStanzas: [true,false],
                                        stanzas: []
                                    }
 */
 function getSpecConfig(specFilePath) {

    let specFileName = path.parse(specFilePath).base;

    let specFileContent = fs.readFileSync(specFilePath, "utf-8");
    let specConfig = parseSpecConfig(specFileContent, specFileName);

    // Special case for inputs.conf.spec
    if(specConfig["specName"] == "inputs.conf.spec") {

        // The inputs.conf.spec file shipped from Splunk does not include the disabled setting (even though that is a valid setting).
        // See https://github.com/splunk/vscode-extension-splunk/issues/18
        // Until this is fixed in the inputs.conf.spec file, we will add it here.
        for (var i=0; i < specConfig["stanzas"].length; i++) {
            if (specConfig["stanzas"][i]["stanzaName"] == "default") {
                let specialDisalbedSetting = {
                    "name": "disabled",
                    "value": "<boolean>",
                    "docString": '* Toggles your input entry off and on.\n* Set to "true" to disable an input.\n* Default: false'
                }
                specConfig["stanzas"][i]["settings"].push(specialDisalbedSetting)
                break;
            }
        }
    }

    // Modular .spec files allow freeform stanzas, but this is not denoted in the static .spec file.
    // So, override the freeform setting on these.
    if(modularSpecFiles.includes(specFileName)) {
        specConfig["allowsFreeformStanzas"] = true;
    }
    return specConfig
}

function parseSpecConfig (str, name) {
    let specConfig = {}
    specConfig = {"specName": name}
    specConfig["allowsFreeformStanzas"] = false
    specConfig["stanzas"] = []

    // Spec files have a preable stating what the file does.  
    // We do not want this in the returned config, so strip it out with a regex.
    // The PREAMBLE_REGEX mataches everything from the beginning of the file
    // up to and including the phrase GLOBAL SETTINGS
    str = str.replace(PREAMBLE_REGEX,"");

    // Remove blank lines to make life easier
    str = str.replace(BLANK_LINE_REGEX, "")

    if(name == "indexes.conf.spec") {
        str = str.replace("# PER INDEX OPTIONS", "[<index>]");
        str = str.replace("# PER VIRTUAL INDEX OPTIONS", "[<virtual-index>]");
        str = str.replace("# [provider-family:family_name]", "[provider-family:<family_name>]");
        str = str.replace(/^#\s*\[volume:volume_name\]/gm, "[volume:<volume_name>]")
    }

    while(str.length) {

        // Find a  section
        // A section starts with a stanza [stanza] and includes all text until the next stanza.
        let section = str.match(SECTION_REGEX)[0]

        let stanza = createStanza(section)

        // Some spec files can create empty default stanzas if the spec file explicitlly defines [default] or [global]
        // limits.conf.spec does this with [default] for example.
        // serverclass.conf does this with [global] for example.
        // In these cases, a default stanza can be produced with no settings.

        if(!["default", "global"].includes(stanza["stanzaName"])) {
            specConfig["stanzas"].push(stanza)
        } else if(stanza["settings"].length > 0) {
            specConfig["stanzas"].push(stanza)
        }

        if(stanza["stanzaType"] == stanzaTypes.FREEFORM) {
            specConfig["allowsFreeformStanzas"] = true
        }
        
        // Remove the stanza from the working string.
        str = str.replace(section, "")
        str = str.replace(BLANK_LINE_REGEX, "")

    }

    // Special case: searchbnf.conf.spec has a postfix stanza that is commented out.  Add it here.
    if(name == "searchbnf.conf.spec") {
        specConfig.stanzas[0].stanzaName = "<command-name>-command"
        specConfig.stanzas[0].stanzaType = stanzaTypes.FREEFORM
    }
    return specConfig
}

// Create a stanza object from the passed in string
function createStanza (str) {
    /*
    {
        stanzaName: string,
        docString: string,
        stanzaType: enum,
        settings: [
            {
                name: string
                value: string
                docString: string
            }
        ]
    }
    */

    let stanza = {
        "stanzaName":"",
        "docString":"",
        "stanzaType": stanzaTypes.UNKNOWN,
        "settings":[]
    }
    let stanzaSetting = {}
    let lines = str.split(/[\r\n]+/g)
    let defaultStanzaCreated = false


    lines.forEach(function (line) {

        let lineType = lineTypes.UNKNOWN
        
        // Determine the type of line
        if (DEFAULT_STANZA_REGEX.test(line)) {
            lineType = lineTypes.DEFAULT_STANZA
        } else if (STANZA_REGEX.test(line) || DEFAULT_STANZA_REGEX.test(line)) { 
            lineType = lineTypes.STANZA
        }
        else if (SETTING_REGEX.test(line)) { 
            lineType = lineTypes.SETTING 
        }
        else if (COMMENT_REGEX.test(line)) {
            lineType = lineTypes.COMMENT
        }
        else { 
            lineType = lineTypes.DOC_STRING 
        }

        switch(lineType) {
            case lineTypes.COMMENT: {
                break
            }
            case lineTypes.DEFAULT_STANZA: {
                stanza["stanzaName"] = "default"
                stanza["docString"] = ""
                stanza["stanzaType"] = stanzaTypes.ABSOLUTE
                defaultStanzaCreated = true
                break
            }
            case lineTypes.STANZA: {
                stanza["stanzaName"] = line.match(STANZA_REGEX).groups['stanza']
                stanza["docString"] = ""
                stanza["stanzaType"] = getStanzaType(line)
                break
            }
            case lineTypes.DOC_STRING: {
                // We need to determine if this doc string goes with a setting or stanza
                if(stanzaSetting["name"]) {
                    // There is a current seting, so add this doc string to the setting
                    stanzaSetting["docString"] += line + "\n"
                } else {
                    // There is no current setting, so add this doc string to the stanza
                    stanza["docString"] += line + "\n"
                }
                break
            }
            case lineTypes.SETTING: {
                if(stanzaSetting["name"]) {
                    // If a stanza setting name exists and we got here,
                    // that means we are at a new setting.
                    // So, commit the current setting to the array
                    // before constructing a new setting.
                    stanza["settings"].push(stanzaSetting)
                }

                let setting = line.match(SETTING_REGEX)
                stanzaSetting = {}
                stanzaSetting["name"] = setting.groups["setting"]
                stanzaSetting["value"] = setting.groups["value"]
                stanzaSetting["docString"] = ""
                break
            }

        }
    })

    // Commit the last stanza setting if any
    if(stanzaSetting["name"]) {
        stanza["settings"].push(stanzaSetting)
    }
    return stanza
}

function getStanzaSettingsByPrefix(specConfig, stanza, pattern) {
    // Given a stanza prefix, return the stanza config

    let matchStanza = stanza.match(pattern)[1]
    for (var i=0; i < specConfig["stanzas"].length; i++) {
        if (specConfig["stanzas"][i]["stanzaType"] != stanzaTypes.PREFIX) {
            continue
        }
        let thisStanza = `[${specConfig["stanzas"][i]["stanzaName"]}]`  // Adding the brackets back for comparison
        if ((pattern.test(thisStanza)) && (thisStanza.match(pattern)[1] == matchStanza)) {
            return [...specConfig["stanzas"][i].settings]
        }
    }
    return null
}

function getStanzaSettingsByStanzaName(specConfig, stanzaName) {
    // Given a stanza name, return the stanza config

    for (var i=0; i < specConfig["stanzas"].length; i++) {
        let thisStanza = `[${specConfig["stanzas"][i]["stanzaName"]}]`  // Adding the brackets back for comparison
        if (thisStanza == stanzaName) {
            return [...specConfig["stanzas"][i].settings]
        }
    }

    return []
}

function getStanzaSettingsbyFreeform(specConfig) {
    // Get freeform stanza settings.

    let freeFormStanzas = []

    for (var i=0; i < specConfig["stanzas"].length; i++) {
        if (specConfig["stanzas"][i]["stanzaType"] == stanzaTypes.FREEFORM) {
            freeFormStanzas.push(...specConfig["stanzas"][i].settings)
        }
    }

    // Special case for inputs.conf
    // Inputs.conf can have modular inputs with all kinds of settings.
    // Add python.version setting here.  See https://github.com/splunk/vscode-extension-splunk/issues/50
    // TODO: add settings from README/inputs.conf.spec in a future release.  See issue https://github.com/splunk/vscode-extension-splunk/issues/59
    if(specConfig.specName == "inputs.conf.spec") {
        let specialPythonSeting = {
            "name": "python.version",
            "value": "{default|python|python2|python3}",
            "docString": "* For Python scripts only, selects which Python version to use.\n* Set to either \"default\" or \"python\" to use the system-wide default Python\n  version.\n* Optional.\n* Default: Not set; uses the system-wide Python version."
        }
        freeFormStanzas.push(specialPythonSeting)
    }
    
    return freeFormStanzas
}

function getStanzaType(stanza) {
    // Given a stanza, return a stanzaType

    let stanzaType = stanzaTypes.UNKNOWN

    if (STANZA_FREEFORM_REGEX.test(stanza)) {
        stanzaType = stanzaTypes.FREEFORM
    } else if (STANZA_PREFIX_REGEX.test(stanza)) { 
        stanzaType = stanzaTypes.PREFIX
    } else if (STANZA_ABSOLUTE_REGEX.test(stanza)) {
        stanzaType = stanzaTypes.ABSOLUTE
    }

    return stanzaType
}

function getStanzaSettings(specConfig, stanzaName) {
    // Given a stanzaName, return its settings
    // Stanzas could follow one of these syntaxes:
    //    * prefix   - examples: [monitor://<path>], [tcp://<remote server>:<port>]
    //    * absolute - examples: [tcp], [SSL]
    //    * freeform - examples: [my:sourcetype], [my_alert_action], [foo] (if the spec allows freeform)

    let settings = []
    
    // Special case for indexes.conf - see https://github.com/splunk/vscode-extension-splunk/issues/23
    // All the settings in indexes.conf are valid, so return them all.
    if(specConfig.specName == "indexes.conf.spec") {
        let settings = []
        for (var i=0; i < specConfig["stanzas"].length; i++) {
            settings.push(...specConfig["stanzas"][i].settings)
        }
        return settings
    }

    let defaultSettings = getStanzaSettingsByStanzaName(specConfig, "[default]")
    let stanzaType = getStanzaType(stanzaName)
    if((stanzaName == "[default]") && (!specConfig.allowsFreeformStanzas)) { return defaultSettings }

    switch(stanzaType) {

        case stanzaTypes.PREFIX: {
            let colonMatch = /^\[(?<prefix>[^:].*?:)[\w|\<]/        // Example: [tcp:test] OR [tcp:<...
            let uriMatch   = /^\[(?<prefix>[^:].*?:\/\/)[\w|\<|\/]/    // Example: [tcp://test] OR [tcp://<... OR [script:///]
            let sepMatch    = /^\[(?<prefix>.*?[=|_|:])[\w|\<|\/]/     // Example [author=test] OR [role_name]
            if (uriMatch.test(stanzaName)) {
                settings = getStanzaSettingsByPrefix(specConfig, stanzaName, uriMatch)
            } else if (colonMatch.test(stanzaName)) {
                settings = getStanzaSettingsByPrefix(specConfig, stanzaName, colonMatch)
            } else if (sepMatch.test(stanzaName)) {
                settings = getStanzaSettingsByPrefix(specConfig, stanzaName, sepMatch)
            } else {
                settings = null
            }
            
            if ((!settings) && (specConfig.allowsFreeformStanzas)) {
                // A freeform stanza like [my:sourcetype] may show up here too.
                settings = getStanzaSettingsbyFreeform(specConfig)
            }

            if(settings) {
                settings.push(...defaultSettings)
                return settings
            }
            break
        }

        case stanzaTypes.ABSOLUTE: {
            // An absolute stanza like [SSL]
            settings = getStanzaSettingsByStanzaName(specConfig, stanzaName)

            if ((settings.length == 0) && (specConfig.allowsFreeformStanzas)) {
                // Example: [my_sourcetype] in props.conf
                settings = getStanzaSettingsbyFreeform(specConfig)
            }

            if(settings.length > 0) {
                // Found an absolute stanza with this name
                if (stanzaName != "[default]") {
                    settings.push(...defaultSettings)
                }
            }
            return settings
            
            break
        }
    }

    // We should not get here, but if we did something is invalid
    return null
}

function isStanzaValid(specConfig, stanzaName) {

    // If the spec allows freeform stanzas, then they are all valid
    if(specConfig["allowsFreeformStanzas"] || (specConfig["specName"].endsWith(".conf.spec") && stanzaName == "[default]")) {
        return true
    }

    let stanzaSettings = getStanzaSettings(specConfig, stanzaName)

    if(stanzaSettings && stanzaSettings.length > 0) {
        // If settings were returned for this stanza name, it is valid
        return true
    }

    return false
}

function isValueValid(specValue, settingValue) {

    let isValid = true

    // Look for known types
    switch(specValue) {
        case "<boolean>": {
            let booleans = ["true", "false", "1", "0"]
            if (!booleans.includes(settingValue.toLowerCase())) isValid = false;
            break
        }
        case "<enabled|disabled>": {
            let settings = ["enabled", "disabled"]
            if (!settings.includes(settingValue.toLowerCase())) isValid = false;
            break
        }
        case "<system|none>": {
            let settings = ["system", "none"]
            if (!settings.includes(settingValue.toLowerCase())) isValid = false;
            break
        }
        case "<0 or positive integer>":
        case "<unsigned integer>":
        case "<positive integer>":
        case "<nonnegative integer>":
        case "<non-negative integer>": {
            let INT_REGEX = /^\d+\s*$/
            isValid = INT_REGEX.test(settingValue)
            break
        }
        case "<int>":
        case "<integer>": {
            let INT_REGEX = /^[-]?\d+\s*$/
            isValid = INT_REGEX.test(settingValue)
            break
        }
        case "<decimal number>":
        case "<number>":
        case "<unsigned long>":
        case "<decimal>":
        case "<double>": {
            let FLOAT_REGEX = /^[-]?[0-9]*\.?[0-9]+\s*$/
            isValid = FLOAT_REGEX.test(settingValue)
            break
        }
    }

    // Look for multiple choice types
    if(DROPDOWN_PLACEHOLDER_REGEX.test(specValue)) {
        // Remove square brackets and curly braces
        let possibleValues = specValue.replace(/[\[\{\}\]]/g, '')
        let settings = possibleValues.split('|')
        if (!settings.includes(settingValue.toLowerCase())) isValid = false;
    }

return isValid;
}

function isSettingValid(specConfig, stanzaName, settingString) {

    let isValid = false

    if (!SETTING_REGEX.test(settingString)) {
        // The settingString shound be in the form key = value
        return false
    }

    let setting = settingString.match(SETTING_REGEX)
    let settingName = setting.groups["setting"]
    let settingValue = setting.groups["value"]

    // Get settings for this stanza
    let stanzaSettings = getStanzaSettings(specConfig, stanzaName)

    stanzaSettings.forEach(specSetting => {

        // Look for this exact setting in the specConfig
        if(specSetting["name"] == settingName) {
            // The setting name is valid, is the setting value valid also?
            isValid = isValueValid(specSetting["value"], settingValue)

        } else if (SETTING_PREFIX_REGEX.test(specSetting["name"])) {

            // There is still a chance this is a valid setting.
            // Some settings are prefix settings.
            // For example REPORT-<class> or FIELDALIAS-<class>

            let specSettingPrefixMatch = specSetting["name"].match(SETTING_PREFIX_REGEX)
            let specSettingPrefix = specSettingPrefixMatch.groups["prefix"]
            if(settingName.startsWith(specSettingPrefix)) {
                isValid = true
            }

        } else if(SETTING_FREEFORM_REGEX.test(specSetting["name"])) {

            // There is still a chance this is a valid setting.
            // Some settings are freeform settings.
            // For example <tag1>
            // If a setting is in this form, anything goes.

            isValid = isValueValid(specSetting["value"], settingValue)
        }
    });

    return isValid
}

exports.SETTING_REGEX = SETTING_REGEX
exports.DROPDOWN_PLACEHOLDER_REGEX = DROPDOWN_PLACEHOLDER_REGEX
exports.STANZA_REGEX = STANZA_REGEX
exports.getSpecConfig = getSpecConfig
exports.getStanzaSettings = getStanzaSettings
exports.isStanzaValid = isStanzaValid
exports.isSettingValid = isSettingValid