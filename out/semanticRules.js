"use strict";
const path = require("path");
const fs = require("fs");
const vscode = require("vscode");

let semanticRulesCache = null;
const SETTING_REGEX = /^(?<setting>\w[\w\-\.]*)\s*=\s*(?<value>.*)$/;
const STANZA_REGEX = /^\[(?<stanza>[^\]]+)\]/;

function loadSemanticRules(extensionPath) {
    if (semanticRulesCache) {
        return semanticRulesCache;
    }
    
    const rulesPath = path.join(extensionPath, "resources", "semantic_rules.json");
    if (!fs.existsSync(rulesPath)) {
        console.log("Semantic rules file not found:", rulesPath);
        return null;
    }
    
    try {
        const content = fs.readFileSync(rulesPath, "utf-8");
        semanticRulesCache = JSON.parse(content);
        return semanticRulesCache;
    } catch (err) {
        console.error("Error loading semantic rules:", err);
        return null;
    }
}

function getConfFileName(document) {
    return path.basename(document.uri.fsPath);
}

function parseStanzaContext(document, stanzaLine) {
    const context = {
        stanzaName: "",
        stanzaRange: null,
        settings: {},
        settingLines: {}
    };
    
    const stanzaMatch = document.lineAt(stanzaLine).text.match(STANZA_REGEX);
    if (!stanzaMatch) return null;
    
    context.stanzaName = stanzaMatch.groups.stanza;
    context.stanzaRange = new vscode.Range(stanzaLine, 0, stanzaLine, document.lineAt(stanzaLine).text.length);
    
    for (let i = stanzaLine + 1; i < document.lineCount; i++) {
        const lineText = document.lineAt(i).text.trim();
        
        if (lineText.startsWith("[")) break;
        if (lineText === "" || lineText.startsWith("#")) continue;
        
        const settingMatch = lineText.match(SETTING_REGEX);
        if (settingMatch) {
            const name = settingMatch.groups.setting;
            const value = settingMatch.groups.value.trim();
            context.settings[name] = value;
            context.settingLines[name] = i;
        }
    }
    
    return context;
}

function getAllStanzaContexts(document) {
    const contexts = [];
    for (let i = 0; i < document.lineCount; i++) {
        if (document.lineAt(i).text.trim().startsWith("[")) {
            const ctx = parseStanzaContext(document, i);
            if (ctx) contexts.push(ctx);
        }
    }
    return contexts;
}

function matchesTrigger(trigger, stanzaContext) {
    if (trigger.stanza_pattern) {
        const regex = new RegExp(trigger.stanza_pattern);
        if (!regex.test("[" + stanzaContext.stanzaName + "]")) {
            return false;
        }
    }
    
    if (trigger.settings) {
        for (const [key, expectedValue] of Object.entries(trigger.settings)) {
            const actualValue = stanzaContext.settings[key];
            if (actualValue === undefined) return false;
            if (String(actualValue).toLowerCase() !== String(expectedValue).toLowerCase()) {
                return false;
            }
        }
    }

    if (trigger.settings_regex) {
        for (const [key, pattern] of Object.entries(trigger.settings_regex)) {
            const actualValue = stanzaContext.settings[key];
            if (actualValue === undefined) return false;
            let regex;
            try {
                regex = new RegExp(pattern);
            } catch (err) {
                console.error(`Invalid settings_regex pattern for ${key}: ${pattern}`, err);
                return false;
            }
            if (!regex.test(String(actualValue))) {
                return false;
            }
        }
    }

    if (trigger.setting_exists) {
        if (!(trigger.setting_exists in stanzaContext.settings)) {
            return false;
        }
    }
    
    if (trigger.setting_missing) {
        if (trigger.setting_missing in stanzaContext.settings) {
            return false;
        }
    }
    
    if (trigger.with_any) {
        const hasAny = trigger.with_any.some(s => s in stanzaContext.settings);
        if (!hasAny) return false;
    }
    
    if (trigger.with_all) {
        const hasAll = trigger.with_all.every(s => s in stanzaContext.settings);
        if (!hasAll) return false;
    }
    
    if (trigger.without) {
        const hasNone = trigger.without.every(s => !(s in stanzaContext.settings));
        if (!hasNone) return false;
    }
    
    if (trigger.value_less_than) {
        for (const [key, threshold] of Object.entries(trigger.value_less_than)) {
            const val = parseFloat(stanzaContext.settings[key]);
            if (isNaN(val) || val >= threshold) return false;
        }
    }
    
    if (trigger.value_greater_than) {
        for (const [key, threshold] of Object.entries(trigger.value_greater_than)) {
            const val = parseFloat(stanzaContext.settings[key]);
            if (isNaN(val) || val <= threshold) return false;
        }
    }
    
    return true;
}

function getSeverity(severityStr) {
    switch (severityStr) {
        case "error": return vscode.DiagnosticSeverity.Error;
        case "warning": return vscode.DiagnosticSeverity.Warning;
        case "information": return vscode.DiagnosticSeverity.Information;
        case "hint": return vscode.DiagnosticSeverity.Hint;
        default: return vscode.DiagnosticSeverity.Information;
    }
}

function evaluateDocument(extensionPath, document) {
    const suggestions = [];
    const rules = loadSemanticRules(extensionPath);
    if (!rules) return suggestions;
    
    const confFile = getConfFileName(document);
    const confRules = rules.rules[confFile];
    if (!confRules) return suggestions;
    
    const stanzaContexts = getAllStanzaContexts(document);
    
    for (const ctx of stanzaContexts) {
        for (const [categoryName, category] of Object.entries(confRules)) {
            if (!category.patterns) continue;
            
            for (const pattern of category.patterns) {
                if (pattern.enabled === false) continue;
                
                if (matchesTrigger(pattern.trigger, ctx)) {
                    suggestions.push({
                        ruleId: pattern.id,
                        range: ctx.stanzaRange,
                        stanzaContext: ctx,
                        suggestion: pattern.suggestion,
                        fix: pattern.fix
                    });
                }
            }
        }
    }
    
    return suggestions;
}

function getRuleById(extensionPath, ruleId) {
    const rules = loadSemanticRules(extensionPath);
    if (!rules) return null;
    
    for (const [confFile, confRules] of Object.entries(rules.rules)) {
        for (const [categoryName, category] of Object.entries(confRules)) {
            if (!category.patterns) continue;
            for (const pattern of category.patterns) {
                if (pattern.id === ruleId) {
                    return pattern;
                }
            }
        }
    }
    return null;
}

function clearCache() {
    semanticRulesCache = null;
}

exports.loadSemanticRules = loadSemanticRules;
exports.evaluateDocument = evaluateDocument;
exports.getRuleById = getRuleById;
exports.getSeverity = getSeverity;
exports.clearCache = clearCache;
exports.parseStanzaContext = parseStanzaContext;
