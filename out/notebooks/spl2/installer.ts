import axios from 'axios';
import * as child_process from "child_process";
import * as fs from "fs";
import * as path from "path";
import { ExtensionContext, StatusBarItem, workspace } from 'vscode';

// Keys used to store/retrieve state related to this extension
export const configKeyAcceptedTerms = 'splunk.spl2.acceptedTerms';
export const configKeyJavaPath = 'splunk.spl2.javaPath';
export const configKeyLspVersion = 'splunk.spl2.languageServerVersion';
export const configKeyLspUrl = 'splunk.spl2.languageServerUrl';

// Minimum version of Java needed for SPL2 Language Server
const minimumMajorJavaVersion = 17;

export enum TermsAcceptanceStatus {
    DeclinedForever = "declined (forever)",
    DeclinedOnce = "declined (once)",
    Accepted = "accepted",
}

/**
 * Provide a guided install experience for installing Java and SPL2 Language Server including
 * accepting Splunk General terms. If compatible Java and Language Server is already installed
 * this will be a no-op.
 */
export async function getMissingSpl2Requirements(context: ExtensionContext, progressBar: StatusBarItem): Promise<void> {
    return new Promise(async (resolve, reject) => {
        // If the user has already opted-out for good then stop here
        const termsStatus: TermsAcceptanceStatus = workspace.getConfiguration().get(configKeyAcceptedTerms);
        if (termsStatus === TermsAcceptanceStatus.DeclinedForever) {
            reject(
                `User opted out of SPL2. To reset this adjust the '${configKeyAcceptedTerms}' ` +
                `setting to = '${TermsAcceptanceStatus.DeclinedOnce}' in the Splunk Extension Settings.`
            );
            return;
        }
        // Check for compatible Java version installed already
        let javaLoc = workspace.getConfiguration().get(configKeyJavaPath);
        // If java hasn't been set up, check $JAVA_HOME before downloading a JDK
        if (!javaLoc && process.env.JAVA_HOME) {
            let javaHomeBin = path.join(process.env.JAVA_HOME, 'bin', 'java');
            if (isJavaVersionCompatible(javaHomeBin)) {
                javaLoc = javaHomeBin;
                workspace.getConfiguration().update(configKeyJavaPath, javaHomeBin);
            }
        }
        // Setup local storage directory for downloads and installs
        makeLocalStorage(context);
        if (!javaLoc) {
            const jdkDir = path.join(context.globalStorageUri.fsPath, "spl2", "jdk");
            await installJDK(jdkDir, progressBar);
        }

        // Check workspace for current installed LSP version
        let lspVersion = workspace.getConfiguration().get(configKeyLspVersion);
        if (!lspVersion) {
            // If we haven't set up a Language Server version prompt use to accept terms
            // and also install java if needed

            const lspUrl = workspace.getConfiguration().get(configKeyLspUrl);

        } else if (!javaLoc) {
            // If only java is needed simply install this in the background, no terms are needed

            // TODO install java
        }
        // Check to see LSP version exists on disk
        // If LSP but no Java prompt for install
        // If no LSP and no Java ask to accept terms and install both
        // Record acceptance or denying of terms
        // If accept
        //   a) download and unpack JDK and update workspace config with location
        //   b) download and unpack LSP and update workspace config with installedLSPVersion
        reject('getMissingSpl2Requirements not implemented');
    });
}

/**
 * Helper function to run 'java -version' and parse the result to check if it
 * meets out minimum Java major version
 * @param javaLoc Location of java executable (e.g. value of $JAVA_HOME) 
 * @returns true if running `java -version` returns a `version "X.Y.Z"` where X
 *          meets out minimum Java major version
 */
