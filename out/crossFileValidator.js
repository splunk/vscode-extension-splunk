"use strict";
/**
 * Cross-File Validator for Splunk Configuration Files
 *
 * This module validates references between related conf files:
 * - props.conf → transforms.conf (REPORT, TRANSFORMS, LOOKUP, RULESET)
 * - transforms.conf → lookups/*.csv (filename setting)
 * - props.conf/inputs.conf → indexes.conf (index setting)
 * - inputs.conf → props.conf (sourcetype setting)
 *
 * Phase 2: Transform Reference Validation
 */

const path = require("path");
const fs = require("fs");
const vscode = require("vscode");
const workspaceScanner = require("./workspaceScanner.js");

/**
 * Reference patterns in props.conf that point to transforms.conf stanzas.
 *
 * Each pattern has:
 * - pattern: Regex to match the setting line
 * - type: Human-readable description for error messages
 * - prefix: Optional prefix for special stanza types (e.g., "statsd-dims:")
 *
 * Why these specific patterns?
 * - TRANSFORMS-* : Index-time field extractions (applied during indexing)
 * - REPORT-*     : Search-time field extractions (applied during search)
 * - LOOKUP-*     : Automatic lookup enrichment
 * - RULESET-*    : Event routing/filtering rules
 */
const TRANSFORM_REFERENCE_PATTERNS = [
  {
    pattern: /^TRANSFORMS-[\w-]+\s*=\s*(.+)/i,
    type: "index-time transform",
    description: "Index-time field extraction",
  },
  {
    pattern: /^REPORT-[\w-]+\s*=\s*(.+)/i,
    type: "search-time transform",
    description: "Search-time field extraction",
  },
  {
    pattern: /^LOOKUP-[\w-]+\s*=\s*(\w+)/i,
    type: "lookup",
    description: "Automatic lookup",
  },
  {
    pattern: /^RULESET-[\w-]+\s*=\s*(.+)/i,
    type: "ruleset",
    description: "Event routing ruleset",
  },
  {
    // STATSD-DIM-TRANSFORMS references stanzas like [statsd-dims:my_stanza]
    pattern: /^STATSD-DIM-TRANSFORMS\s*=\s*(.+)/i,
    type: "statsd dimension transform",
    prefix: "statsd-dims:",
    description: "StatsD dimension extraction",
  },
  {
    // METRIC-SCHEMA-TRANSFORMS references stanzas like [metric-schema:my_stanza]
    pattern: /^METRIC-SCHEMA-TRANSFORMS\s*=\s*(.+)/i,
    type: "metric schema transform",
    prefix: "metric-schema:",
    description: "Metric schema definition",
  },
];

/**
 * Validates transform references in a props.conf document.
 *
 * This is the main entry point for Phase 2 validation.
 *
 * @param {vscode.TextDocument} document - The props.conf document being edited
 * @returns {vscode.Diagnostic[]} - Array of diagnostics for missing references
 */
