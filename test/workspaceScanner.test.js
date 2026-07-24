"use strict";

/**
 * Unit Tests for Workspace Scanner
 * 
 * These tests demonstrate how the workspace scanner finds related
 * Splunk configuration files across the app directory structure.
 */

// Setup must be required first to mock vscode
const { mockVscode } = require("./setup.js");

const { expect } = require("chai");
const path = require("path");
const fs = require("fs");
const os = require("os");

const workspaceScanner = require("../out/workspaceScanner.js");

// Create a temporary test directory structure
let testAppDir;

describe("workspaceScanner", function () {
  
  before(function () {
    // Create a realistic Splunk app structure for testing
    testAppDir = path.join(os.tmpdir(), "test_splunk_app_" + Date.now());
    
    // Create directories
    fs.mkdirSync(path.join(testAppDir, "default"), { recursive: true });
    fs.mkdirSync(path.join(testAppDir, "local"), { recursive: true });
    fs.mkdirSync(path.join(testAppDir, "lookups"), { recursive: true });
    
    // Create test conf files
    fs.writeFileSync(
      path.join(testAppDir, "default", "props.conf"),
      "[source::syslog]\nTIME_FORMAT = %b %d %H:%M:%S\n"
    );
    fs.writeFileSync(
      path.join(testAppDir, "default", "transforms.conf"),
      "[extract_user]\nREGEX = user=(\\w+)\nFORMAT = user::$1\n\n[extract_ip]\nREGEX = (\\d+\\.\\d+\\.\\d+\\.\\d+)\n"
    );
    fs.writeFileSync(
      path.join(testAppDir, "local", "props.conf"),
      "[my_sourcetype]\nREPORT-fields = extract_user\n"
    );
    fs.writeFileSync(
      path.join(testAppDir, "local", "transforms.conf"),
      "[my_custom_transform]\nREGEX = custom=(\\w+)\n"
    );
    fs.writeFileSync(
      path.join(testAppDir, "lookups", "users.csv"),
      "user,department\njohn,engineering\njane,sales\n"
    );
  });
  
  after(function () {
    // Cleanup test directory
    fs.rmSync(testAppDir, { recursive: true, force: true });
  });
  
  describe("getAppDirectory()", function () {
    
    it("should return app root when conf is in default/", function () {
      const confPath = path.join(testAppDir, "default", "props.conf");
      const appDir = workspaceScanner.getAppDirectory(confPath);
      expect(appDir).to.equal(testAppDir);
    });
    
    it("should return app root when conf is in local/", function () {
      const confPath = path.join(testAppDir, "local", "props.conf");
      const appDir = workspaceScanner.getAppDirectory(confPath);
      expect(appDir).to.equal(testAppDir);
    });
    
    it("should handle conf at app root (non-standard)", function () {
      const confPath = path.join(testAppDir, "props.conf");
      const appDir = workspaceScanner.getAppDirectory(confPath);
      expect(appDir).to.equal(testAppDir);
    });
  });
  
  describe("getConfLayer()", function () {
    
    it("should identify default/ layer", function () {
      const confPath = path.join(testAppDir, "default", "props.conf");
      expect(workspaceScanner.getConfLayer(confPath)).to.equal("default");
    });
    
    it("should identify local/ layer", function () {
      const confPath = path.join(testAppDir, "local", "props.conf");
      expect(workspaceScanner.getConfLayer(confPath)).to.equal("local");
    });
    
    it("should identify root layer", function () {
      const confPath = path.join(testAppDir, "props.conf");
      expect(workspaceScanner.getConfLayer(confPath)).to.equal("root");
    });
  });
  
  describe("findRelatedConfFiles()", function () {
    
    it("should find only default/ when editing default/props.conf", function () {
      // App developer mode: only look in default/
      const propsPath = path.join(testAppDir, "default", "props.conf");
      const found = workspaceScanner.findRelatedConfFiles(propsPath, "transforms.conf");
      
      expect(found).to.have.lengthOf(1);
      expect(found[0]).to.include("default");
      expect(found[0]).to.not.include("local");
    });
    
    it("should find both local/ and default/ when editing local/props.conf", function () {
      // Admin/user mode: check both, local first
      const propsPath = path.join(testAppDir, "local", "props.conf");
      const found = workspaceScanner.findRelatedConfFiles(propsPath, "transforms.conf");
      
      expect(found).to.have.lengthOf(2);
      expect(found[0]).to.include("local");  // local/ should be first
      expect(found[1]).to.include("default");
    });
    
    it("should return empty array when target file doesn't exist", function () {
      const propsPath = path.join(testAppDir, "default", "props.conf");
      const found = workspaceScanner.findRelatedConfFiles(propsPath, "nonexistent.conf");
      
      expect(found).to.be.an("array").that.is.empty;
    });
  });
  
  describe("parseStanzaNames()", function () {
    
    it("should extract all stanza names from a conf file", function () {
      const transformsPath = path.join(testAppDir, "default", "transforms.conf");
      const stanzas = workspaceScanner.parseStanzaNames(transformsPath);
      
      expect(stanzas.has("extract_user")).to.be.true;
      expect(stanzas.has("extract_ip")).to.be.true;
    });
    
    it("should return lowercase stanza names for case-insensitive matching", function () {
      const transformsPath = path.join(testAppDir, "default", "transforms.conf");
      const stanzas = workspaceScanner.parseStanzaNames(transformsPath);
      
      // All should be lowercase
      for (const stanza of stanzas) {
        expect(stanza).to.equal(stanza.toLowerCase());
      }
    });
    
    it("should return empty set for non-existent file", function () {
      const stanzas = workspaceScanner.parseStanzaNames("/nonexistent/path.conf");
      expect(stanzas.size).to.equal(0);
    });
  });
  
  describe("getMergedStanzas()", function () {
    
    it("should merge stanzas from local/ and default/ when editing local/", function () {
      const propsPath = path.join(testAppDir, "local", "props.conf");
      const stanzas = workspaceScanner.getMergedStanzas(propsPath, "transforms.conf");
      
      // Should have stanzas from BOTH files
      expect(stanzas.has("extract_user")).to.be.true;      // from default/
      expect(stanzas.has("extract_ip")).to.be.true;        // from default/
      expect(stanzas.has("my_custom_transform")).to.be.true; // from local/
    });
    
    it("should only return default/ stanzas when editing default/", function () {
      const propsPath = path.join(testAppDir, "default", "props.conf");
      const stanzas = workspaceScanner.getMergedStanzas(propsPath, "transforms.conf");
      
      // Should only have stanzas from default/
      expect(stanzas.has("extract_user")).to.be.true;
      expect(stanzas.has("extract_ip")).to.be.true;
      expect(stanzas.has("my_custom_transform")).to.be.false; // NOT from local/
    });
  });
  
  describe("getLookupsDirectory()", function () {
    
    it("should find lookups/ directory from any conf file", function () {
      const propsPath = path.join(testAppDir, "local", "props.conf");
      const lookupsDir = workspaceScanner.getLookupsDirectory(propsPath);
      
      expect(lookupsDir).to.equal(path.join(testAppDir, "lookups"));
    });
    
    it("should return null when lookups/ doesn't exist", function () {
      // Create a temp app without lookups/
      const noLookupsApp = path.join(os.tmpdir(), "no_lookups_" + Date.now());
      fs.mkdirSync(path.join(noLookupsApp, "default"), { recursive: true });
      fs.writeFileSync(path.join(noLookupsApp, "default", "props.conf"), "[test]\n");
      
      const lookupsDir = workspaceScanner.getLookupsDirectory(
        path.join(noLookupsApp, "default", "props.conf")
      );
      
      expect(lookupsDir).to.be.null;
      
      // Cleanup
      fs.rmSync(noLookupsApp, { recursive: true, force: true });
    });
  });
});