function isJavaVersionCompatible(javaLoc: string): boolean {
    const javaVerCmd = child_process.spawnSync(javaLoc, ['-version'], { encoding : 'utf8' });
    if (!javaVerCmd || javaVerCmd.stdout) {
        return false;
    }
    // java -version actually writes to stderr so check for a match there
    const match = javaVerCmd.stderr.toString().match(/version \"([0-9]+)\.[0-9]+\.[0-9]\"/m);
    return (match && match.length > 1 && (parseInt(match[1]) >= minimumMajorJavaVersion));
}

/**
 * Create the local storage directory struture for storing SPL2 artifacts
 * if they haven't already been created
 */
function makeLocalStorage(context: ExtensionContext): void {
    // We are guaranteed to have read/write access to this directory
    const localSplunkArtifacts = context.globalStorageUri.fsPath;
    // Create this directory structure:
    // .../User/globalStorage/splunk.splunk
    // └── spl2
    //     ├── jdk
    //     └── lsp
    if (!fs.existsSync(localSplunkArtifacts)) {
        fs.mkdirSync(localSplunkArtifacts);
    }
    const spl2Artifacts = path.join(localSplunkArtifacts, "spl2");
    if (!fs.existsSync(spl2Artifacts)) {
        fs.mkdirSync(spl2Artifacts);
    }
    const jdkArtifacts = path.join(spl2Artifacts, "jdk");
    if (!fs.existsSync(jdkArtifacts)) {
        fs.mkdirSync(jdkArtifacts);
    }
    const lspArtifacts = path.join(spl2Artifacts, "lsp");
    if (!fs.existsSync(lspArtifacts)) {
        fs.mkdirSync(lspArtifacts);
    }
}

/**
 * Helper function to install appropriate JDK to run the SPL2 Language Server
 * @param installDir Local directory file path to write JDK to
 */
async function installJDK(installDir: string, progressBar: StatusBarItem): Promise<void> {
    let arch = '';
    let os = '';
    let ext = 'tar.gz';
    // Determine architecture
    switch(process.arch) {
        case 'x64':
            arch = process.arch;
            break;
        case 'arm64':
            arch = 'aarch64';
            break;
        default:
            throw new Error(
                `No JDK found for architecture: '${process.arch}'. To continue ` +
                `install a Java ${minimumMajorJavaVersion} or later JDK and configure ` +
                `the location in the Splunk Extension Settings under '${configKeyJavaPath}'.`
            );
    }
    // Determine OS/extension
    switch(process.platform) {
        case 'darwin':
            os = 'macos';
            break;
        case 'win32':
            os = 'windows';
            ext = 'zip';
            break;
        default:
            os = 'linux';
    }
    
    const filename = `amazon-corretto-${minimumMajorJavaVersion}-${arch}-${os}-jdk.${ext}`;
    const url = `https://corretto.aws/downloads/latest/${filename}`;
    // Download to installDir
    const downloadedArchive = path.join(installDir, filename);
    const fileWriter = fs.createWriteStream(downloadedArchive);

    return new Promise(async (resolve, reject) => {
        const { data, headers } = await axios({
            url,
            method: 'GET',
            responseType: 'stream',
        })
        const totalSize = parseInt(headers['content-length']);
        let totalDownloaded = 0;
        let nextUpdate = 1;
        let error;
        progressBar.show();
        data.on('data', (chunk) => {
            totalDownloaded += chunk.length;
            let pct = Math.floor(totalDownloaded * 100 / totalSize);
            if (pct === nextUpdate) {
                progressBar.text = `Downloading JDK ${pct}%`;
                nextUpdate++;
            }
        });
        fileWriter.on('error', (err) => {
            error = err;
            fileWriter.close();
            reject(err);
        });
        fileWriter.on('close', () => {
            if (!error) {
                progressBar.hide();
                resolve();
            }
        });
        data.pipe(fileWriter);
    });
}

/**
 * Checks if the installed SPL2 Language Server version is the latest and prompt for
 * upgrade if not, or automatically upgrade if user has that setting enabled.
 */
export async function getLatestSpl2Release(context: ExtensionContext, progressBar: StatusBarItem): Promise<void> {
    return new Promise((resolve, reject) => {
        // TODO:
        // Get lastChecked date from workspaceState
        // if Date.now() - lastChecked > 1 day then
        //   retrieve 
        //   read metadata.versioning.latest value
        // if latest version > installed version then prompt for download
        // save update preference to workspace.getConfiguration
        // if yes then download and unpack and update workspaceState with installedLSPVersion 
        reject('getLatestSpl2Release not implemented');
    });
}