function validateTransformReferences(document) {
  const diagnostics = [];
  const filePath = document.uri.fsPath;

  // Only validate props.conf files
  if (!filePath.endsWith("props.conf")) {
    return diagnostics;
  }

  // Get all available transform stanzas (respects local/default layering)
  const availableStanzas = workspaceScanner.getMergedStanzas(
    filePath,
    "transforms.conf",
  );

  // Also track which transforms.conf files we found (for error messages)
  const transformFiles = workspaceScanner.findRelatedConfFiles(
    filePath,
    "transforms.conf",
  );
  const hasTransformsConf = transformFiles.length > 0;

  // Scan each line for transform references
  for (let lineNum = 0; lineNum < document.lineCount; lineNum++) {
    const lineText = document.lineAt(lineNum).text;

    // Skip comments and empty lines
    if (lineText.trim().startsWith("#") || lineText.trim() === "") {
      continue;
    }

    // Check each reference pattern
    for (const refPattern of TRANSFORM_REFERENCE_PATTERNS) {
      const match = lineText.match(refPattern.pattern);
      if (!match) continue;

      // Extract the stanza name(s) - may be comma-separated
      const stanzaList = match[1];
      const stanzaNames = stanzaList.split(",").map((s) => s.trim());

      // Validate each referenced stanza
      for (const stanzaName of stanzaNames) {
        // Skip empty names (from trailing commas, etc.)
        if (!stanzaName) continue;

        // Build the full stanza name (with prefix if needed)
        const fullStanzaName = refPattern.prefix
          ? `${refPattern.prefix}${stanzaName}`.toLowerCase()
          : stanzaName.toLowerCase();

        // Check if stanza exists
        if (!availableStanzas.has(fullStanzaName)) {
          // Find the position of this stanza name in the line
          const stanzaStart = lineText.indexOf(
            stanzaName,
            lineText.indexOf("="),
          );
          const stanzaEnd = stanzaStart + stanzaName.length;

          const range = new vscode.Range(
            new vscode.Position(lineNum, stanzaStart),
            new vscode.Position(lineNum, stanzaEnd),
          );

          // Build helpful error message
          let message = `Transform stanza '${stanzaName}' not found`;
          if (refPattern.prefix) {
            message = `Transform stanza '[${refPattern.prefix}${stanzaName}]' not found`;
          }

          if (hasTransformsConf) {
            const fileNames = transformFiles.map(
              (f) => path.basename(path.dirname(f)) + "/transforms.conf",
            );
            message += ` in ${fileNames.join(" or ")}`;
          } else {
            message += `. No transforms.conf found in this app.`;
          }

          const diagnostic = new vscode.Diagnostic(
            range,
            message,
            vscode.DiagnosticSeverity.Error,
          );

          // Add metadata for quick fixes and identification
          diagnostic.code = "missing-transform-stanza";
          diagnostic.source = "splunk-crossfile";

          // Store extra data for the CodeActionProvider
          diagnostic.data = {
            stanzaName: stanzaName,
            fullStanzaName: fullStanzaName,
            type: refPattern.type,
            prefix: refPattern.prefix || "",
            transformsConfPath: transformFiles[0] || null,
          };

          diagnostics.push(diagnostic);
        }
      }
    }
  }

  return diagnostics;
}

/**
 * Gets a summary of what transform references exist in a props.conf file.
 * Useful for debugging and understanding the file structure.
 *
 * @param {string} propsPath - Path to props.conf
 * @returns {Object} - Summary of references found
 */
function getTransformReferenceSummary(propsPath) {
  const summary = {
    file: propsPath,
    references: [],
    availableStanzas: [],
  };

  if (!fs.existsSync(propsPath)) {
    return summary;
  }

  const content = fs.readFileSync(propsPath, "utf-8");
  const lines = content.split("\n");

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    for (const refPattern of TRANSFORM_REFERENCE_PATTERNS) {
      const match = line.match(refPattern.pattern);
      if (match) {
        const stanzaNames = match[1]
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean);
        summary.references.push({
          line: i + 1,
          type: refPattern.type,
          stanzas: stanzaNames,
        });
      }
    }
  }

  // Get available stanzas
  const stanzas = workspaceScanner.getMergedStanzas(
    propsPath,
    "transforms.conf",
  );
  summary.availableStanzas = Array.from(stanzas);

  return summary;
}

/**
 * Detects orphaned transform stanzas - stanzas defined in transforms.conf
 * that are not referenced by any props.conf in the same app.
 *
 * Why this matters:
 * - Unused stanzas clutter the config and cause confusion
 * - May indicate a typo in props.conf (reference doesn't match)
 * - Helps during cleanup/refactoring
 *
 * Severity: Information (not an error, just helpful)
 * Visual: Faded/strikethrough styling via DiagnosticTag.Unnecessary
 *
 * @param {vscode.TextDocument} document - The transforms.conf document
 * @returns {vscode.Diagnostic[]} - Array of diagnostics for orphaned stanzas
 */
