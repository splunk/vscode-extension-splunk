"use strict";

// Setup file to mock vscode module before any tests run
const Module = require("module");
const path = require("path");

// Store original require
const originalRequire = Module.prototype.require;

// Mock vscode module
const mockVscode = require("./mocks/vscode.js");

// Override require to intercept vscode
Module.prototype.require = function (id) {
  if (id === "vscode") {
    return mockVscode;
  }
  return originalRequire.apply(this, arguments);
};

// Export for use in tests
module.exports = { mockVscode };
