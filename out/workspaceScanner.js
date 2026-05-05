"use strict";
/**
 * Workspace Scanner for Cross-File Validation
 *
 * This module helps find related Splunk configuration files within an app's
 * directory structure. Splunk apps have a predictable layout:
 *
 *   my_app/
 *   ├── default/     <- App developer edits (ships with app)
 *   │   ├── props.conf
 *   │   └── transforms.conf
 *   ├── local/       <- Admin/user edits (local customizations)
 *   │   ├── props.conf
 *   │   └── transforms.conf
 *   └── lookups/     <- Lookup table CSV files
 *       └── users.csv
 *
 * Key concept: Splunk MERGES local/ over default/ at runtime.
 * So when validating references, we need to check both directories.
 */

const path = require("path");
const fs = require("fs");
const vscode = require("vscode");

/**
 * Determines the Splunk app root directory from a conf file path.
 *
 * Example:
 *   Input:  /opt/splunk/etc/apps/my_app/local/props.conf
 *   Output: /opt/splunk/etc/apps/my_app
 *
 * We look for the parent of 'default/' or 'local/' directory.
 * If neither exists, we assume the conf file is at app root.
 *
 * @param {string} confPath - Full path to a .conf file
 * @returns {string|null} - App root directory, or null if can't determine
 */
function getAppDirectory(confPath) {
  const dir = path.dirname(confPath);
  const dirName = path.basename(dir);

  // If we're in default/ or local/, go up one level
  if (dirName === "default" || dirName === "local") {
    return path.dirname(dir);
  }

  // Otherwise, assume conf file is at app root (unusual but possible)
  return dir;
}

/**
 * Determines which layer (default/local) a conf file is in.
 *
 * This matters because:
 * - If editing default/, only look in default/ (app developer mode)
 * - If editing local/, check local/ first, then fall back to default/
 *
 * @param {string} confPath - Full path to a .conf file
 * @returns {"default"|"local"|"root"} - The layer this file is in
 */
function getConfLayer(confPath) {
  const dir = path.dirname(confPath);
  const dirName = path.basename(dir);

  if (dirName === "default") return "default";
  if (dirName === "local") return "local";
  return "root"; // Conf file at app root (non-standard)
}

/**
 * Finds a related conf file (e.g., transforms.conf for props.conf).
 *
 * Respects Splunk's layering:
 * - If source is in default/, only look in default/
 * - If source is in local/, check local/ first, then default/
 *
 * @param {string} sourcePath - Path to the source conf file
 * @param {string} targetFileName - Name of the target file (e.g., "transforms.conf")
 * @returns {string[]} - Array of found paths (may be empty, or have 1-2 entries)
 */
function findRelatedConfFiles(sourcePath, targetFileName) {
  const appDir = getAppDirectory(sourcePath);
  if (!appDir) return [];

  const layer = getConfLayer(sourcePath);
  const found = [];

  if (layer === "default") {
    // App developer mode: only check default/
    const defaultPath = path.join(appDir, "default", targetFileName);
    if (fs.existsSync(defaultPath)) {
      found.push(defaultPath);
    }
  } else if (layer === "local") {
    // Admin/user mode: check local/ first, then default/
    const localPath = path.join(appDir, "local", targetFileName);
    const defaultPath = path.join(appDir, "default", targetFileName);

    if (fs.existsSync(localPath)) {
      found.push(localPath);
    }
    if (fs.existsSync(defaultPath)) {
      found.push(defaultPath);
    }
  } else {
    // Root level: check same directory, then default/ and local/
    const sameDirPath = path.join(appDir, targetFileName);
    const defaultPath = path.join(appDir, "default", targetFileName);
    const localPath = path.join(appDir, "local", targetFileName);

    if (fs.existsSync(sameDirPath)) {
      found.push(sameDirPath);
    }
    if (fs.existsSync(defaultPath)) {
      found.push(defaultPath);
    }
    if (fs.existsSync(localPath)) {
      found.push(localPath);
    }
  }

  return found;
}

/**
 * Finds all conf files of a given type in the workspace.
 *
 * Used for orphan detection: we need to scan ALL props.conf files
 * to see if a transform stanza is referenced anywhere.
 *
 * @param {string} fileName - Name of conf file to find (e.g., "props.conf")
 * @returns {Promise<string[]>} - Array of file paths
 */
async function findAllConfFilesInWorkspace(fileName) {
  const files = [];

  // Use VS Code's workspace API to find files
  const pattern = `**/${fileName}`;
  const uris = await vscode.workspace.findFiles(pattern, "**/node_modules/**");

  for (const uri of uris) {
    files.push(uri.fsPath);
  }

  return files;
}

/**
 * Synchronous version for use in diagnostics (which can't be async).
 * Searches within the app directory only.
 *
 * @param {string} appDir - App root directory
 * @param {string} fileName - Name of conf file to find
 * @returns {string[]} - Array of file paths
 */
function findConfFilesInApp(appDir, fileName) {
  const files = [];
  const searchDirs = ["default", "local"];

  for (const dir of searchDirs) {
    const confPath = path.join(appDir, dir, fileName);
    if (fs.existsSync(confPath)) {
      files.push(confPath);
    }
  }

  // Also check app root
  const rootPath = path.join(appDir, fileName);
  if (fs.existsSync(rootPath)) {
    files.push(rootPath);
  }

  return files;
}

/**
 * Gets the lookups directory for an app.
 *
 * @param {string} confPath - Path to any conf file in the app
 * @returns {string|null} - Path to lookups/ directory, or null if not found
 */