function findOrphanedTransforms(document) {
  const diagnostics = [];
  const filePath = document.uri.fsPath;

  // Only validate transforms.conf files
  if (!filePath.endsWith("transforms.conf")) {
    return diagnostics;
  }

  const appDir = workspaceScanner.getAppDirectory(filePath);
  if (!appDir) {
    return diagnostics;
  }

  // Step 1: Get all stanzas defined in this transforms.conf
  // We need line numbers, so we parse the document directly
  const definedStanzas = new Map(); // stanzaName -> lineNumber

  for (let lineNum = 0; lineNum < document.lineCount; lineNum++) {
    const lineText = document.lineAt(lineNum).text;
    const match = lineText.match(/^\[([^\]]+)\]/);

    if (match) {
      const stanzaName = match[1].toLowerCase();

      // Skip special stanzas that don't need to be referenced
      if (isSpecialStanza(stanzaName)) {
        continue;
      }

      definedStanzas.set(stanzaName, {
        line: lineNum,
        originalName: match[1], // Preserve original case for display
        fullLineText: lineText,
      });
    }
  }

  // Step 2: Find all props.conf files in this app and collect references
  const referencedStanzas = new Set();
  const propsFiles = workspaceScanner.findConfFilesInApp(appDir, "props.conf");

  for (const propsPath of propsFiles) {
    const references = collectTransformReferences(propsPath);
    for (const ref of references) {
      referencedStanzas.add(ref.toLowerCase());
    }
  }

  // Step 3: Find orphans (defined but not referenced)
  for (const [stanzaName, stanzaInfo] of definedStanzas) {
    if (!referencedStanzas.has(stanzaName)) {
      const range = new vscode.Range(
        new vscode.Position(stanzaInfo.line, 0),
        new vscode.Position(stanzaInfo.line, stanzaInfo.fullLineText.length),
      );

      const diagnostic = new vscode.Diagnostic(
        range,
        `Transform stanza '${stanzaInfo.originalName}' is not referenced by any props.conf in this app`,
        vscode.DiagnosticSeverity.Information,
      );

      diagnostic.code = "orphaned-transform";
      diagnostic.source = "splunk-crossfile";

      // Apply "Unnecessary" tag for faded/strikethrough styling
      diagnostic.tags = [vscode.DiagnosticTag.Unnecessary];

      diagnostic.data = {
        stanzaName: stanzaInfo.originalName,
        appDir: appDir,
      };

      diagnostics.push(diagnostic);
    }
  }

  return diagnostics;
}

/**
 * Checks if a stanza name is a "special" stanza that doesn't need
 * to be explicitly referenced in props.conf.
 *
 * @param {string} stanzaName - Lowercase stanza name
 * @returns {boolean} - True if this is a special stanza
 */
function isSpecialStanza(stanzaName) {
  // Default stanza applies to all
  if (stanzaName === "default") {
    return true;
  }

  // Stanzas with special prefixes are often auto-applied
  const specialPrefixes = [
    "statsd-dims:", // StatsD dimension transforms
    "metric-schema:", // Metric schema transforms
    "syslog-", // Syslog-specific transforms
  ];

  for (const prefix of specialPrefixes) {
    if (stanzaName.startsWith(prefix)) {
      return true;
    }
  }

  return false;
}

/**
 * Collects all transform stanza references from a props.conf file.
 *
 * @param {string} propsPath - Path to props.conf
 * @returns {string[]} - Array of referenced stanza names
 */
function collectTransformReferences(propsPath) {
  const references = [];

  if (!fs.existsSync(propsPath)) {
    return references;
  }

  const content = fs.readFileSync(propsPath, "utf-8");
  const lines = content.split("\n");

  for (const line of lines) {
    // Skip comments
    if (line.trim().startsWith("#")) {
      continue;
    }

    for (const refPattern of TRANSFORM_REFERENCE_PATTERNS) {
      const match = line.match(refPattern.pattern);
      if (match) {
        // Handle comma-separated stanza names
        const stanzaNames = match[1]
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean);

        for (const name of stanzaNames) {
          // Apply prefix if needed
          const fullName = refPattern.prefix
            ? `${refPattern.prefix}${name}`
            : name;
          references.push(fullName);
        }
      }
    }
  }

  return references;
}

