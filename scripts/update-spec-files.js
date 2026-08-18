#!/usr/bin/env node
/**
 * Splunk Spec File Updater
 *
 * This script automates the process of updating Splunk specification files
 * from the jewnix/splunk-spec-files GitHub repository.
 *
 * Features:
 * - Detects current spec file versions in spec_files/
 * - Queries GitHub for available Splunk versions
 * - Downloads spec files for missing versions
 * - Analyzes deprecations and generates semantic rules (Phase 2+)
 *
 * Usage:
 *   node scripts/update-spec-files.js [options]
 *
 * Options:
 *   --check-only      Only check for updates, don't download
 *   --dry-run         Show what would be done without writing files
 *   --version X.Y     Download only a specific version
 *   --verbose         Enable detailed logging
 *   --output-report   Generate markdown report file for PR body
 *   --skip-analysis   Download only, skip deprecation analysis
 */

const fs = require("fs");
const path = require("path");
const https = require("https");

// Configuration
const CONFIG = {
  sourceRepo: "jewnix/splunk-spec-files",
  specFilesDir: path.join(__dirname, "..", "spec_files"),
  githubApiBase: "https://api.github.com",
  githubRawBase: "https://raw.githubusercontent.com",
  versionPattern: /^\d+\.\d+$/,
  tagPattern: /^(\d+)\.(\d+)\.(\d+)$/,
  retryAttempts: 3,
  retryDelayMs: 1000,
  // Minimum version to consider - older versions are EOL
  minVersion: { major: 9, minor: 2 },
};

// CLI argument parsing
const args = process.argv.slice(2);
const options = {
  checkOnly: args.includes("--check-only"),
  dryRun: args.includes("--dry-run"),
  verbose: args.includes("--verbose"),
  outputReport: args.includes("--output-report"),
  skipAnalysis: args.includes("--skip-analysis"),
  analyzeOnly: args.includes("--analyze-only"),
  generateRules: args.includes("--generate-rules"),
  version: null,
};

// Parse --version X.Y
const versionIndex = args.indexOf("--version");
if (versionIndex !== -1 && args[versionIndex + 1]) {
  options.version = args[versionIndex + 1];
}

/**
 * Logger utility with verbose mode support
 */
const log = {
  info: (msg) => console.log(`[INFO] ${msg}`),
  warn: (msg) => console.warn(`[WARN] ${msg}`),
  error: (msg) => console.error(`[ERROR] ${msg}`),
  verbose: (msg) => options.verbose && console.log(`[DEBUG] ${msg}`),
  success: (msg) => console.log(`[OK] ${msg}`),
};

/**
 * Makes an HTTPS request and returns the response body
 * @param {string} url - The URL to fetch
 * @param {object} headers - Optional headers
 * @returns {Promise<{statusCode: number, body: string, headers: object}>}
 */
function httpsGet(url, headers = {}) {
  return new Promise((resolve, reject) => {
    const defaultHeaders = {
      "User-Agent": "vscode-extension-splunk-spec-updater",
      ...headers,
    };

    const urlObj = new URL(url);
    const requestOptions = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: "GET",
      headers: defaultHeaders,
    };

    const req = https.request(requestOptions, (res) => {
      let body = "";
      res.on("data", (chunk) => (body += chunk));
      res.on("end", () => {
        resolve({
          statusCode: res.statusCode,
          body: body,
          headers: res.headers,
        });
      });
    });

    req.on("error", reject);
    req.end();
  });
}

/**
 * Retry wrapper for async functions
 * @param {Function} fn - Async function to retry
 * @param {number} attempts - Number of attempts
 * @param {number} delayMs - Delay between attempts
 */
async function withRetry(
  fn,
  attempts = CONFIG.retryAttempts,
  delayMs = CONFIG.retryDelayMs,
) {
  let lastError;
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (i < attempts - 1) {
        log.verbose(`Attempt ${i + 1} failed, retrying in ${delayMs}ms...`);
        await new Promise((resolve) => setTimeout(resolve, delayMs));
        delayMs *= 2; // Exponential backoff
      }
    }
  }
  throw lastError;
}

/**
 * Scans the spec_files directory and returns existing version directories
 * @returns {string[]} Array of version strings (e.g., ["7.3", "8.0", "9.2"])
 */
function getCurrentVersions() {
  log.verbose(`Scanning ${CONFIG.specFilesDir} for existing versions...`);

  if (!fs.existsSync(CONFIG.specFilesDir)) {
    log.warn(`spec_files directory not found at ${CONFIG.specFilesDir}`);
    return [];
  }

  const entries = fs.readdirSync(CONFIG.specFilesDir, { withFileTypes: true });
  const versions = entries
    .filter(
      (entry) => entry.isDirectory() && CONFIG.versionPattern.test(entry.name),
    )
    .map((entry) => entry.name)
    .sort((a, b) => {
      const [aMajor, aMinor] = a.split(".").map(Number);
      const [bMajor, bMinor] = b.split(".").map(Number);
      return aMajor - bMajor || aMinor - bMinor;
    });

  log.verbose(
    `Found ${versions.length} existing versions: ${versions.join(", ")}`,
  );
  return versions;
}

/**
 * Fetches all tags from the jewnix/splunk-spec-files repository
 * @returns {Promise<Array<{name: string, commit: {sha: string}}>>}
 */
