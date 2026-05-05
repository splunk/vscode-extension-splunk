"use strict";

// Mock VS Code API for unit testing

class Position {
  constructor(line, character) {
    this.line = line;
    this.character = character;
  }
}

class Range {
  constructor(startLine, startChar, endLine, endChar) {
    if (startLine instanceof Position) {
      this.start = startLine;
      this.end = startChar;
    } else {
      this.start = new Position(startLine, startChar);
      this.end = new Position(endLine, endChar);
    }
  }
}

class Diagnostic {
  constructor(range, message, severity) {
    this.range = range;
    this.message = message;
    this.severity = severity;
    this.source = undefined;
    this.code = undefined;
    this.tags = [];
    this.relatedInformation = [];
  }
}

class DiagnosticRelatedInformation {
  constructor(location, message) {
    this.location = location;
    this.message = message;
  }
}

class Location {
  constructor(uri, rangeOrPosition) {
    this.uri = uri;
    this.range = rangeOrPosition;
  }
}

class CodeAction {
  constructor(title, kind) {
    this.title = title;
    this.kind = kind;
    this.diagnostics = [];
    this.isPreferred = false;
    this.edit = undefined;
    this.command = undefined;
  }
}

class WorkspaceEdit {
  constructor() {
    this._edits = [];
  }

  replace(uri, range, newText) {
    this._edits.push({ type: "replace", uri, range, newText });
  }

  insert(uri, position, newText) {
    this._edits.push({ type: "insert", uri, position, newText });
  }

  delete(uri, range) {
    this._edits.push({ type: "delete", uri, range });
  }

  get edits() {
    return this._edits;
  }
}

const DiagnosticSeverity = {
  Error: 0,
  Warning: 1,
  Information: 2,
  Hint: 3,
};

const DiagnosticTag = {
  Unnecessary: 1,
  Deprecated: 2,
};

const CodeActionKind = {
  QuickFix: "quickfix",
  Refactor: "refactor",
  Empty: "",
};

const Uri = {
  parse: (str) => ({
    toString: () => str,
    fsPath: str,
  }),
  file: (filePath) => ({
    toString: () => `file://${filePath}`,
    fsPath: filePath,
  }),
};

// Mock workspace API for findFiles
const workspace = {
  findFiles: async (pattern, exclude) => {
    // Return empty array in tests - real implementation uses VS Code API
    return [];
  },
};

module.exports = {
  Position,
  Range,
  Diagnostic,
  DiagnosticSeverity,
  DiagnosticTag,
  DiagnosticRelatedInformation,
  Location,
  CodeAction,
  CodeActionKind,
  WorkspaceEdit,
  Uri,
  workspace,
};