/**
 * Validates that lookup files referenced in transforms.conf actually exist.
 *
 * In transforms.conf, lookup stanzas have a `filename` setting:
 *   [my_lookup]
 *   filename = users.csv
 *
 * Splunk searches for lookup files in multiple locations:
 * 1. $SPLUNK_HOME/etc/users/<user>/<app>/lookups/ (user-specific)
 * 2. $SPLUNK_HOME/etc/apps/<app>/local/lookups/ (app local)
 * 3. $SPLUNK_HOME/etc/apps/<app>/lookups/ (app default)
 * 4. $SPLUNK_HOME/etc/system/local/lookups/ (system local)
 * 5. $SPLUNK_HOME/etc/system/default/lookups/ (system default)
 *
 * Supported file types: .csv, .csv.gz, .kmz
 *
 * @param {vscode.TextDocument} document - The transforms.conf document
 * @param {Object} options - Optional configuration
 * @param {string} options.splunkHome - Path to SPLUNK_HOME
 * @param {string} options.currentUser - Current Splunk user
 * @returns {vscode.Diagnostic[]} - Array of diagnostics for missing lookup files
 */
function validateLookupFiles(document, options = {}) {
  const diagnostics = [];
  const filePath = document.uri.fsPath;
  const { splunkHome = null, currentUser = null } = options;

  // Only validate transforms.conf files
  if (!filePath.endsWith("transforms.conf")) {
    return diagnostics;
  }

  // Track current stanza to determine if we're in a lookup stanza
  let currentStanza = null;

  for (let lineNum = 0; lineNum < document.lineCount; lineNum++) {
    const lineText = document.lineAt(lineNum).text;

    // Check for stanza header
    const stanzaMatch = lineText.match(/^\[([^\]]+)\]/);
    if (stanzaMatch) {
      currentStanza = stanzaMatch[1];
      continue;
    }

    // Skip comments and empty lines
    if (lineText.trim().startsWith("#") || lineText.trim() === "") {
      continue;
    }

    // Check for filename setting (indicates this is a lookup stanza)
    const filenameMatch = lineText.match(/^filename\s*=\s*(.+)/i);
    if (filenameMatch) {
      const lookupFilename = filenameMatch[1].trim();

      // Search for the lookup file across all possible locations
      const searchResult = workspaceScanner.findLookupFile(
        lookupFilename,
        filePath,
        splunkHome,
        currentUser,
      );

      if (!searchResult.found) {
        const filenameStart = lineText.indexOf(lookupFilename);
        const range = new vscode.Range(
          new vscode.Position(lineNum, filenameStart),
          new vscode.Position(lineNum, filenameStart + lookupFilename.length),
        );

        // Build helpful message showing where we searched
        let message = `Lookup file '${lookupFilename}' not found`;
        if (searchResult.searchedDirs.length > 0) {
          message += ` in: ${searchResult.searchedDirs.map((d) => path.basename(path.dirname(d)) + "/lookups/").join(", ")}`;
        } else {
          message += `. No lookups/ directories found.`;
        }

        const diagnostic = new vscode.Diagnostic(
          range,
          message,
          vscode.DiagnosticSeverity.Warning,
        );

        // Use different code based on whether any lookup dirs exist
        diagnostic.code =
          searchResult.searchedDirs.length > 0
            ? "missing-lookup-file"
            : "no-lookups-directory";
        diagnostic.source = "splunk-crossfile";

        diagnostic.data = {
          filename: lookupFilename,
          searchedDirs: searchResult.searchedDirs,
          stanzaName: currentStanza,
          splunkHome: splunkHome,
        };

        diagnostics.push(diagnostic);
      }
    }
  }

  return diagnostics;
}

/**
 * Lists all lookup files in an app's lookups/ directory.
 * Useful for autocomplete and validation.
 *
 * @param {string} confPath - Path to any conf file in the app
 * @returns {string[]} - Array of lookup filenames
 */