function getLookupsDirectory(confPath) {
  const appDir = getAppDirectory(confPath);
  if (!appDir) return null;

  const lookupsDir = path.join(appDir, "lookups");
  if (fs.existsSync(lookupsDir)) {
    return lookupsDir;
  }

  return null;
}

/**
 * Gets all possible lookup directories where a lookup file might exist.
 *
 * Splunk searches for lookup files in this order:
 * 1. $SPLUNK_HOME/etc/users/<user>/<app>/lookups/ (user-specific)
 * 2. $SPLUNK_HOME/etc/apps/<app>/local/lookups/ (app local)
 * 3. $SPLUNK_HOME/etc/apps/<app>/lookups/ (app default)
 * 4. $SPLUNK_HOME/etc/system/local/lookups/ (system local)
 * 5. $SPLUNK_HOME/etc/system/default/lookups/ (system default)
 *
 * @param {string} confPath - Path to any conf file in the app
 * @param {string|null} splunkHome - Optional SPLUNK_HOME path
 * @param {string|null} currentUser - Optional current Splunk user
 * @returns {string[]} - Array of lookup directories to search (in priority order)
 */
function getAllLookupDirectories(
  confPath,
  splunkHome = null,
  currentUser = null,
) {
  const lookupDirs = [];
  const appDir = getAppDirectory(confPath);
  const appName = appDir ? path.basename(appDir) : null;

  // 1. User-specific lookups (if SPLUNK_HOME and user are known)
  if (splunkHome && currentUser && appName) {
    const userLookups = path.join(
      splunkHome,
      "etc",
      "users",
      currentUser,
      appName,
      "lookups",
    );
    if (fs.existsSync(userLookups)) {
      lookupDirs.push(userLookups);
    }
  }

  // 2. App local lookups
  if (appDir) {
    const appLocalLookups = path.join(appDir, "local", "lookups");
    if (fs.existsSync(appLocalLookups)) {
      lookupDirs.push(appLocalLookups);
    }
  }

  // 3. App default lookups (most common location)
  if (appDir) {
    const appLookups = path.join(appDir, "lookups");
    if (fs.existsSync(appLookups)) {
      lookupDirs.push(appLookups);
    }
  }

  // 4. System local lookups
  if (splunkHome) {
    const systemLocalLookups = path.join(
      splunkHome,
      "etc",
      "system",
      "local",
      "lookups",
    );
    if (fs.existsSync(systemLocalLookups)) {
      lookupDirs.push(systemLocalLookups);
    }
  }

  // 5. System default lookups
  if (splunkHome) {
    const systemDefaultLookups = path.join(
      splunkHome,
      "etc",
      "system",
      "default",
      "lookups",
    );
    if (fs.existsSync(systemDefaultLookups)) {
      lookupDirs.push(systemDefaultLookups);
    }
  }

  return lookupDirs;
}

/**
 * Searches for a lookup file across all possible lookup directories.
 *
 * @param {string} filename - The lookup filename to find
 * @param {string} confPath - Path to any conf file in the app
 * @param {string|null} splunkHome - Optional SPLUNK_HOME path
 * @param {string|null} currentUser - Optional current Splunk user
 * @returns {{found: boolean, path: string|null, searchedDirs: string[]}}
 */
function findLookupFile(
  filename,
  confPath,
  splunkHome = null,
  currentUser = null,
) {
  const lookupDirs = getAllLookupDirectories(confPath, splunkHome, currentUser);
  const searchedDirs = [];

  for (const dir of lookupDirs) {
    searchedDirs.push(dir);

    // Check exact filename
    const exactPath = path.join(dir, filename);
    if (fs.existsSync(exactPath)) {
      return { found: true, path: exactPath, searchedDirs };
    }

    // Check for .gz compressed version
    const gzPath = exactPath + ".gz";
    if (fs.existsSync(gzPath)) {
      return { found: true, path: gzPath, searchedDirs };
    }
  }

  return { found: false, path: null, searchedDirs };
}

/**
 * Parses a conf file and returns all stanza names.
 *
 * @param {string} confPath - Path to the conf file
 * @returns {Set<string>} - Set of stanza names (lowercase for case-insensitive matching)
 */
function parseStanzaNames(confPath) {
  const stanzas = new Set();

  if (!fs.existsSync(confPath)) {
    return stanzas;
  }

  const content = fs.readFileSync(confPath, "utf-8");
  const stanzaPattern = /^\[([^\]]+)\]/gm;

  let match;
  while ((match = stanzaPattern.exec(content)) !== null) {
    // Store lowercase for case-insensitive comparison
    stanzas.add(match[1].toLowerCase());
  }

  return stanzas;
}

/**
 * Gets all stanzas from related conf files, respecting layering.
 *
 * For local/ editing: merges stanzas from both local/ and default/
 * For default/ editing: only returns stanzas from default/
 *
 * @param {string} sourcePath - Path to the source conf file
 * @param {string} targetFileName - Name of target file (e.g., "transforms.conf")
 * @returns {Set<string>} - Combined set of stanza names
 */
function getMergedStanzas(sourcePath, targetFileName) {
  const relatedFiles = findRelatedConfFiles(sourcePath, targetFileName);
  const allStanzas = new Set();

  for (const filePath of relatedFiles) {
    const stanzas = parseStanzaNames(filePath);
    for (const stanza of stanzas) {
      allStanzas.add(stanza);
    }
  }

  return allStanzas;
}

// Export all functions
module.exports = {
  getAppDirectory,
  getConfLayer,
  findRelatedConfFiles,
  findAllConfFilesInWorkspace,
  findConfFilesInApp,
  getLookupsDirectory,
  getAllLookupDirectories,
  findLookupFile,
  parseStanzaNames,
  getMergedStanzas,
};
