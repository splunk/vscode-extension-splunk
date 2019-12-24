"use strict";
exports.parse = parse
exports.getStanzaSettings = getStanzaSettings
exports.isStanzaValid = isStanzaValid
exports.isSettingValid = isSettingValid

const PREAMBLE_REGEX = /^.*?GLOBAL\sSETTINGS/s
// Start the match at the beginning of the string ^
// Lazily match anything .*?
// Match GLOBAL SETTINGS literally
// Enable multiline /s

const SECTION_REGEX = /^.*?(?=\n\[|$)/s
// Start the match at the beginning of the string ^
// Lazily match anything .*?
// Positive lookahead to match until a newline followed by a [ or the end of the string $
// Enable multiline /s

const COMMENT_REGEX = /^#/
const BLANK_LINE_REGEX = /^\s*\n/gm

const DEFAULT_STANZA_REGEX = /^# Use the \[default\] stanza/

const STANZA_REGEX = /^\[(?<stanza>[^\]].*?)\]/
const STANZA_PREFIX_REGEX = /^\[(?<prefix>[^\]].*?(:|::|::...))[\<|\w|\/]/   // matches things like [tcp:<port>], [tcp:123], [source::...a...], [tcp://<remote server>:<port>], or [tcp://123]
const STANZA_FREEFORM_REGEX = /^\[\<(?<stanza>.*?)\>\]/           // matches things like [<spec>] or [<custom_alert_action>]
const STANZA_ABSOLUTE_REGEX = /^\[(?<stanza>[^\<\>\:\/]+)\]/      // matches things like [tcp] or [SSL] (does not allow <, >, :, or /)

const SETTING_REGEX = /^(?<setting>[\w\-_\<\>\.]+)\s*=\s*(?<value>[^\r\n]+)/
const SETTING_PREFIX_REGEX = /^(?<prefix>[^-].*?-)\<\w+\>/

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

function parse (str, name) {
    // Create a spec object from the passed in string
    /*
    {
        specName: string,
        allowsFreeformStanzas: [true,false],
        stanzas: []
    }
    */

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

    while(str.length) {

        // Find a  section
        // A section starts with a stanza [stanza] and includes all text until the next stanza.
        let section = str.match(SECTION_REGEX)[0]

        let stanza = createStanza(section)

        // Some spec files can create empty default stanzas if the spec file explicitlly defines [default].
        // limits.conf.spec does this for example
        // In these cases, a default stanza can be produced with no settings

        if(stanza["stanzaName"] != "default") {
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
    return specConfig
}

function createStanza (str) {
    // Create a stanza object from the passed in string
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
    // Get the freeform stanza settings.
    // Spec files should only define one freeform stanza, so return the first one

    for (var i=0; i < specConfig["stanzas"].length; i++) {
        if (specConfig["stanzas"][i]["stanzaType"] == stanzaTypes.FREEFORM) {
            return [...specConfig["stanzas"][i].settings]
        }
    }

    return []
}

function getStanzaType(stanza) {
    // Given a stanza, return a stanzaType

    let stanzaType = stanzaTypes.UNKNOWN

    if (STANZA_PREFIX_REGEX.test(stanza)) { 
        stanzaType = stanzaTypes.PREFIX
    } else if (STANZA_FREEFORM_REGEX.test(stanza)) {
        stanzaType = stanzaTypes.FREEFORM
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
    let defaultSettings = getStanzaSettingsByStanzaName(specConfig, "[default]")
    if(stanzaName == "[default]") { return defaultSettings }
    let stanzaType = getStanzaType(stanzaName)

    switch(stanzaType) {

        case stanzaTypes.PREFIX: {
            // There are 2 types of prefix stanzas:
            //    1) [tcp:port]
            //    2) [tcp://port]
            let colonMatch = /^\[(?<prefix>[^:].*?:)[\w|\<]/        // Example: [tcp:test] OR [tcp:<...
            let uriMatch   = /^\[(?<prefix>[^:].*?:\/\/)[\w|\<]/    // Example: [tcp://test] OR [tcp://<...
            if (uriMatch.test(stanzaName)) {
                settings = getStanzaSettingsByPrefix(specConfig, stanzaName, uriMatch)
            } else if (colonMatch.test(stanzaName)) {
                settings = getStanzaSettingsByPrefix(specConfig, stanzaName, colonMatch)
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
                return settings
            }
            
            break
        }
    }

    // We should not get here, but if we did something is invalid
    return null
}

function isStanzaValid(specConfig, stanzaName) {

    // If the spec allows freeform stanzas, then they are all valid
    if(specConfig["allowsFreeformStanzas"]) {
        return true
    }

    let stanzaSettings = getStanzaSettings(specConfig, stanzaName)

    if(stanzaSettings && stanzaSettings.length > 0) {
        // If settings were returned for this stanza name, it is valid
        return true
    }

    return false
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
            isValid = true;
        } else if (SETTING_PREFIX_REGEX.test(specSetting["name"])) {

            // There is still a chance this is a valid setting
            // Some settings are prefix settings.
            // For example REPORT-<class> or FIELDALIAS-<class>

            let specSettingPrefixMatch = specSetting["name"].match(SETTING_PREFIX_REGEX)
            let specSettingPrefix = specSettingPrefixMatch.groups["prefix"]
            if(settingName.startsWith(specSettingPrefix)) {
                isValid = true
            }
        }

        
        
    });

    return isValid
}