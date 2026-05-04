"use strict";
const vscode = require("vscode");
const semanticRules = require("./semanticRules.js");

class SplunkCodeActionProvider {
  constructor(extensionPath) {
    this.extensionPath = extensionPath;
  }

  static get providedCodeActionKinds() {
    return [vscode.CodeActionKind.QuickFix, vscode.CodeActionKind.Refactor];
  }

  provideCodeActions(document, range, context) {
    const actions = [];

    for (const diagnostic of context.diagnostics) {
      // Handle semantic linting diagnostics
      if (diagnostic.source === "splunk-semantic") {
        const ruleId = diagnostic.code;
        const rule = semanticRules.getRuleById(this.extensionPath, ruleId);

        if (!rule) continue;

        if (rule.fix) {
          const fixAction = this.createFixAction(document, diagnostic, rule);
          if (fixAction) actions.push(fixAction);
        }

        if (rule.suggestion.documentation) {
          const learnMoreAction = this.createLearnMoreAction(rule);
          actions.push(learnMoreAction);
        }
      }
    }

    return actions;
  }

  createFixAction(document, diagnostic, rule) {
    const fix = rule.fix;
    if (!fix || !fix.changes || fix.changes.length === 0) return null;

    const action = new vscode.CodeAction(
      `Fix: ${rule.suggestion.title}`,
      vscode.CodeActionKind.QuickFix,
    );

    action.diagnostics = [diagnostic];
    action.isPreferred = true;

    const edit = new vscode.WorkspaceEdit();
    const stanzaLine = diagnostic.range.start.line;

    const stanzaContext = semanticRules.parseStanzaContext(
      document,
      stanzaLine,
    );
    if (!stanzaContext) return null;

    let lastSettingLine = stanzaLine;
    for (const line of Object.values(stanzaContext.settingLines)) {
      if (line > lastSettingLine) lastSettingLine = line;
    }

    for (const change of fix.changes) {
      switch (change.action) {
        case "set": {
          if (change.setting in stanzaContext.settingLines) {
            const line = stanzaContext.settingLines[change.setting];
            const lineText = document.lineAt(line).text;
            const newLine = `${change.setting} = ${change.value}`;
            edit.replace(
              document.uri,
              new vscode.Range(line, 0, line, lineText.length),
              newLine,
            );
          } else {
            const insertPosition = new vscode.Position(lastSettingLine + 1, 0);
            edit.insert(
              document.uri,
              insertPosition,
              `${change.setting} = ${change.value}\n`,
            );
            lastSettingLine++;
          }
          break;
        }
        case "add": {
          if (!(change.setting in stanzaContext.settingLines)) {
            const insertPosition = new vscode.Position(lastSettingLine + 1, 0);
            edit.insert(
              document.uri,
              insertPosition,
              `${change.setting} = ${change.value}\n`,
            );
            lastSettingLine++;
          }
          break;
        }
        case "remove": {
          if (change.setting in stanzaContext.settingLines) {
            const line = stanzaContext.settingLines[change.setting];
            edit.delete(document.uri, new vscode.Range(line, 0, line + 1, 0));
          }
          break;
        }
      }
    }

    action.edit = edit;
    return action;
  }

  createLearnMoreAction(rule) {
    const action = new vscode.CodeAction(
      `Learn more: ${rule.suggestion.title}`,
      vscode.CodeActionKind.Empty,
    );

    action.command = {
      command: "vscode.open",
      title: "Open Documentation",
      arguments: [vscode.Uri.parse(rule.suggestion.documentation)],
    };

    return action;
  }
}

exports.SplunkCodeActionProvider = SplunkCodeActionProvider;