async function getAvailableTags() {
  log.verbose("Fetching tags from GitHub API...");

  const allTags = [];
  let page = 1;
  const perPage = 100;

  while (true) {
    const url = `${CONFIG.githubApiBase}/repos/${CONFIG.sourceRepo}/tags?per_page=${perPage}&page=${page}`;
    log.verbose(`Fetching page ${page}: ${url}`);

    const response = await withRetry(() =>
      httpsGet(url, {
        Accept: "application/vnd.github.v3+json",
      }),
    );

    if (response.statusCode === 403) {
      throw new Error(
        "GitHub API rate limit exceeded. Try again later or use a GITHUB_TOKEN.",
      );
    }

    if (response.statusCode !== 200) {
      throw new Error(
        `GitHub API returned status ${response.statusCode}: ${response.body}`,
      );
    }

    const tags = JSON.parse(response.body);
    if (tags.length === 0) break;

    allTags.push(...tags);

    if (tags.length < perPage) break;
    page++;
  }

  log.verbose(`Fetched ${allTags.length} total tags`);
  return allTags;
}

/**
 * Checks if a version meets the minimum version requirement
 * @param {number} major - Major version number
 * @param {number} minor - Minor version number
 * @returns {boolean} True if version >= minVersion
 */
function meetsMinVersion(major, minor) {
  if (major > CONFIG.minVersion.major) return true;
  if (major < CONFIG.minVersion.major) return false;
  return minor >= CONFIG.minVersion.minor;
}

/**
 * Groups tags by major.minor version and finds the latest patch for each
 * Filters out versions below the configured minimum (EOL versions)
 * @param {Array<{name: string}>} tags - Array of tag objects
 * @returns {Map<string, string>} Map of major.minor -> latest full tag
 */
function groupTagsByVersion(tags) {
  const versionMap = new Map();

  for (const tag of tags) {
    const match = tag.name.match(CONFIG.tagPattern);
    if (!match) {
      log.verbose(`Skipping non-semver tag: ${tag.name}`);
      continue;
    }

    const [, major, minor, patch] = match;
    const majorNum = parseInt(major, 10);
    const minorNum = parseInt(minor, 10);
    const patchNum = parseInt(patch, 10);

    // Skip EOL versions
    if (!meetsMinVersion(majorNum, minorNum)) {
      log.verbose(`Skipping EOL version: ${tag.name}`);
      continue;
    }

    const majorMinor = `${major}.${minor}`;

    if (!versionMap.has(majorMinor)) {
      versionMap.set(majorMinor, { tag: tag.name, patch: patchNum });
    } else {
      const current = versionMap.get(majorMinor);
      if (patchNum > current.patch) {
        versionMap.set(majorMinor, { tag: tag.name, patch: patchNum });
      }
    }
  }

  // Convert to simple map of version -> tag
  const result = new Map();
  for (const [version, data] of versionMap) {
    result.set(version, data.tag);
  }

  return result;
}

/**
 * Determines which versions are missing from the local spec_files
 * @param {string[]} currentVersions - Existing local versions
 * @param {Map<string, string>} availableVersions - Available versions from GitHub
 * @returns {Array<{version: string, tag: string}>} Missing versions with their tags
 */
function findMissingVersions(currentVersions, availableVersions) {
  const currentSet = new Set(currentVersions);
  const missing = [];

  for (const [version, tag] of availableVersions) {
    if (!currentSet.has(version)) {
      missing.push({ version, tag });
    }
  }

  // Sort by version
  missing.sort((a, b) => {
    const [aMajor, aMinor] = a.version.split(".").map(Number);
    const [bMajor, bMinor] = b.version.split(".").map(Number);
    return aMajor - bMajor || aMinor - bMinor;
  });

  return missing;
}

/**
 * Fetches the list of .spec files for a given tag
 * @param {string} tag - The git tag to fetch files for
 * @returns {Promise<string[]>} Array of spec file names
 */
async function getSpecFileList(tag) {
  log.verbose(`Fetching file list for tag ${tag}...`);

  const url = `${CONFIG.githubApiBase}/repos/${CONFIG.sourceRepo}/contents?ref=${tag}`;

  const response = await withRetry(() =>
    httpsGet(url, {
      Accept: "application/vnd.github.v3+json",
    }),
  );

  if (response.statusCode !== 200) {
    throw new Error(`Failed to fetch file list: ${response.statusCode}`);
  }

  const files = JSON.parse(response.body);
  const specFiles = files
    .filter((f) => f.type === "file" && f.name.endsWith(".spec"))
    .map((f) => f.name);

  log.verbose(`Found ${specFiles.length} spec files for tag ${tag}`);
  return specFiles;
}

/**
 * Downloads a single spec file from GitHub
 * @param {string} tag - The git tag
 * @param {string} filename - The spec file name
 * @param {string} destDir - Destination directory
 * @returns {Promise<void>}
 */
async function downloadSpecFile(tag, filename, destDir) {
  const url = `${CONFIG.githubRawBase}/${CONFIG.sourceRepo}/${tag}/${filename}`;
  log.verbose(`Downloading ${filename} from ${url}`);

  const response = await withRetry(() => httpsGet(url));

  if (response.statusCode !== 200) {
    throw new Error(`Failed to download ${filename}: ${response.statusCode}`);
  }

  const destPath = path.join(destDir, filename);

  if (!options.dryRun) {
    fs.writeFileSync(destPath, response.body, "utf-8");
  }

  log.verbose(`Saved ${filename} to ${destPath}`);
}