function getAvailableLookupFiles(confPath) {
  const lookupsDir = workspaceScanner.getLookupsDirectory(confPath);

  if (!lookupsDir || !fs.existsSync(lookupsDir)) {
    return [];
  }

  const files = fs.readdirSync(lookupsDir);

  // Filter to supported lookup file types
  const lookupExtensions = [".csv", ".csv.gz", ".kmz", ".gz"];

  return files.filter((f) => {
    const lower = f.toLowerCase();
    return lookupExtensions.some((ext) => lower.endsWith(ext));
  });
}

/**
 * Built-in Splunk indexes that always exist and don't need validation.
 * These are created by default in every Splunk installation.
 */
const BUILTIN_INDEXES = new Set([
  "main", // Default index for events
  "_internal", // Splunk internal logs
  "_audit", // Audit trail
  "_introspection", // Performance data
  "_telemetry", // Telemetry data
  "_thefishbucket", // File input checkpoints
  "_metrics", // Metrics data (9.0+)
  "_metrics_rollup", // Metrics rollup
  "history", // Search history
  "summary", // Summary indexing
  "splunklogger", // Splunk logger
  "lastchanceindex", // Fallback index
]);

/**
 * Validates that index references in props.conf and inputs.conf exist.
 *
 * Settings that reference indexes:
 * - inputs.conf: index = <name>
 * - props.conf: DEST_KEY = _MetaData:Index (with FORMAT containing index name)
 *
 * @param {vscode.TextDocument} document - The conf document being edited
 * @param {Object} options - Optional configuration
 * @param {string} options.splunkHome - Path to SPLUNK_HOME for system indexes
 * @returns {vscode.Diagnostic[]} - Array of diagnostics for missing indexes
 */
function validateIndexReferences(document, options = {}) {
  const diagnostics = [];
  const filePath = document.uri.fsPath;
  const { splunkHome = null } = options;

  // Only validate inputs.conf and props.conf
  const fileName = path.basename(filePath);
  if (fileName !== "inputs.conf" && fileName !== "props.conf") {
    return diagnostics;
  }

  // Get available indexes from indexes.conf files
  const availableIndexes = getAvailableIndexes(filePath, splunkHome);

  // Add built-in indexes
  for (const builtin of BUILTIN_INDEXES) {
    availableIndexes.add(builtin);
  }

  // Scan for index references
  for (let lineNum = 0; lineNum < document.lineCount; lineNum++) {
    const lineText = document.lineAt(lineNum).text;

    // Skip comments and empty lines
    if (lineText.trim().startsWith("#") || lineText.trim() === "") {
      continue;
    }

    // Check for index = <name> setting
    const indexMatch = lineText.match(/^index\s*=\s*(\S+)/i);
    if (indexMatch) {
      const indexName = indexMatch[1].trim().toLowerCase();

      if (!availableIndexes.has(indexName)) {
        const indexStart = lineText
          .toLowerCase()
          .indexOf(indexMatch[1].toLowerCase());
        const range = new vscode.Range(
          new vscode.Position(lineNum, indexStart),
          new vscode.Position(lineNum, indexStart + indexMatch[1].length),
        );

        const diagnostic = new vscode.Diagnostic(
          range,
          `Index '${indexMatch[1]}' not found in indexes.conf. Data may go to the default index.`,
          vscode.DiagnosticSeverity.Warning,
        );

        diagnostic.code = "missing-index";
        diagnostic.source = "splunk-crossfile";

        diagnostic.data = {
          indexName: indexMatch[1],
          availableIndexes: Array.from(availableIndexes).filter(
            (i) => !i.startsWith("_"),
          ),
        };

        diagnostics.push(diagnostic);
      }
    }
  }

  return diagnostics;
}

/**
 * Gets all available indexes from indexes.conf files.
 *
 * Searches in:
 * 1. Current app's indexes.conf (local/ and default/)
 * 2. System indexes.conf (if SPLUNK_HOME provided)
 *
 * @param {string} confPath - Path to the conf file being validated
 * @param {string|null} splunkHome - Optional SPLUNK_HOME path
 * @returns {Set<string>} - Set of available index names (lowercase)
 */
