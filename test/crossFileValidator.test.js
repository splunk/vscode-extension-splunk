"use strict";

/**
 * Unit Tests for Cross-File Validator
 *
 * These tests verify that transform references in props.conf
 * are correctly validated against transforms.conf stanzas.
 */

// Setup must be required first to mock vscode
const { mockVscode } = require("./setup.js");

const { expect } = require("chai");
const path = require("path");
const fs = require("fs");
const os = require("os");

const crossFileValidator = require("../out/crossFileValidator.js");

// Create a temporary test directory structure
let testAppDir;

// Helper to create a mock VS Code document
function createMockDocument(filePath, content) {
  const lines = content.split("\n");
  return {
    uri: { fsPath: filePath },
    lineCount: lines.length,
    lineAt: (n) => ({ text: lines[n] || "" }),
  };
}

describe("crossFileValidator", function () {
  before(function () {
    // Create a realistic Splunk app structure for testing
    testAppDir = path.join(os.tmpdir(), "test_crossfile_app_" + Date.now());

    // Create directories
    fs.mkdirSync(path.join(testAppDir, "default"), { recursive: true });
    fs.mkdirSync(path.join(testAppDir, "local"), { recursive: true });
    fs.mkdirSync(path.join(testAppDir, "lookups"), { recursive: true });

    // Create a lookup file
    fs.writeFileSync(
      path.join(testAppDir, "lookups", "users.csv"),
      "user,department\njohn,engineering\njane,sales\n",
    );

    // Create transforms.conf with some stanzas
    fs.writeFileSync(
      path.join(testAppDir, "default", "transforms.conf"),
      `[extract_user]
REGEX = user=(\\w+)
FORMAT = user::$1

[extract_ip]
REGEX = (\\d+\\.\\d+\\.\\d+\\.\\d+)
FORMAT = src_ip::$1

[my_lookup]
filename = users.csv
`,
    );

    // Create local transforms.conf with additional stanza
    fs.writeFileSync(
      path.join(testAppDir, "local", "transforms.conf"),
      `[local_transform]
REGEX = local=(\\w+)
`,
    );
  });

  after(function () {
    // Cleanup test directory
    fs.rmSync(testAppDir, { recursive: true, force: true });
  });

  describe("validateTransformReferences()", function () {
    it("should return no diagnostics when all references are valid", function () {
      const propsPath = path.join(testAppDir, "local", "props.conf");
      const propsContent = `[my_sourcetype]
REPORT-fields = extract_user, extract_ip
`;
      const doc = createMockDocument(propsPath, propsContent);

      const diagnostics = crossFileValidator.validateTransformReferences(doc);

      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should detect missing transform stanza", function () {
      const propsPath = path.join(testAppDir, "local", "props.conf");
      const propsContent = `[my_sourcetype]
REPORT-fields = extract_user, nonexistent_transform
`;
      const doc = createMockDocument(propsPath, propsContent);

      const diagnostics = crossFileValidator.validateTransformReferences(doc);

      expect(diagnostics).to.have.lengthOf(1);
      expect(diagnostics[0].message).to.include("nonexistent_transform");
      expect(diagnostics[0].message).to.include("not found");
      expect(diagnostics[0].code).to.equal("missing-transform-stanza");
    });

    it("should detect multiple missing stanzas on same line", function () {
      const propsPath = path.join(testAppDir, "local", "props.conf");
      const propsContent = `[my_sourcetype]
REPORT-fields = missing1, extract_user, missing2
`;
      const doc = createMockDocument(propsPath, propsContent);

      const diagnostics = crossFileValidator.validateTransformReferences(doc);

      expect(diagnostics).to.have.lengthOf(2);
      const messages = diagnostics.map((d) => d.message);
      expect(messages.some((m) => m.includes("missing1"))).to.be.true;
      expect(messages.some((m) => m.includes("missing2"))).to.be.true;
    });

    it("should validate TRANSFORMS- references (index-time)", function () {
      const propsPath = path.join(testAppDir, "local", "props.conf");
      const propsContent = `[my_sourcetype]
TRANSFORMS-routing = nonexistent_routing
`;
      const doc = createMockDocument(propsPath, propsContent);

      const diagnostics = crossFileValidator.validateTransformReferences(doc);

      expect(diagnostics).to.have.lengthOf(1);
      expect(diagnostics[0].data.type).to.equal("index-time transform");
    });

    it("should validate LOOKUP- references", function () {
      const propsPath = path.join(testAppDir, "local", "props.conf");
      const propsContent = `[my_sourcetype]
LOOKUP-users = my_lookup
LOOKUP-missing = nonexistent_lookup
`;
      const doc = createMockDocument(propsPath, propsContent);

      const diagnostics = crossFileValidator.validateTransformReferences(doc);

      expect(diagnostics).to.have.lengthOf(1);
      expect(diagnostics[0].message).to.include("nonexistent_lookup");
    });

    it("should find stanzas from local/ when editing local/props.conf", function () {
      const propsPath = path.join(testAppDir, "local", "props.conf");
      const propsContent = `[my_sourcetype]
REPORT-local = local_transform
`;
      const doc = createMockDocument(propsPath, propsContent);

      const diagnostics = crossFileValidator.validateTransformReferences(doc);

      // local_transform exists in local/transforms.conf
      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should NOT find local/ stanzas when editing default/props.conf", function () {
      const propsPath = path.join(testAppDir, "default", "props.conf");
      const propsContent = `[my_sourcetype]
REPORT-local = local_transform
`;
      const doc = createMockDocument(propsPath, propsContent);

      const diagnostics = crossFileValidator.validateTransformReferences(doc);

      // local_transform is in local/, but we're editing default/
      // App developer shouldn't reference local/ stanzas
      expect(diagnostics).to.have.lengthOf(1);
      expect(diagnostics[0].message).to.include("local_transform");
    });

    it("should skip non-props.conf files", function () {
      const otherPath = path.join(testAppDir, "local", "inputs.conf");
      const content = `[monitor:///var/log]
REPORT-fields = whatever
`;
      const doc = createMockDocument(otherPath, content);

      const diagnostics = crossFileValidator.validateTransformReferences(doc);

      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should skip comment lines", function () {
      const propsPath = path.join(testAppDir, "local", "props.conf");
      const propsContent = `[my_sourcetype]
# REPORT-fields = nonexistent
REPORT-fields = extract_user
`;
      const doc = createMockDocument(propsPath, propsContent);

      const diagnostics = crossFileValidator.validateTransformReferences(doc);

      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should be case-insensitive for stanza matching", function () {
      const propsPath = path.join(testAppDir, "local", "props.conf");
      const propsContent = `[my_sourcetype]
REPORT-fields = EXTRACT_USER
`;
      const doc = createMockDocument(propsPath, propsContent);

      const diagnostics = crossFileValidator.validateTransformReferences(doc);

      // extract_user exists, EXTRACT_USER should match
      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should include diagnostic data for quick fixes", function () {
      const propsPath = path.join(testAppDir, "local", "props.conf");
      const propsContent = `[my_sourcetype]
REPORT-fields = missing_stanza
`;
      const doc = createMockDocument(propsPath, propsContent);

      const diagnostics = crossFileValidator.validateTransformReferences(doc);

      expect(diagnostics).to.have.lengthOf(1);
      expect(diagnostics[0].data).to.exist;
      expect(diagnostics[0].data.stanzaName).to.equal("missing_stanza");
      expect(diagnostics[0].data.type).to.equal("search-time transform");
    });
  });

  describe("getTransformReferenceSummary()", function () {
    it("should summarize all transform references in a file", function () {
      const propsPath = path.join(testAppDir, "local", "props.conf");
      fs.writeFileSync(
        propsPath,
        `[sourcetype1]
REPORT-a = extract_user
TRANSFORMS-b = extract_ip

[sourcetype2]
LOOKUP-c = my_lookup
`,
      );

      const summary =
        crossFileValidator.getTransformReferenceSummary(propsPath);

      expect(summary.references).to.have.lengthOf(3);
      expect(summary.availableStanzas).to.include("extract_user");
      expect(summary.availableStanzas).to.include("local_transform");
    });
  });

  describe("validateLookupFiles()", function () {
    it("should return no diagnostics when lookup file exists", function () {
      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const transformsContent = `[my_lookup]
filename = users.csv
`;
      const doc = createMockDocument(transformsPath, transformsContent);

      const diagnostics = crossFileValidator.validateLookupFiles(doc);

      // users.csv exists in lookups/
      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should detect missing lookup file", function () {
      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const transformsContent = `[my_lookup]
filename = nonexistent.csv
`;
      const doc = createMockDocument(transformsPath, transformsContent);

      const diagnostics = crossFileValidator.validateLookupFiles(doc);

      expect(diagnostics).to.have.lengthOf(1);
      expect(diagnostics[0].message).to.include("nonexistent.csv");
      expect(diagnostics[0].message).to.include("not found");
      expect(diagnostics[0].code).to.equal("missing-lookup-file");
    });

    it("should accept .csv.gz compressed files", function () {
      // Create a compressed lookup file
      fs.writeFileSync(
        path.join(testAppDir, "lookups", "compressed.csv.gz"),
        "compressed",
      );

      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const transformsContent = `[compressed_lookup]
filename = compressed.csv.gz
`;
      const doc = createMockDocument(transformsPath, transformsContent);

      const diagnostics = crossFileValidator.validateLookupFiles(doc);

      expect(diagnostics).to.be.an("array").that.is.empty;

      // Cleanup
      fs.unlinkSync(path.join(testAppDir, "lookups", "compressed.csv.gz"));
    });

    it("should find .gz version when .csv is referenced", function () {
      // Create only the .gz version
      fs.writeFileSync(
        path.join(testAppDir, "lookups", "gzonly.csv.gz"),
        "compressed",
      );

      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const transformsContent = `[gz_lookup]
filename = gzonly.csv
`;
      const doc = createMockDocument(transformsPath, transformsContent);

      const diagnostics = crossFileValidator.validateLookupFiles(doc);

      // Should find gzonly.csv.gz when gzonly.csv is referenced
      expect(diagnostics).to.be.an("array").that.is.empty;

      // Cleanup
      fs.unlinkSync(path.join(testAppDir, "lookups", "gzonly.csv.gz"));
    });

    it("should warn when no lookups/ directory exists", function () {
      // Create a temp app without lookups/
      const noLookupsApp = path.join(os.tmpdir(), "no_lookups_" + Date.now());
      fs.mkdirSync(path.join(noLookupsApp, "default"), { recursive: true });

      const transformsPath = path.join(
        noLookupsApp,
        "default",
        "transforms.conf",
      );
      fs.writeFileSync(
        transformsPath,
        `[my_lookup]
filename = users.csv
`,
      );

      const content = fs.readFileSync(transformsPath, "utf-8");
      const doc = createMockDocument(transformsPath, content);

      const diagnostics = crossFileValidator.validateLookupFiles(doc);

      expect(diagnostics).to.have.lengthOf(1);
      expect(diagnostics[0].code).to.equal("no-lookups-directory");
      expect(diagnostics[0].message).to.include(
        "No lookups/ directories found",
      );

      // Cleanup
      fs.rmSync(noLookupsApp, { recursive: true, force: true });
    });

    it("should skip non-transforms.conf files", function () {
      const otherPath = path.join(testAppDir, "default", "props.conf");
      const doc = createMockDocument(
        otherPath,
        `[my_lookup]
filename = users.csv
`,
      );

      const diagnostics = crossFileValidator.validateLookupFiles(doc);

      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should include diagnostic data for quick fixes", function () {
      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const transformsContent = `[my_lookup]
filename = missing.csv
`;
      const doc = createMockDocument(transformsPath, transformsContent);

      const diagnostics = crossFileValidator.validateLookupFiles(doc);

      expect(diagnostics).to.have.lengthOf(1);
      expect(diagnostics[0].data).to.exist;
      expect(diagnostics[0].data.filename).to.equal("missing.csv");
      expect(diagnostics[0].data.stanzaName).to.equal("my_lookup");
    });

    it("should validate multiple lookup stanzas", function () {
      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const transformsContent = `[lookup1]
filename = users.csv

[lookup2]
filename = missing1.csv

[lookup3]
filename = missing2.csv
`;
      const doc = createMockDocument(transformsPath, transformsContent);

      const diagnostics = crossFileValidator.validateLookupFiles(doc);

      // users.csv exists, missing1.csv and missing2.csv don't
      expect(diagnostics).to.have.lengthOf(2);
      const filenames = diagnostics.map((d) => d.data.filename);
      expect(filenames).to.include("missing1.csv");
      expect(filenames).to.include("missing2.csv");
    });
  });

  describe("validateLookupFiles() with SPLUNK_HOME", function () {
    let splunkHome;

    before(function () {
      // Create a mock SPLUNK_HOME structure
      splunkHome = path.join(os.tmpdir(), "splunk_home_" + Date.now());

      // System lookups
      fs.mkdirSync(path.join(splunkHome, "etc", "system", "local", "lookups"), {
        recursive: true,
      });
      fs.mkdirSync(
        path.join(splunkHome, "etc", "system", "default", "lookups"),
        { recursive: true },
      );
      fs.writeFileSync(
        path.join(
          splunkHome,
          "etc",
          "system",
          "local",
          "lookups",
          "system_local.csv",
        ),
        "field1,field2\nval1,val2\n",
      );
      fs.writeFileSync(
        path.join(
          splunkHome,
          "etc",
          "system",
          "default",
          "lookups",
          "system_default.csv",
        ),
        "field1,field2\nval1,val2\n",
      );

      // User-specific lookups
      fs.mkdirSync(
        path.join(
          splunkHome,
          "etc",
          "users",
          "admin",
          "test_crossfile_app",
          "lookups",
        ),
        { recursive: true },
      );
      fs.writeFileSync(
        path.join(
          splunkHome,
          "etc",
          "users",
          "admin",
          "test_crossfile_app",
          "lookups",
          "user_lookup.csv",
        ),
        "user,role\nadmin,superuser\n",
      );
    });

    after(function () {
      fs.rmSync(splunkHome, { recursive: true, force: true });
    });

    it("should find lookup in system local directory", function () {
      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const transformsContent = `[sys_lookup]
filename = system_local.csv
`;
      const doc = createMockDocument(transformsPath, transformsContent);

      const diagnostics = crossFileValidator.validateLookupFiles(doc, {
        splunkHome,
      });

      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should find lookup in system default directory", function () {
      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const transformsContent = `[sys_lookup]
filename = system_default.csv
`;
      const doc = createMockDocument(transformsPath, transformsContent);

      const diagnostics = crossFileValidator.validateLookupFiles(doc, {
        splunkHome,
      });

      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should find user-specific lookup when user is specified", function () {
      // Need to rename testAppDir to match the user lookup path
      const appName = path.basename(testAppDir);

      // Create user lookup for this specific app
      const userLookupDir = path.join(
        splunkHome,
        "etc",
        "users",
        "testuser",
        appName,
        "lookups",
      );
      fs.mkdirSync(userLookupDir, { recursive: true });
      fs.writeFileSync(
        path.join(userLookupDir, "my_user_lookup.csv"),
        "a,b\n1,2\n",
      );

      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const transformsContent = `[user_lookup]
filename = my_user_lookup.csv
`;
      const doc = createMockDocument(transformsPath, transformsContent);

      const diagnostics = crossFileValidator.validateLookupFiles(doc, {
        splunkHome,
        currentUser: "testuser",
      });

      expect(diagnostics).to.be.an("array").that.is.empty;

      // Cleanup
      fs.rmSync(path.join(splunkHome, "etc", "users", "testuser"), {
        recursive: true,
        force: true,
      });
    });

    it("should prioritize app lookup over system lookup", function () {
      // Create a lookup with same name in both app and system
      fs.writeFileSync(
        path.join(splunkHome, "etc", "system", "local", "lookups", "users.csv"),
        "different,content\n",
      );

      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const transformsContent = `[my_lookup]
filename = users.csv
`;
      const doc = createMockDocument(transformsPath, transformsContent);

      const diagnostics = crossFileValidator.validateLookupFiles(doc, {
        splunkHome,
      });

      // Should find app's users.csv first (no diagnostic)
      expect(diagnostics).to.be.an("array").that.is.empty;
    });
  });

  describe("getAvailableLookupFiles()", function () {
    it("should list all lookup files in lookups/ directory", function () {
      const confPath = path.join(testAppDir, "default", "props.conf");
      const files = crossFileValidator.getAvailableLookupFiles(confPath);

      expect(files).to.include("users.csv");
    });

    it("should return empty array when no lookups/ directory", function () {
      const noLookupsApp = path.join(os.tmpdir(), "no_lookups_" + Date.now());
      fs.mkdirSync(path.join(noLookupsApp, "default"), { recursive: true });

      const confPath = path.join(noLookupsApp, "default", "props.conf");
      const files = crossFileValidator.getAvailableLookupFiles(confPath);

      expect(files).to.be.an("array").that.is.empty;

      // Cleanup
      fs.rmSync(noLookupsApp, { recursive: true, force: true });
    });
  });

  describe("findOrphanedTransforms()", function () {
    it("should detect orphaned stanzas not referenced by props.conf", function () {
      // Create props.conf that only references extract_user
      const propsPath = path.join(testAppDir, "local", "props.conf");
      fs.writeFileSync(
        propsPath,
        `[my_sourcetype]
REPORT-fields = extract_user
`,
      );

      // transforms.conf has extract_user, extract_ip, my_lookup
      // Only extract_user is referenced, so extract_ip and my_lookup are orphans
      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const transformsContent = fs.readFileSync(transformsPath, "utf-8");
      const doc = createMockDocument(transformsPath, transformsContent);

      const diagnostics = crossFileValidator.findOrphanedTransforms(doc);

      // extract_ip and my_lookup should be flagged as orphans
      expect(diagnostics.length).to.be.greaterThanOrEqual(2);

      const orphanNames = diagnostics.map((d) =>
        d.data.stanzaName.toLowerCase(),
      );
      expect(orphanNames).to.include("extract_ip");
      expect(orphanNames).to.include("my_lookup");
    });

    it("should NOT flag referenced stanzas as orphans", function () {
      // Reference all stanzas
      const propsPath = path.join(testAppDir, "local", "props.conf");
      fs.writeFileSync(
        propsPath,
        `[my_sourcetype]
REPORT-a = extract_user
REPORT-b = extract_ip
LOOKUP-c = my_lookup
`,
      );

      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const transformsContent = fs.readFileSync(transformsPath, "utf-8");
      const doc = createMockDocument(transformsPath, transformsContent);

      const diagnostics = crossFileValidator.findOrphanedTransforms(doc);

      // No orphans - all are referenced
      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should skip [default] stanza", function () {
      // Add a [default] stanza to transforms.conf
      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const originalContent = fs.readFileSync(transformsPath, "utf-8");
      fs.writeFileSync(
        transformsPath,
        `[default]
REGEX = .*

${originalContent}`,
      );

      // Empty props.conf - nothing referenced
      const propsPath = path.join(testAppDir, "local", "props.conf");
      fs.writeFileSync(
        propsPath,
        `[my_sourcetype]
# no transform references
`,
      );

      const newContent = fs.readFileSync(transformsPath, "utf-8");
      const doc = createMockDocument(transformsPath, newContent);

      const diagnostics = crossFileValidator.findOrphanedTransforms(doc);

      // [default] should NOT be flagged as orphan
      const orphanNames = diagnostics.map((d) =>
        d.data.stanzaName.toLowerCase(),
      );
      expect(orphanNames).to.not.include("default");

      // Restore original content
      fs.writeFileSync(transformsPath, originalContent);
    });

    it("should apply Unnecessary tag for faded styling", function () {
      const propsPath = path.join(testAppDir, "local", "props.conf");
      fs.writeFileSync(
        propsPath,
        `[my_sourcetype]
# no references
`,
      );

      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const transformsContent = fs.readFileSync(transformsPath, "utf-8");
      const doc = createMockDocument(transformsPath, transformsContent);

      const diagnostics = crossFileValidator.findOrphanedTransforms(doc);

      expect(diagnostics.length).to.be.greaterThan(0);

      // Check that Unnecessary tag is applied
      for (const diag of diagnostics) {
        expect(diag.tags).to.include(mockVscode.DiagnosticTag.Unnecessary);
        expect(diag.severity).to.equal(
          mockVscode.DiagnosticSeverity.Information,
        );
      }
    });

    it("should skip non-transforms.conf files", function () {
      const otherPath = path.join(testAppDir, "local", "props.conf");
      const doc = createMockDocument(otherPath, "[test]\nREGEX = .*\n");

      const diagnostics = crossFileValidator.findOrphanedTransforms(doc);

      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should check both local/ and default/ props.conf for references", function () {
      // Reference in default/props.conf
      fs.writeFileSync(
        path.join(testAppDir, "default", "props.conf"),
        `[sourcetype1]
REPORT-a = extract_user
`,
      );

      // Reference in local/props.conf
      fs.writeFileSync(
        path.join(testAppDir, "local", "props.conf"),
        `[sourcetype2]
REPORT-b = extract_ip
`,
      );

      const transformsPath = path.join(
        testAppDir,
        "default",
        "transforms.conf",
      );
      const transformsContent = fs.readFileSync(transformsPath, "utf-8");
      const doc = createMockDocument(transformsPath, transformsContent);

      const diagnostics = crossFileValidator.findOrphanedTransforms(doc);

      // extract_user and extract_ip are referenced (in different props.conf files)
      // Only my_lookup should be orphaned
      const orphanNames = diagnostics.map((d) =>
        d.data.stanzaName.toLowerCase(),
      );
      expect(orphanNames).to.not.include("extract_user");
      expect(orphanNames).to.not.include("extract_ip");
      expect(orphanNames).to.include("my_lookup");
    });
  });

  describe("validateIndexReferences()", function () {
    before(function () {
      // Create indexes.conf with some custom indexes
      fs.writeFileSync(
        path.join(testAppDir, "default", "indexes.conf"),
        `[custom_index]
homePath = $SPLUNK_DB/custom_index/db
coldPath = $SPLUNK_DB/custom_index/colddb
thawedPath = $SPLUNK_DB/custom_index/thaweddb

[app_logs]
homePath = $SPLUNK_DB/app_logs/db
coldPath = $SPLUNK_DB/app_logs/colddb
thawedPath = $SPLUNK_DB/app_logs/thaweddb
`,
      );
    });

    it("should return no diagnostics for built-in indexes", function () {
      const inputsPath = path.join(testAppDir, "local", "inputs.conf");
      const inputsContent = `[monitor:///var/log/messages]
index = main

[monitor:///var/log/audit]
index = _audit
`;
      const doc = createMockDocument(inputsPath, inputsContent);

      const diagnostics = crossFileValidator.validateIndexReferences(doc);

      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should return no diagnostics for custom indexes defined in indexes.conf", function () {
      const inputsPath = path.join(testAppDir, "local", "inputs.conf");
      const inputsContent = `[monitor:///var/log/app.log]
index = custom_index

[monitor:///var/log/app2.log]
index = app_logs
`;
      const doc = createMockDocument(inputsPath, inputsContent);

      const diagnostics = crossFileValidator.validateIndexReferences(doc);

      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should detect missing index", function () {
      const inputsPath = path.join(testAppDir, "local", "inputs.conf");
      const inputsContent = `[monitor:///var/log/app.log]
index = nonexistent_index
`;
      const doc = createMockDocument(inputsPath, inputsContent);

      const diagnostics = crossFileValidator.validateIndexReferences(doc);

      expect(diagnostics).to.have.lengthOf(1);
      expect(diagnostics[0].message).to.include("nonexistent_index");
      expect(diagnostics[0].message).to.include("not found");
      expect(diagnostics[0].code).to.equal("missing-index");
    });

    it("should validate index in props.conf", function () {
      const propsPath = path.join(testAppDir, "local", "props.conf");
      const propsContent = `[my_sourcetype]
index = missing_props_index
`;
      const doc = createMockDocument(propsPath, propsContent);

      const diagnostics = crossFileValidator.validateIndexReferences(doc);

      expect(diagnostics).to.have.lengthOf(1);
      expect(diagnostics[0].message).to.include("missing_props_index");
    });

    it("should be case-insensitive for index matching", function () {
      const inputsPath = path.join(testAppDir, "local", "inputs.conf");
      const inputsContent = `[monitor:///var/log/app.log]
index = CUSTOM_INDEX
`;
      const doc = createMockDocument(inputsPath, inputsContent);

      const diagnostics = crossFileValidator.validateIndexReferences(doc);

      // custom_index exists, CUSTOM_INDEX should match
      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should skip non-inputs/props.conf files", function () {
      const otherPath = path.join(testAppDir, "local", "transforms.conf");
      const doc = createMockDocument(
        otherPath,
        `[test]
index = whatever
`,
      );

      const diagnostics = crossFileValidator.validateIndexReferences(doc);

      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should include available indexes in diagnostic data", function () {
      const inputsPath = path.join(testAppDir, "local", "inputs.conf");
      const inputsContent = `[monitor:///var/log/app.log]
index = missing_index
`;
      const doc = createMockDocument(inputsPath, inputsContent);

      const diagnostics = crossFileValidator.validateIndexReferences(doc);

      expect(diagnostics).to.have.lengthOf(1);
      expect(diagnostics[0].data).to.exist;
      expect(diagnostics[0].data.availableIndexes).to.include("custom_index");
      expect(diagnostics[0].data.availableIndexes).to.include("app_logs");
    });

    it("should skip comment lines", function () {
      const inputsPath = path.join(testAppDir, "local", "inputs.conf");
      const inputsContent = `[monitor:///var/log/app.log]
# index = nonexistent_index
index = main
`;
      const doc = createMockDocument(inputsPath, inputsContent);

      const diagnostics = crossFileValidator.validateIndexReferences(doc);

      expect(diagnostics).to.be.an("array").that.is.empty;
    });
  });

  describe("getAvailableIndexes()", function () {
    it("should return indexes from indexes.conf", function () {
      const confPath = path.join(testAppDir, "local", "inputs.conf");
      const indexes = crossFileValidator.getAvailableIndexes(confPath);

      expect(indexes.has("custom_index")).to.be.true;
      expect(indexes.has("app_logs")).to.be.true;
    });

    it("should not include volume: or provider: stanzas", function () {
      // Add volume and provider stanzas
      const indexesPath = path.join(testAppDir, "default", "indexes.conf");
      const originalContent = fs.readFileSync(indexesPath, "utf-8");
      fs.writeFileSync(
        indexesPath,
        `${originalContent}

[volume:primary]
path = /opt/splunk/var/lib/splunk

[provider:aws_s3]
vix.command = splunk-vix
`,
      );

      const confPath = path.join(testAppDir, "local", "inputs.conf");
      const indexes = crossFileValidator.getAvailableIndexes(confPath);

      expect(indexes.has("volume:primary")).to.be.false;
      expect(indexes.has("provider:aws_s3")).to.be.false;

      // Restore
      fs.writeFileSync(indexesPath, originalContent);
    });
  });

  describe("validateSourcetypeConsistency()", function () {
    before(function () {
      // Create props.conf with some sourcetype definitions
      fs.writeFileSync(
        path.join(testAppDir, "default", "props.conf"),
        `[my_app_logs]
TIME_FORMAT = %Y-%m-%d %H:%M:%S
LINE_BREAKER = ([\\r\\n]+)

[custom_sourcetype]
SHOULD_LINEMERGE = false

[source::/var/log/special.log]
sourcetype = special_logs
`,
      );
    });

    it("should return no diagnostics when sourcetype is defined in props.conf", function () {
      const inputsPath = path.join(testAppDir, "local", "inputs.conf");
      const inputsContent = `[monitor:///var/log/app.log]
sourcetype = my_app_logs
`;
      const doc = createMockDocument(inputsPath, inputsContent);

      const diagnostics = crossFileValidator.validateSourcetypeConsistency(doc);

      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should detect missing sourcetype definition", function () {
      const inputsPath = path.join(testAppDir, "local", "inputs.conf");
      const inputsContent = `[monitor:///var/log/app.log]
sourcetype = undefined_sourcetype
`;
      const doc = createMockDocument(inputsPath, inputsContent);

      const diagnostics = crossFileValidator.validateSourcetypeConsistency(doc);

      expect(diagnostics).to.have.lengthOf(1);
      expect(diagnostics[0].message).to.include("undefined_sourcetype");
      expect(diagnostics[0].message).to.include("no definition in props.conf");
      expect(diagnostics[0].code).to.equal("missing-sourcetype-definition");
      expect(diagnostics[0].severity).to.equal(
        mockVscode.DiagnosticSeverity.Information,
      );
    });

    it("should NOT flag built-in sourcetypes", function () {
      const inputsPath = path.join(testAppDir, "local", "inputs.conf");
      const inputsContent = `[monitor:///var/log/syslog]
sourcetype = syslog

[monitor:///var/log/access.log]
sourcetype = access_combined

[monitor:///var/log/app.json]
sourcetype = json
`;
      const doc = createMockDocument(inputsPath, inputsContent);

      const diagnostics = crossFileValidator.validateSourcetypeConsistency(doc);

      // Built-in sourcetypes should not trigger diagnostics
      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should NOT flag splunk_* pattern sourcetypes", function () {
      const inputsPath = path.join(testAppDir, "local", "inputs.conf");
      const inputsContent = `[monitor:///opt/splunk/var/log/splunk/metrics.log]
sourcetype = splunk_metrics
`;
      const doc = createMockDocument(inputsPath, inputsContent);

      const diagnostics = crossFileValidator.validateSourcetypeConsistency(doc);

      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should be case-insensitive for sourcetype matching", function () {
      const inputsPath = path.join(testAppDir, "local", "inputs.conf");
      const inputsContent = `[monitor:///var/log/app.log]
sourcetype = MY_APP_LOGS
`;
      const doc = createMockDocument(inputsPath, inputsContent);

      const diagnostics = crossFileValidator.validateSourcetypeConsistency(doc);

      // my_app_logs exists in props.conf, MY_APP_LOGS should match
      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should skip non-inputs.conf files", function () {
      const otherPath = path.join(testAppDir, "local", "props.conf");
      const doc = createMockDocument(
        otherPath,
        `[monitor:///var/log/app.log]
sourcetype = undefined_sourcetype
`,
      );

      const diagnostics = crossFileValidator.validateSourcetypeConsistency(doc);

      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should skip comment lines", function () {
      const inputsPath = path.join(testAppDir, "local", "inputs.conf");
      const inputsContent = `[monitor:///var/log/app.log]
# sourcetype = undefined_sourcetype
sourcetype = my_app_logs
`;
      const doc = createMockDocument(inputsPath, inputsContent);

      const diagnostics = crossFileValidator.validateSourcetypeConsistency(doc);

      expect(diagnostics).to.be.an("array").that.is.empty;
    });

    it("should detect multiple missing sourcetypes", function () {
      const inputsPath = path.join(testAppDir, "local", "inputs.conf");
      const inputsContent = `[monitor:///var/log/app1.log]
sourcetype = missing_type_1

[monitor:///var/log/app2.log]
sourcetype = my_app_logs

[monitor:///var/log/app3.log]
sourcetype = missing_type_2
`;
      const doc = createMockDocument(inputsPath, inputsContent);

      const diagnostics = crossFileValidator.validateSourcetypeConsistency(doc);

      expect(diagnostics).to.have.lengthOf(2);
      const names = diagnostics.map((d) => d.data.sourcetypeName);
      expect(names).to.include("missing_type_1");
      expect(names).to.include("missing_type_2");
    });

    it("should include defined sourcetypes in diagnostic data", function () {
      const inputsPath = path.join(testAppDir, "local", "inputs.conf");
      const inputsContent = `[monitor:///var/log/app.log]
sourcetype = missing_sourcetype
`;
      const doc = createMockDocument(inputsPath, inputsContent);

      const diagnostics = crossFileValidator.validateSourcetypeConsistency(doc);

      expect(diagnostics).to.have.lengthOf(1);
      expect(diagnostics[0].data.definedSourcetypes).to.include("my_app_logs");
      expect(diagnostics[0].data.definedSourcetypes).to.include(
        "custom_sourcetype",
      );
    });
  });

  describe("getDefinedSourcetypes()", function () {
    it("should return sourcetypes from props.conf", function () {
      const confPath = path.join(testAppDir, "local", "inputs.conf");
      const sourcetypes = crossFileValidator.getDefinedSourcetypes(confPath);

      expect(sourcetypes.has("my_app_logs")).to.be.true;
      expect(sourcetypes.has("custom_sourcetype")).to.be.true;
    });

    it("should NOT include source:: stanzas", function () {
      const confPath = path.join(testAppDir, "local", "inputs.conf");
      const sourcetypes = crossFileValidator.getDefinedSourcetypes(confPath);

      expect(sourcetypes.has("source::/var/log/special.log")).to.be.false;
    });

    it("should NOT include default stanza", function () {
      // Add default stanza
      const propsPath = path.join(testAppDir, "default", "props.conf");
      const originalContent = fs.readFileSync(propsPath, "utf-8");
      fs.writeFileSync(
        propsPath,
        `[default]
SHOULD_LINEMERGE = true

${originalContent}`,
      );

      const confPath = path.join(testAppDir, "local", "inputs.conf");
      const sourcetypes = crossFileValidator.getDefinedSourcetypes(confPath);

      expect(sourcetypes.has("default")).to.be.false;

      // Restore
      fs.writeFileSync(propsPath, originalContent);
    });
  });
});