/**
 * Downloads all spec files for a version
 * @param {string} tag - The git tag
 * @param {string} version - The major.minor version
 * @returns {Promise<{downloaded: number, failed: string[]}>}
 */
async function downloadVersionSpecs(tag, version) {
  const destDir = path.join(CONFIG.specFilesDir, version);

  log.info(`Downloading spec files for version ${version} (tag: ${tag})...`);

  // Create directory
  if (!options.dryRun) {
    if (!fs.existsSync(destDir)) {
      fs.mkdirSync(destDir, { recursive: true });
    }
  }

  // Get file list
  const specFiles = await getSpecFileList(tag);

  if (specFiles.length === 0) {
    log.warn(`No spec files found for tag ${tag}`);
    return { downloaded: 0, failed: [] };
  }

  // Download each file
  let downloaded = 0;
  const failed = [];

  for (const filename of specFiles) {
    try {
      await downloadSpecFile(tag, filename, destDir);
      downloaded++;
    } catch (error) {
      log.error(`Failed to download ${filename}: ${error.message}`);
      failed.push(filename);
    }
  }

  log.success(
    `Downloaded ${downloaded}/${specFiles.length} files for version ${version}`,
  );
  return { downloaded, failed };
}

// ============================================================================
// PHASE 2: Deprecation Analysis
// ============================================================================

/**
 * Regex patterns for parsing spec files
 */
const SPEC_PATTERNS = {
  version: /^#\s+Version\s+(\d+\.\d+\.\d+)/m,
  stanza: /^\[([^\]]+)\]/,
  setting: /^([a-zA-Z_][\w.<>-]*)\s*=\s*(.+)$/,
  comment: /^#/,
  deprecated: /DEPRECATED/i,
  // Match: "DEPRECATED. Use 'settingName'" or "DEPRECATED; use 'settingName'"
  deprecatedUse: /DEPRECATED[.;]?\s*[Uu]se\s+['`"]([a-zA-Z_][\w.]+)['`"]/i,
  // Match: "replaced by 'settingName'" or "use 'settingName' instead"
  replacedBy:
    /(?:replaced by|use)\s+['`"]([a-zA-Z_][\w.]+)['`"]\s*(?:instead)?/i,
  removed: /(?:removed|no longer supported|will be removed|do not use)/i,
};

/**
 * Parses a spec file into a structured format
 * @param {string} filePath - Path to the spec file
 * @returns {object} Parsed spec file structure
 */
function parseSpecFile(filePath) {
  const content = fs.readFileSync(filePath, "utf-8");
  const lines = content.split(/\r?\n/);
  const fileName = path.basename(filePath);

  const result = {
    fileName,
    filePath,
    version: null,
    settings: new Map(), // Map of settingName -> { value, docString, stanza, lineNumber }
  };

  // Extract version
  const versionMatch = content.match(SPEC_PATTERNS.version);
  if (versionMatch) {
    result.version = versionMatch[1];
  }

  let currentStanza = "default";
  let currentSetting = null;
  let currentDocString = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const lineNumber = i + 1;

    // Check for stanza
    const stanzaMatch = line.match(SPEC_PATTERNS.stanza);
    if (stanzaMatch) {
      // Save previous setting if exists
      if (currentSetting) {
        saveSetting(result.settings, currentSetting, currentDocString);
        currentSetting = null;
        currentDocString = [];
      }
      currentStanza = stanzaMatch[1];
      continue;
    }

    // Check for setting definition
    const settingMatch = line.match(SPEC_PATTERNS.setting);
    if (settingMatch) {
      // Save previous setting if exists
      if (currentSetting) {
        saveSetting(result.settings, currentSetting, currentDocString);
      }

      currentSetting = {
        name: settingMatch[1],
        value: settingMatch[2].trim(),
        stanza: currentStanza,
        lineNumber,
      };
      currentDocString = [];
      continue;
    }

    // Accumulate doc string lines (lines starting with * after a setting)
    if (currentSetting && line.startsWith("*")) {
      currentDocString.push(line);
    }
  }

  // Save last setting
  if (currentSetting) {
    saveSetting(result.settings, currentSetting, currentDocString);
  }

  return result;
}

/**
 * Helper to save a setting with its docstring
 */
function saveSetting(settingsMap, setting, docStringLines) {
  const docString = docStringLines.join("\n");
  const key = `${setting.stanza}::${setting.name}`;

  settingsMap.set(key, {
    name: setting.name,
    value: setting.value,
    stanza: setting.stanza,
    lineNumber: setting.lineNumber,
    docString,
    isDeprecated: SPEC_PATTERNS.deprecated.test(docString),
  });
}

/**
 * Compares two parsed spec files and identifies changes
 * @param {object} oldSpec - Parsed old spec file
 * @param {object} newSpec - Parsed new spec file
 * @returns {object} Comparison results
 */
function compareSpecVersions(oldSpec, newSpec) {
  const changes = {
    added: [],
    removed: [],
    deprecated: [],
    changed: [],
  };

  // Find added and changed settings
  for (const [key, newSetting] of newSpec.settings) {
    const oldSetting = oldSpec.settings.get(key);

    if (!oldSetting) {
      // New setting added
      changes.added.push({
        key,
        setting: newSetting,
      });
    } else {
      // Check if newly deprecated
      if (newSetting.isDeprecated && !oldSetting.isDeprecated) {
        changes.deprecated.push({
          key,
          oldSetting,
          newSetting,
        });
      }

      // Check if value type changed
      if (oldSetting.value !== newSetting.value) {
        changes.changed.push({
          key,
          oldSetting,
          newSetting,
        });
      }
    }
  }

  // Find removed settings
  for (const [key, oldSetting] of oldSpec.settings) {
    if (!newSpec.settings.has(key)) {
      changes.removed.push({
        key,
        setting: oldSetting,
      });
    }
  }

  return changes;
}