function getAvailableIndexes(confPath, splunkHome = null) {
  const indexes = new Set();

  // Get indexes from current app
  const appIndexFiles = workspaceScanner.findRelatedConfFiles(
    confPath,
    "indexes.conf",
  );
  for (const indexFile of appIndexFiles) {
    const stanzas = workspaceScanner.parseStanzaNames(indexFile);
    for (const stanza of stanzas) {
      // Index stanzas are just [index_name], skip special stanzas
      if (
        !stanza.startsWith("provider:") &&
        !stanza.startsWith("volume:") &&
        stanza !== "default"
      ) {
        indexes.add(stanza);
      }
    }
  }

  // Get system indexes if SPLUNK_HOME is provided
  if (splunkHome) {
    const systemIndexPaths = [
      path.join(splunkHome, "etc", "system", "local", "indexes.conf"),
      path.join(splunkHome, "etc", "system", "default", "indexes.conf"),
    ];

    for (const indexPath of systemIndexPaths) {
      if (fs.existsSync(indexPath)) {
        const stanzas = workspaceScanner.parseStanzaNames(indexPath);
        for (const stanza of stanzas) {
          if (
            !stanza.startsWith("provider:") &&
            !stanza.startsWith("volume:") &&
            stanza !== "default"
          ) {
            indexes.add(stanza);
          }
        }
      }
    }
  }

  return indexes;
}

/**
 * Validates sourcetype consistency between inputs.conf and props.conf.
 *
 * When inputs.conf defines `sourcetype = X`, there should typically be
 * a corresponding `[X]` stanza in props.conf to define parsing rules.
 *
 * Without a props.conf stanza:
 * - Splunk uses default timestamp extraction
 * - No custom field extractions apply
 * - Line breaking may not work correctly
 *
 * This is an informational check (not an error) since Splunk will still
 * function, but it's a best practice to define sourcetype properties.
 *
 * @param {vscode.TextDocument} document - The inputs.conf document
 * @returns {vscode.Diagnostic[]} - Array of diagnostics for missing sourcetypes
 */
function validateSourcetypeConsistency(document) {
  const diagnostics = [];
  const filePath = document.uri.fsPath;

  // Only validate inputs.conf files
  if (!filePath.endsWith("inputs.conf")) {
    return diagnostics;
  }

  // Step 1: Get all defined sourcetypes from props.conf
  const definedSourcetypes = getDefinedSourcetypes(filePath);

  // Step 2: Scan inputs.conf for sourcetype references
  for (let lineNum = 0; lineNum < document.lineCount; lineNum++) {
    const lineText = document.lineAt(lineNum).text;

    // Skip comments and empty lines
    if (lineText.trim().startsWith("#") || lineText.trim() === "") {
      continue;
    }

    // Check for sourcetype = <name> setting
    const sourcetypeMatch = lineText.match(/^sourcetype\s*=\s*(\S+)/i);
    if (sourcetypeMatch) {
      const sourcetypeName = sourcetypeMatch[1].trim();
      const sourcetypeLower = sourcetypeName.toLowerCase();

      // Step 3: Check if this sourcetype has a props.conf definition
      if (!definedSourcetypes.has(sourcetypeLower)) {
        // Check if it's a built-in or pattern-based sourcetype
        if (!isBuiltinSourcetype(sourcetypeName)) {
          const stStart = lineText.indexOf(
            sourcetypeName,
            lineText.indexOf("="),
          );
          const range = new vscode.Range(
            new vscode.Position(lineNum, stStart),
            new vscode.Position(lineNum, stStart + sourcetypeName.length),
          );

          const diagnostic = new vscode.Diagnostic(
            range,
            `Sourcetype '${sourcetypeName}' has no definition in props.conf. Consider adding a [${sourcetypeName}] stanza to define parsing rules.`,
            vscode.DiagnosticSeverity.Information,
          );

          diagnostic.code = "missing-sourcetype-definition";
          diagnostic.source = "splunk-crossfile";

          diagnostic.data = {
            sourcetypeName: sourcetypeName,
            definedSourcetypes: Array.from(definedSourcetypes).slice(0, 20), // Limit for UI
          };

          diagnostics.push(diagnostic);
        }
      }
    }
  }

  return diagnostics;
}