/**
 * Classifies a deprecation into categories
 * @param {object} deprecation - Deprecation info from compareSpecVersions
 * @returns {object} Classification result
 */
function classifyDeprecation(deprecation) {
  const { newSetting } = deprecation;
  const docString = newSetting.docString;

  // Try to find replacement setting
  let replacement = null;
  let category = 3; // Default to breaking change

  // Check for "Use X instead" pattern
  const useMatch = docString.match(SPEC_PATTERNS.deprecatedUse);
  if (useMatch) {
    replacement = useMatch[1];
    category = 2; // Replacement with backward compatibility
  }

  // Check for simple rename pattern
  const renameMatch = docString.match(SPEC_PATTERNS.replacedBy);
  if (renameMatch && !useMatch) {
    replacement = renameMatch[1];
    // If the replacement is a simple rename (same stanza, similar name), it's Category 1
    if (
      replacement
        .toLowerCase()
        .includes(newSetting.name.toLowerCase().replace(/[-_]/g, "")) ||
      newSetting.name
        .toLowerCase()
        .includes(replacement.toLowerCase().replace(/[-_]/g, ""))
    ) {
      category = 1; // Simple rename
    } else {
      category = 2;
    }
  }

  // Check for removal pattern
  if (SPEC_PATTERNS.removed.test(docString) && !replacement) {
    category = 3; // Breaking change
  }

  return {
    setting: newSetting.name,
    stanza: newSetting.stanza,
    category,
    replacement,
    docString,
    categoryName: [
      "",
      "simple_rename",
      "replacement_with_overlap",
      "breaking_change",
    ][category],
  };
}

/**
 * Analyzes deprecations between consecutive versions
 * @param {string[]} versions - Sorted array of version strings
 * @returns {object} Analysis results
 */
function analyzeDeprecations(versions) {
  const allDeprecations = {
    category1: [], // Simple renames
    category2: [], // Replacement with backward compatibility
    category3: [], // Breaking changes
  };

  // Compare consecutive versions
  for (let i = 0; i < versions.length - 1; i++) {
    const oldVersion = versions[i];
    const newVersion = versions[i + 1];

    log.verbose(`Comparing ${oldVersion} → ${newVersion}...`);

    const oldDir = path.join(CONFIG.specFilesDir, oldVersion);
    const newDir = path.join(CONFIG.specFilesDir, newVersion);

    if (!fs.existsSync(oldDir) || !fs.existsSync(newDir)) {
      continue;
    }

    // Get spec files in new version
    const specFiles = fs.readdirSync(newDir).filter((f) => f.endsWith(".spec"));

    for (const specFile of specFiles) {
      const oldPath = path.join(oldDir, specFile);
      const newPath = path.join(newDir, specFile);

      if (!fs.existsSync(oldPath)) {
        continue;
      }

      try {
        const oldSpec = parseSpecFile(oldPath);
        const newSpec = parseSpecFile(newPath);
        const changes = compareSpecVersions(oldSpec, newSpec);

        // Classify each deprecation
        for (const dep of changes.deprecated) {
          const classification = classifyDeprecation(dep);
          classification.confFile = specFile;
          classification.fromVersion = oldVersion;
          classification.toVersion = newVersion;

          if (classification.category === 1) {
            allDeprecations.category1.push(classification);
          } else if (classification.category === 2) {
            allDeprecations.category2.push(classification);
          } else {
            allDeprecations.category3.push(classification);
          }
        }
      } catch (error) {
        log.warn(`Error comparing ${specFile}: ${error.message}`);
      }
    }
  }

  return allDeprecations;
}

/**
 * Gets all version directories sorted
 * @returns {string[]} Sorted version strings
 */
function getSortedVersions() {
  const versions = getCurrentVersions();
  return versions.sort((a, b) => {
    const [aMajor, aMinor] = a.split(".").map(Number);
    const [bMajor, bMinor] = b.split(".").map(Number);
    return aMajor - bMajor || aMinor - bMinor;
  });
}

// ============================================================================
// PHASE 3: Auto-Fix & Rule Generation
// ============================================================================

const SEMANTIC_RULES_PATH = path.join(
  __dirname,
  "..",
  "resources",
  "semantic_rules.json",
);

/**
 * Loads the semantic rules JSON file
 * @returns {object} Parsed semantic rules
 */
function loadSemanticRules() {
  const content = fs.readFileSync(SEMANTIC_RULES_PATH, "utf-8");
  return JSON.parse(content);
}

/**
 * Saves the semantic rules JSON file
 * @param {object} rules - The rules object to save
 */
function saveSemanticRules(rules) {
  const content = JSON.stringify(rules, null, 2) + "\n";
  fs.writeFileSync(SEMANTIC_RULES_PATH, content, "utf-8");
}

/**
 * Extracts all setting names used in semantic rules
 * @param {object} rules - The semantic rules object
 * @returns {Set<string>} Set of setting names
 */