/**
 * Gets all sourcetype stanzas defined in props.conf files.
 *
 * In props.conf, sourcetypes are defined as simple stanzas like [my_sourcetype].
 * We exclude special stanzas like [source::...], [host::...], [default], etc.
 *
 * @param {string} confPath - Path to the conf file being validated
 * @returns {Set<string>} - Set of defined sourcetype names (lowercase)
 */
function getDefinedSourcetypes(confPath) {
  const sourcetypes = new Set();

  // Get props.conf files from the app
  const propsFiles = workspaceScanner.findRelatedConfFiles(
    confPath,
    "props.conf",
  );

  for (const propsFile of propsFiles) {
    const stanzas = workspaceScanner.parseStanzaNames(propsFile);

    for (const stanza of stanzas) {
      // Handle [sourcetype::name] format - extract the actual sourcetype name
      if (stanza.startsWith("sourcetype::")) {
        const actualName = stanza.substring("sourcetype::".length);
        sourcetypes.add(actualName);
      }
      // Skip other special stanzas - only include simple sourcetype stanzas
      else if (!isSpecialPropsStanza(stanza)) {
        sourcetypes.add(stanza);
      }
    }
  }

  return sourcetypes;
}

/**
 * Checks if a props.conf stanza is a "special" stanza (not a sourcetype).
 *
 * Special stanzas in props.conf:
 * - [default] - applies to all
 * - [source::...] - source-based rules
 * - [host::...] - host-based rules
 * - [rule::...] - routing rules
 * - [delayedrule::...] - delayed routing rules
 *
 * @param {string} stanzaName - The stanza name (lowercase)
 * @returns {boolean} - True if this is a special stanza
 */
function isSpecialPropsStanza(stanzaName) {
  if (stanzaName === "default") return true;

  const specialPrefixes = ["source::", "host::", "rule::", "delayedrule::"];

  return specialPrefixes.some((prefix) => stanzaName.startsWith(prefix));
}

/**
 * Checks if a sourcetype is a Splunk built-in or commonly auto-generated.
 *
 * Built-in sourcetypes don't need props.conf definitions because
 * Splunk already knows how to parse them.
 *
 * @param {string} sourcetype - The sourcetype name
 * @returns {boolean} - True if this is a built-in sourcetype
 */
function isBuiltinSourcetype(sourcetype) {
  const lower = sourcetype.toLowerCase();

  // Common built-in sourcetypes
  const builtins = new Set([
    "syslog",
    "access_combined",
    "access_common",
    "apache_error",
    "linux_messages_syslog",
    "linux_secure",
    "linux_audit",
    "wineventlog",
    "xmlwineventlog",
    "perfmon",
    "script",
    "stash",
    "csv",
    "json",
    "kvstore",
    "mongod",
    "splunkd",
    "splunkd_access",
    "splunk_web_access",
    "splunk_web_service",
    "scheduler",
    "metrics",
    "statsd",
    "collectd_http",
    "generic_single_line",
    "log4j",
    "log4php",
    "too_small",
  ]);

  if (builtins.has(lower)) {
    return true;
  }

  // Pattern-based sourcetypes that are auto-generated
  // e.g., "stash_new", "preprocess-*"
  if (
    lower.startsWith("stash_") ||
    lower.startsWith("preprocess-") ||
    lower.startsWith("splunk_")
  ) {
    return true;
  }

  return false;
}

// Export functions
module.exports = {
  validateTransformReferences,
  findOrphanedTransforms,
  validateLookupFiles,
  validateIndexReferences,
  validateSourcetypeConsistency,
  getTransformReferenceSummary,
  collectTransformReferences,
  getAvailableLookupFiles,
  getAvailableIndexes,
  getDefinedSourcetypes,
  TRANSFORM_REFERENCE_PATTERNS,
  BUILTIN_INDEXES,
};