function extractSettingsFromRules(rules) {
  const settings = new Set();

  function traverse(obj) {
    if (!obj || typeof obj !== "object") return;

    // Check trigger conditions
    if (obj.settings) {
      Object.keys(obj.settings).forEach((s) => settings.add(s));
    }
    if (obj.with_any) {
      obj.with_any.forEach((s) => settings.add(s));
    }
    if (obj.with_all) {
      obj.with_all.forEach((s) => settings.add(s));
    }
    if (obj.without) {
      obj.without.forEach((s) => settings.add(s));
    }
    if (obj.setting_exists) {
      settings.add(obj.setting_exists);
    }
    if (obj.setting_missing) {
      settings.add(obj.setting_missing);
    }
    if (obj.value_less_than) {
      Object.keys(obj.value_less_than).forEach((s) => settings.add(s));
    }
    if (obj.value_greater_than) {
      Object.keys(obj.value_greater_than).forEach((s) => settings.add(s));
    }

    // Recurse into arrays and objects
    if (Array.isArray(obj)) {
      obj.forEach(traverse);
    } else {
      Object.values(obj).forEach(traverse);
    }
  }

  traverse(rules);
  return settings;
}

/**
 * Applies simple renames (Category 1) to semantic rules
 * @param {object} rules - The semantic rules object
 * @param {Array} renames - Array of Category 1 deprecations
 * @returns {object} Results of the operation
 */
function applySimpleRenames(rules, renames) {
  const results = {
    applied: [],
    skipped: [],
  };

  const rulesStr = JSON.stringify(rules);

  for (const rename of renames) {
    const { setting, replacement } = rename;

    // Check if the old setting is used in rules
    if (!rulesStr.includes(`"${setting}"`)) {
      results.skipped.push({
        ...rename,
        reason: "Setting not found in semantic rules",
      });
      continue;
    }

    // Apply the rename throughout the rules object
    const updatedStr = rulesStr.replace(
      new RegExp(`"${setting}"`, "g"),
      `"${replacement}"`,
    );

    // Parse back and update
    Object.assign(rules, JSON.parse(updatedStr));

    results.applied.push(rename);
    log.info(`  Renamed: ${setting} → ${replacement}`);
  }

  return results;
}

/**
 * Generates a semantic rule for a Category 2 deprecation
 * @param {object} deprecation - The deprecation info
 * @returns {object} Generated rule pattern
 */
function generateSemanticRule(deprecation) {
  const { setting, replacement, confFile, toVersion } = deprecation;
  const confName = confFile.replace(".spec", "");

  // Generate rule for: old setting without new
  const deprecatedRule = {
    id: `${setting.replace(/[.<>]/g, "_")}_deprecated`,
    trigger: {
      setting_exists: setting,
      without: [replacement],
    },
    suggestion: {
      severity: "warning",
      title: `${setting} deprecated in Splunk ${toVersion}+`,
      message: `${setting} is deprecated starting in Splunk ${toVersion}. Add ${replacement} for forward compatibility. When both are set, ${replacement} takes precedence on ${toVersion}+ while ${setting} serves as fallback for older versions.`,
      documentation: `https://docs.splunk.com/Documentation/Splunk/latest/Admin/${confName.charAt(0).toUpperCase() + confName.slice(1)}`,
      deprecated_in: toVersion,
      replacement: replacement,
    },
    fix: {
      type: "add",
      changes: [{ action: "add", setting: replacement, value: "" }],
    },
  };

  // Generate rule for: new setting without old (backward compat warning)
  const backwardCompatRule = {
    id: `${replacement.replace(/[.<>]/g, "_")}_no_fallback`,
    trigger: {
      setting_exists: replacement,
      without: [setting],
    },
    suggestion: {
      severity: "information",
      title: `Consider adding ${setting} for backward compatibility`,
      message: `${replacement} is only recognized in Splunk ${toVersion}+. If your app targets older Splunk versions, add ${setting} as a fallback.`,
      documentation: `https://docs.splunk.com/Documentation/Splunk/latest/Admin/${confName.charAt(0).toUpperCase() + confName.slice(1)}`,
      introduced_in: toVersion,
    },
    fix: {
      type: "add",
      changes: [{ action: "add", setting: setting, value: "" }],
    },
  };

  return { deprecatedRule, backwardCompatRule };
}

/**
 * Inserts generated rules into the semantic rules structure
 * @param {object} rules - The semantic rules object
 * @param {Array} deprecations - Array of Category 2 deprecations
 * @returns {object} Results of the operation
 */
function insertSemanticRules(rules, deprecations) {
  const results = {
    added: [],
    skipped: [],
  };

  // Group deprecations by conf file, deduplicating by setting name
  const byConfFile = new Map();
  for (const dep of deprecations) {
    const confName = dep.confFile.replace(".spec", "");
    if (!byConfFile.has(confName)) {
      byConfFile.set(confName, new Map());
    }
    // Use setting+replacement as key to deduplicate
    const settingKey = `${dep.setting}::${dep.replacement}`;
    if (!byConfFile.get(confName).has(settingKey)) {
      byConfFile.get(confName).set(settingKey, dep);
    }
  }

  // Process each conf file
  for (const [confName, depsMap] of byConfFile) {
    // Ensure the conf file section exists
    if (!rules.rules[confName]) {
      rules.rules[confName] = {};
    }

    // Ensure the deprecations category exists
    if (!rules.rules[confName].deprecations) {
      rules.rules[confName].deprecations = {
        description: "Rules for deprecated settings and their replacements",
        patterns: [],
      };
    }

    const patterns = rules.rules[confName].deprecations.patterns;
    const existingIds = new Set(patterns.map((p) => p.id));

    for (const dep of depsMap.values()) {
      const { deprecatedRule, backwardCompatRule } = generateSemanticRule(dep);

      // Add deprecated rule if not exists
      if (!existingIds.has(deprecatedRule.id)) {
        patterns.push(deprecatedRule);
        results.added.push({
          confFile: confName,
          ruleId: deprecatedRule.id,
          type: "deprecated",
        });
        log.info(`  Added rule: ${deprecatedRule.id}`);
      } else {
        results.skipped.push({
          confFile: confName,
          ruleId: deprecatedRule.id,
          reason: "Rule already exists",
        });
      }

      // Add backward compat rule if not exists
      if (!existingIds.has(backwardCompatRule.id)) {
        patterns.push(backwardCompatRule);
        results.added.push({
          confFile: confName,
          ruleId: backwardCompatRule.id,
          type: "backward_compat",
        });
        log.info(`  Added rule: ${backwardCompatRule.id}`);
      } else {
        results.skipped.push({
          confFile: confName,
          ruleId: backwardCompatRule.id,
          reason: "Rule already exists",
        });
      }
    }
  }

  return results;
}

/**
 * Cross-references deprecations with settings used in semantic rules
 * @param {object} deprecations - Deprecation analysis results
 * @returns {object} Impact analysis
 */
function analyzeImpact(deprecations) {
  const rules = loadSemanticRules();
  const usedSettings = extractSettingsFromRules(rules);

  const impact = {
    affectedSettings: [],
    unaffectedSettings: [],
  };

  const allDeprecations = [
    ...deprecations.category1,
    ...deprecations.category2,
    ...deprecations.category3,
  ];

  for (const dep of allDeprecations) {
    if (usedSettings.has(dep.setting)) {
      impact.affectedSettings.push(dep);
    } else {
      impact.unaffectedSettings.push(dep);
    }
  }

  return impact;
}

// ============================================================================
// PHASE 4: Package.json Version Management
// ============================================================================

const PACKAGE_JSON_PATH = path.join(__dirname, "..", "package.json");

/**
 * Loads the package.json file
 * @returns {object} Parsed package.json
 */
function loadPackageJson() {
  const content = fs.readFileSync(PACKAGE_JSON_PATH, "utf-8");
  return JSON.parse(content);
}

/**
 * Saves the package.json file
 * @param {object} pkg - The package.json object to save
 */
function savePackageJson(pkg) {
  const content = JSON.stringify(pkg, null, 4) + "\n";
  fs.writeFileSync(PACKAGE_JSON_PATH, content, "utf-8");
}

/**
 * Updates the splunk.spec.FileVersion enum and default in package.json
 * Only adds new minor versions (X.Y format), sets newest as default
 * @param {string[]} newVersions - Array of new version strings to add (e.g., ["9.3", "9.4"])
 * @returns {object} Results of the operation
 */
function updatePackageJsonVersions(newVersions) {
  const results = {
    added: [],
    skipped: [],
    newDefault: null,
    previousDefault: null,
  };

  if (newVersions.length === 0) {
    log.verbose("No new versions to add to package.json");
    return results;
  }

  const pkg = loadPackageJson();

  // Navigate to the FileVersion setting
  const fileVersionSetting =
    pkg.contributes?.configuration?.properties?.["splunk.spec.FileVersion"];

  if (!fileVersionSetting) {
    log.error("Could not find splunk.spec.FileVersion in package.json");
    return results;
  }

  const currentEnum = fileVersionSetting.enum || [];
  const currentEnumSet = new Set(currentEnum);
  results.previousDefault = fileVersionSetting.default;

  // Filter to only minor versions (X.Y format) and sort
  const validNewVersions = newVersions
    .filter((v) => CONFIG.versionPattern.test(v))
    .filter((v) => !currentEnumSet.has(v))
    .sort((a, b) => {
      const [aMajor, aMinor] = a.split(".").map(Number);
      const [bMajor, bMinor] = b.split(".").map(Number);
      return aMajor - bMajor || aMinor - bMinor;
    });

  if (validNewVersions.length === 0) {
    log.verbose("All versions already exist in package.json enum");
    return results;
  }

  // Add new versions to enum
  for (const version of validNewVersions) {
    currentEnum.push(version);
    results.added.push(version);
    log.info(`  Added version to enum: ${version}`);
  }

  // Sort the enum by version
  currentEnum.sort((a, b) => {
    const [aMajor, aMinor] = a.split(".").map(Number);
    const [bMajor, bMinor] = b.split(".").map(Number);
    return aMajor - bMajor || aMinor - bMinor;
  });

  fileVersionSetting.enum = currentEnum;

  // Set the newest version as the default
  const newestVersion = currentEnum[currentEnum.length - 1];
  if (newestVersion !== fileVersionSetting.default) {
    fileVersionSetting.default = newestVersion;
    results.newDefault = newestVersion;
    log.info(
      `  Updated default version: ${results.previousDefault} → ${newestVersion}`,
    );
  }

  // Save the updated package.json
  if (!options.dryRun) {
    savePackageJson(pkg);
    log.success(`Updated ${PACKAGE_JSON_PATH}`);
  } else {
    log.info("DRY RUN - package.json not modified");
  }

  return results;
}

/**
 * Sets GitHub Actions output variables
 * @param {string} name - Output name
 * @param {string} value - Output value
 */
function setGitHubOutput(name, value) {
  const outputFile = process.env.GITHUB_OUTPUT;
  if (outputFile) {
    fs.appendFileSync(outputFile, `${name}=${value}\n`);
    log.verbose(`Set GitHub output: ${name}=${value}`);
  }
}

/**
 * Generates a markdown report for the PR body
 * @param {object} results - Update results
 * @returns {string} Markdown report
 */
function generateReport(results) {
  const lines = [
    "## Automated Spec File Update",
    "",
    `**Run Date:** ${new Date().toISOString()}`,
    "",
    "### Versions Added",
    "",
  ];

  if (results.downloaded.length > 0) {
    for (const v of results.downloaded) {
      lines.push(`- **${v.version}** (tag: ${v.tag}) - ${v.fileCount} files`);
    }
  } else {
    lines.push("No new versions downloaded.");
  }

  if (results.failed.length > 0) {
    lines.push("", "### Failed Downloads", "");
    for (const f of results.failed) {
      lines.push(`- ${f.version}: ${f.errors.join(", ")}`);
    }
  }

  // Package.json updates
  if (results.packageJsonUpdated) {
    const pkgResults = results.packageJsonUpdated;
    lines.push("", "### Extension Settings Updated", "");
    if (pkgResults.added.length > 0) {
      lines.push(
        `- Added to \`splunk.spec.FileVersion\` enum: ${pkgResults.added.join(", ")}`,
      );
    }
    if (pkgResults.newDefault) {
      lines.push(
        `- Default version updated: \`${pkgResults.previousDefault}\` → \`${pkgResults.newDefault}\``,
      );
    }
    if (pkgResults.added.length === 0 && !pkgResults.newDefault) {
      lines.push("No changes to package.json settings.");
    }
  }

  lines.push(
    "",
    "### Source",
    `Files downloaded from [jewnix/splunk-spec-files](https://github.com/${CONFIG.sourceRepo})`,
    "",
    "### Checklist",
    "- [ ] Verify spec files are complete",
    "- [ ] Run tests to ensure parsing works",
    "- [ ] Review any new settings/stanzas",
    "- [ ] Verify package.json enum includes all new versions",
    "",
    "---",
    "*This PR was automatically generated by the spec file update workflow.*",
  );

  return lines.join("\n");
}

/**
 * Main entry point
 */
async function main() {
  log.info("Splunk Spec File Updater");
  log.info("========================");

  if (options.dryRun) {
    log.info("DRY RUN MODE - No files will be written");
  }

  // Handle --analyze-only mode
  if (options.analyzeOnly) {
    log.info("Running deprecation analysis on existing spec files...");
    const versions = getSortedVersions();
    log.info(`Analyzing versions: ${versions.join(", ")}`);

    const deprecations = analyzeDeprecations(versions);

    log.info("");
    log.info("=== Deprecation Analysis Results ===");
    log.info(`Category 1 (Simple Renames): ${deprecations.category1.length}`);
    log.info(
      `Category 2 (Replacement with Overlap): ${deprecations.category2.length}`,
    );
    log.info(`Category 3 (Breaking Changes): ${deprecations.category3.length}`);

    if (options.verbose) {
      if (deprecations.category1.length > 0) {
        log.info("");
        log.info("--- Category 1: Simple Renames ---");
        for (const d of deprecations.category1) {
          log.info(
            `  ${d.confFile}: ${d.setting} → ${d.replacement} (${d.fromVersion} → ${d.toVersion})`,
          );
        }
      }
      if (deprecations.category2.length > 0) {
        log.info("");
        log.info("--- Category 2: Replacement with Backward Compatibility ---");
        for (const d of deprecations.category2) {
          log.info(
            `  ${d.confFile}: ${d.setting} → ${d.replacement} (${d.fromVersion} → ${d.toVersion})`,
          );
        }
      }
      if (deprecations.category3.length > 0) {
        log.info("");
        log.info("--- Category 3: Breaking Changes ---");
        for (const d of deprecations.category3) {
          log.info(
            `  ${d.confFile}: ${d.setting} (${d.fromVersion} → ${d.toVersion})`,
          );
        }
      }
    }

    // Output JSON for further processing
    if (options.outputReport) {
      const reportPath = path.join(
        __dirname,
        "..",
        "deprecation-analysis.json",
      );
      if (!options.dryRun) {
        fs.writeFileSync(
          reportPath,
          JSON.stringify(deprecations, null, 2),
          "utf-8",
        );
      }
      log.info(`Analysis written to ${reportPath}`);
    }

    return;
  }

  // Handle --generate-rules mode
  if (options.generateRules) {
    log.info("Generating semantic rules from deprecation analysis...");
    const versions = getSortedVersions();
    const deprecations = analyzeDeprecations(versions);

    // Analyze impact on existing rules
    const impact = analyzeImpact(deprecations);
    log.info("");
    log.info("=== Impact Analysis ===");
    log.info(
      `Settings used in semantic_rules.json that are deprecated: ${impact.affectedSettings.length}`,
    );
    if (options.verbose && impact.affectedSettings.length > 0) {
      for (const s of impact.affectedSettings) {
        log.info(`  - ${s.setting} (${s.confFile})`);
      }
    }

    // Load existing rules
    const rules = loadSemanticRules();

    // Apply Category 1: Simple renames
    log.info("");
    log.info("=== Applying Category 1: Simple Renames ===");
    const renameResults = applySimpleRenames(rules, deprecations.category1);
    log.info(
      `Applied: ${renameResults.applied.length}, Skipped: ${renameResults.skipped.length}`,
    );

    // Apply Category 2: Generate deprecation rules
    log.info("");
    log.info("=== Generating Category 2: Deprecation Rules ===");
    // Filter to only include deprecations from 9.2+ (our minimum supported version)
    const relevantDeprecations = deprecations.category2.filter((d) => {
      const [major, minor] = d.toVersion.split(".").map(Number);
      return major > 9 || (major === 9 && minor >= 2);
    });
    log.info(
      `Processing ${relevantDeprecations.length} relevant deprecations (9.2+)...`,
    );
    const insertResults = insertSemanticRules(rules, relevantDeprecations);
    log.info(
      `Added: ${insertResults.added.length}, Skipped: ${insertResults.skipped.length}`,
    );

    // Save updated rules
    if (!options.dryRun) {
      saveSemanticRules(rules);
      log.success(`Updated ${SEMANTIC_RULES_PATH}`);
    } else {
      log.info("DRY RUN - semantic_rules.json not modified");
    }

    // Summary
    log.info("");
    log.info("=== Summary ===");
    log.info(`Category 1 renames applied: ${renameResults.applied.length}`);
    log.info(`Category 2 rules added: ${insertResults.added.length}`);
    log.info(
      `Category 3 breaking changes (manual review): ${deprecations.category3.length}`,
    );

    return;
  }

  try {
    // Step 1: Get current versions
    log.info("Step 1: Scanning for existing versions...");
    const currentVersions = getCurrentVersions();
    log.info(
      `Found ${currentVersions.length} existing versions: ${currentVersions.join(", ") || "(none)"}`,
    );

    // Step 2: Fetch available tags from GitHub
    log.info("Step 2: Fetching available versions from GitHub...");
    const tags = await getAvailableTags();
    const availableVersions = groupTagsByVersion(tags);
    log.info(`Found ${availableVersions.size} available versions`);

    // Step 3: Determine missing versions
    log.info("Step 3: Determining missing versions...");
    let missingVersions = findMissingVersions(
      currentVersions,
      availableVersions,
    );

    // Filter by specific version if requested
    if (options.version) {
      missingVersions = missingVersions.filter(
        (v) => v.version === options.version,
      );
      if (missingVersions.length === 0) {
        const tag = availableVersions.get(options.version);
        if (tag) {
          missingVersions = [{ version: options.version, tag }];
          log.info(`Forcing download of version ${options.version}`);
        } else {
          log.error(`Version ${options.version} not found in available tags`);
          process.exit(1);
        }
      }
    }

    if (missingVersions.length === 0) {
      log.success("All versions are up to date!");
      setGitHubOutput("has_updates", "false");
      return;
    }

    log.info(
      `Found ${missingVersions.length} missing versions: ${missingVersions.map((v) => v.version).join(", ")}`,
    );
    setGitHubOutput("has_updates", "true");
    setGitHubOutput(
      "versions",
      missingVersions.map((v) => v.version).join(","),
    );

    // Check-only mode stops here
    if (options.checkOnly) {
      log.info("Check-only mode - stopping before download");
      return;
    }

    // Step 4: Download missing versions
    log.info("Step 4: Downloading missing spec files...");
    const results = {
      downloaded: [],
      failed: [],
    };

    for (const { version, tag } of missingVersions) {
      try {
        const { downloaded, failed } = await downloadVersionSpecs(tag, version);
        results.downloaded.push({ version, tag, fileCount: downloaded });
        if (failed.length > 0) {
          results.failed.push({ version, errors: failed });
        }
      } catch (error) {
        log.error(`Failed to download version ${version}: ${error.message}`);
        results.failed.push({ version, errors: [error.message] });
      }
    }

    // Step 5: Update package.json with new versions
    log.info("Step 5: Updating package.json FileVersion enum...");
    const successfulVersions = results.downloaded.map((d) => d.version);
    const pkgResults = updatePackageJsonVersions(successfulVersions);
    results.packageJsonUpdated = pkgResults;

    // Step 6: Generate report if requested
    if (options.outputReport) {
      const report = generateReport(results);
      const reportPath = path.join(__dirname, "..", "spec-update-report.md");
      if (!options.dryRun) {
        fs.writeFileSync(reportPath, report, "utf-8");
      }
      log.info(`Report written to ${reportPath}`);
      setGitHubOutput("report_file", reportPath);
    }

    // Summary
    log.info("");
    log.info("=== Summary ===");
    log.success(`Downloaded: ${results.downloaded.length} versions`);
    if (pkgResults.added.length > 0) {
      log.success(`Added to package.json enum: ${pkgResults.added.join(", ")}`);
    }
    if (pkgResults.newDefault) {
      log.success(`New default version: ${pkgResults.newDefault}`);
    }
    if (results.failed.length > 0) {
      log.warn(`Failed: ${results.failed.length} versions`);
    }

    setGitHubOutput("has_breaking_changes", "false"); // Will be set by Phase 2 analysis
  } catch (error) {
    log.error(`Fatal error: ${error.message}`);
    if (options.verbose) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

// Run main
main();
