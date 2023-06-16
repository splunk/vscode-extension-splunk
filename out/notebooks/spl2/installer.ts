import axios from 'axios';
import * as child_process from 'child_process';
import { XMLParser} from 'fast-xml-parser';
import * as fs from 'fs';
import * as path from 'path';
import { pipeline } from 'stream';
import * as tar from 'tar-fs';
import * as unzipper from 'unzipper';
import * as util from 'util';
import { env, ExtensionContext, StatusBarItem, Uri, window, workspace } from 'vscode';
import * as zlib from 'zlib';

// Keys used to store/retrieve state related to this extension
export const configKeyAcceptedTerms = 'splunk.spl2.acceptedTerms';
export const configKeyJavaPath = 'splunk.spl2.javaPath';
export const configKeyLspVersion = 'splunk.spl2.languageServerVersion';

export const stateKeyLatestLspVersion = 'splunk.spl2.latestLspVersion';
export const stateKeyLastLspCheck = 'splunk.spl2.lastLspCheck';

// Minimum version of Java needed for SPL2 Language Server
const minimumMajorJavaVersion = 17;

export enum TermsAcceptanceStatus {
    DeclinedForever = 'declined (forever)',
    DeclinedOnce = 'declined (once)',
    Accepted = 'accepted',
}

/**
 * Provide a guided install experience for installing Java and SPL2 Language Server including
 * accepting Splunk General terms. If compatible Java and Language Server is already installed
 * this will be a no-op.
 */
export async function getMissingSpl2Requirements(context: ExtensionContext, progressBar: StatusBarItem): Promise<boolean> {
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
        let javaLoc;
        try {
            javaLoc = workspace.getConfiguration().get(configKeyJavaPath);
        } catch (err) {
            reject(`Error retrieving configuration '${configKeyJavaPath}', err: ${err}`);
        }
        // If java hasn't been set up, check $JAVA_HOME before downloading a JDK
        if (!javaLoc && process.env.JAVA_HOME) {
            let javaHomeBin = path.join(process.env.JAVA_HOME, 'bin', 'java');
            if (process.platform === 'win32') {
                javaHomeBin = `${javaHomeBin}.exe`;
            }
            if (isJavaVersionCompatible(javaHomeBin)) {
                javaLoc = javaHomeBin;
                try {
                    workspace.getConfiguration().update(configKeyJavaPath, javaHomeBin, true);
                } catch (err) {
                    reject(`Error updating configuration '${configKeyJavaPath}', err: ${err}`);
                }
            }
        }

        // Check workspace for current installed LSP version
        let lspVersion;
        try {
            lspVersion = workspace.getConfiguration().get(configKeyLspVersion);
        } catch (err) {
            reject(`Error retrieving configuration '${configKeyLspVersion}', err: ${err}`);
        }
        // Setup local storage directory for downloads and installs
        try {
            makeLocalStorage(context);
        } catch (err) {
            reject(`Error creating local artifact storage for SPL2, err: ${err}`);
        }
        
        let installedLatestLsp = false;
        if (!lspVersion) {
            // If we haven't set up a Language Server version prompt use to accept terms
            // and also confirm install of java if needed
            try {
                const accepted = await promptToDownloadLsp(!javaLoc);
                if (!accepted) {
                    return;
                }
                // Remove any existing LSP artifacts first
                const localLspDir = getLocalLspDir(context);
                fs.rmdirSync(localLspDir, { recursive: true });
                makeLocalStorage(context); // recreate directory
            
                await getLatestSpl2Release(context, progressBar);
                installedLatestLsp = true;
            } catch (err) {
                reject(`Error retrieving latest SPL2 release, err: ${err}`);
            }
        } else if (!javaLoc) {
            // Ask user to confirm download, cancel, or opt-out of SPL2 altogether
            try {
                const accepted = await promptToDownloadJava();
                if (!accepted) {
                    return;
                }
            } catch (err) {
                reject(`Error confirming JDK download, err: ${err}`);
            }
        }
        // We already prompted the user to confirm this download, proceed
        if (!javaLoc) {
            // Remove any old artifacts first
            const localJdkDir = path.join(context.globalStorageUri.fsPath, 'spl2', 'jdk');
            try {
                fs.rmdirSync(localJdkDir, { recursive: true });
                makeLocalStorage(context); // recreate directory

                javaLoc = await installJDK(localJdkDir, progressBar);
                workspace.getConfiguration().update(configKeyJavaPath, javaLoc, true);
            } catch (err) {
                reject(`Error installing JDK for SPL2, err: ${err}`);
            }
        }
        resolve(installedLatestLsp);
    });
}

/**
 * Helper function to run 'java -version' and parse the result to check if it
 * meets out minimum Java major version
 * @param javaLoc Location of java executable (e.g. value of $JAVA_HOME) 
 * @returns true if running `java -version` returns a `version 'X.Y.Z'` where X
 *          meets out minimum Java major version
 */
function isJavaVersionCompatible(javaLoc: string): boolean {
    try {
        const javaVerCmd = child_process.spawnSync(javaLoc, ['-version'], { encoding : 'utf8' });
        if (!javaVerCmd || javaVerCmd.stdout) {
            return false;
        }
        // java -version actually writes to stderr so check for a match there
        const match = javaVerCmd.stderr.toString().match(/version \"([0-9]+)\.[0-9]+\.[0-9]\"/m);
        return (match && match.length > 1 && (parseInt(match[1]) >= minimumMajorJavaVersion));
    } catch (err) {
        console.warn(`Error checking for java version via '${javaLoc} -version', err: ${err}`);
    }
    return false;
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
    const spl2Artifacts = getLocalSpl2Dir(context);
    const jdkArtifacts = getLocalJdkDir(context);
    const lspArtifacts = getLocalLspDir(context);
    [localSplunkArtifacts, spl2Artifacts, jdkArtifacts, lspArtifacts].forEach((path) => {
        if (!fs.existsSync(path)) {
            fs.mkdirSync(path);
        }
    });
}

function getLocalSpl2Dir(context: ExtensionContext): string {
    return path.join(context.globalStorageUri.fsPath, 'spl2');
}

function getLocalJdkDir(context: ExtensionContext): string {
    return path.join(context.globalStorageUri.fsPath, 'spl2', 'jdk');
}

function getLocalLspDir(context: ExtensionContext): string {
    return path.join(context.globalStorageUri.fsPath, 'spl2', 'lsp');
}

async function promptToDownloadJava(): Promise<boolean> {
    const promptMessage = (
        `For SPL2 support Java ${minimumMajorJavaVersion} or later is required.`
    );
    const downloadAndInstallChoice = 'Download and Install';
    const turnOffSPL2Choice = 'Turn off SPL2 support';
  
    const popup = window.showInformationMessage(
        promptMessage,
        { modal: true },
        downloadAndInstallChoice,
        turnOffSPL2Choice,
    );
  
    const userSelection = (await popup) || null;
    switch(userSelection) {
        case downloadAndInstallChoice:
            // Record preference so user is not asked again
            workspace.getConfiguration().update(configKeyAcceptedTerms, TermsAcceptanceStatus.Accepted, true);
            return true;
        case turnOffSPL2Choice:
            console.log('User opted out of SPL2 Langauge Server download, SPL2 support disabled');
            // Record preference so user is not asked again
            workspace.getConfiguration().update(configKeyAcceptedTerms, TermsAcceptanceStatus.DeclinedForever, true);
            return false;
        default:
            // Cancel, record no preference
            return false;
    }
}

/**
 * Helper function to install appropriate JDK to run the SPL2 Language Server
 * @param installDir Local directory file path to write JDK to
 */
async function installJDK(installDir: string, progressBar: StatusBarItem): Promise<string> {
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
    let compressedSize = 0;
    try {
        compressedSize = await downloadWithProgress(url, downloadedArchive, progressBar, 'Downloading JDK');
    } catch (err) {
        throw new Error(`Error downloading JDK: ${err}`);
    }

    // Extract JDK and return path to java executable
    let binJarPath;

    progressBar.show();
    try {
        if (ext === 'zip') {
            binJarPath = await extractZipWithProgress(downloadedArchive, installDir, compressedSize, progressBar, 'Unzipping JDK');
        } else { // tar.gz
            binJarPath = await extractTgzWithProgress(downloadedArchive, installDir, compressedSize, progressBar, 'Extracting JDK');
        }
    } catch (err) {
        throw new Error(`Error extracting JDK: ${err}`);
    } finally {
        progressBar.hide();
    }
    if (!binJarPath) {
        throw new Error(`Error finding path to java executable within extracted JDK`);
    }
    return binJarPath;
}

/**
 * Helper function to download a file, updating a progress bar while downloading, and returning
 * a Promise containing the total size of the download.
 * @param url URL of artifact to download
 * @param destinationPath Local path to download to
 * @param progressBar To update download progress
 * @param progressBarText Text describing what's being downloaded to precede download %
 * @returns 
 */
async function downloadWithProgress(
    url: string,
    destinationPath: string,
    progressBar: StatusBarItem,
    progressBarText: string,
): Promise<number> {
    const fileWriter = fs.createWriteStream(destinationPath);

    return new Promise(async (resolve, reject) => {
        const { data, headers } = await axios({
            url,
            method: 'GET',
            responseType: 'stream',
            transformRequest: (data, headers) => {
                // Override defaults set elsewhere for splunkd communication
                delete headers.common['Authorization'];
                delete headers.common['Accept'];
                return data;
              },
        });
        const totalSize = parseInt(headers['content-length']);
        let totalDownloaded = 0;
        let nextUpdate = 1;
        let error;
        progressBar.show();
        data.on('data', (chunk) => {
            totalDownloaded += chunk.length;
            let pct = Math.floor(totalDownloaded * 100 / totalSize);
            if (pct === nextUpdate) {
                progressBar.text = `${progressBarText} ${pct}%`;
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
                resolve(totalSize);
            }
        });
        data.pipe(fileWriter);
    });
}

async function extractZipWithProgress(
    zipfilePath:string,
    extractPath: string,
    compressedSize: number,
    progressBar: StatusBarItem,
    progressBarText: string,
): Promise<string> {
    // Create read and unzip streams and listen for individual entry to find bin\java.exe
    let binJavaPath;
    let readCompressedSize = 0;
    let nextUpdate = 1;

    const pipe = util.promisify(pipeline);
    const readStream = fs.createReadStream(zipfilePath);
    const unzipStream = unzipper.Extract({ path: extractPath });
    unzipStream._writable.on('entry', entry => {
        if (entry.path.endsWith(path.join('bin', 'java.exe'))) {
            binJavaPath = path.join(extractPath, entry.path);
        }
        readCompressedSize += entry.vars.compressedSize;
        let pct = Math.floor(readCompressedSize * 100 / compressedSize);
        if (pct === nextUpdate) {
            progressBar.text = `${progressBarText} ${pct}%`;
            nextUpdate++;
        }
        entry.autodrain();
    });
    await pipe(
        readStream,
        unzipStream,
    );
    return binJavaPath;
}

async function extractTgzWithProgress(
        tgzPath:string,
        extractPath: string,
        compressedSize: number,
        progressBar: StatusBarItem,
        progressBarText: string,
    ): Promise<string> {
    // Create read and unzip streams and listen for individual entry to find bin\java.exe
    let binJavaPath;
    let readCompressedSize = 0;
    let nextUpdate = 1;

    const pipe = util.promisify(pipeline);
    
    await pipe(
        fs.createReadStream(tgzPath).on('data', (chunk) => {
            readCompressedSize += chunk.length;
            let pct = Math.floor(readCompressedSize * 100 / compressedSize);
            if (pct === nextUpdate) {
                progressBar.text = `${progressBarText} ${pct}%`;
                nextUpdate++;
            }
        }),
        zlib.createGunzip(),
        tar.extract(extractPath, {
            map: (header) => {
                if (header.name.endsWith(path.join('bin', 'java'))) {
                    binJavaPath = path.join(extractPath, header.name);
                }
                return header;
            }
        }),
    );
    return binJavaPath;
}

async function promptToDownloadLsp(alsoInstallJava: boolean): Promise<boolean> {
    const promptMessage = (
        'For SPL2 support with this extension a download of the SPL2 Language ' +
        'Server subject to the Splunk General Terms ' +
        (
            alsoInstallJava ?
                `and of Java ${minimumMajorJavaVersion} are required.` :
                'is required.'
        )
    );
    const agreeAndContinueChoice = 'Agree and Continue';
    const viewTermsChoice = 'View Splunk General Terms';
    const turnOffSPL2Choice = 'Turn off SPL2 support';

    const popup = window.showInformationMessage(
        promptMessage,
        { modal: true },
        agreeAndContinueChoice,
        viewTermsChoice,
        turnOffSPL2Choice,
    );
    
    const userSelection = (await popup) || null;
    switch(userSelection) {
        case agreeAndContinueChoice:
            return true;
        case viewTermsChoice:
            console.log('Viewing Splunk General Terms in browser...');
            env.openExternal(Uri.parse('https://www.splunk.com/en_us/legal/splunk-general-terms.html'));
            return await promptToDownloadLsp(alsoInstallJava);
        case turnOffSPL2Choice:
            console.log('User opted out of SPL2 Langauge Server download, SPL2 support disabled');
            // Record preference so user is not asked again
            workspace.getConfiguration().update(configKeyAcceptedTerms, TermsAcceptanceStatus.DeclinedForever, true);
            return false;
        default:
            // Cancel
            return false;
    }
}

/**
 * Checks if the installed SPL2 Language Server version is the latest and prompt for
 * upgrade if not, or automatically upgrade if user has that setting enabled.
 */
export async function getLatestSpl2Release(context: ExtensionContext, progressBar: StatusBarItem): Promise<void> {
    return new Promise(async (resolve, reject) => {
        const lspArtifactPath = path.join(context.globalStorageUri.fsPath, 'lsp');
        // TODO: Remove this hardcoded version/update time and check for updates
        let lspVersion: string = '2.0.362'; // context.globalState.get(stateKeyLatestLspVersion) || "";
        const lastUpdateMs: number = Date.now(); // context.globalState.get(stateKeyLastLspCheck) || 0;
        // Check for new version of SPL2 Language Server if longer than 24 hours
        if (Date.now() - lastUpdateMs > 24 * 60 * 60 * 1000) {
            const metaPath = path.join(lspArtifactPath, 'maven-metadata.xml');
            try {
                await downloadWithProgress(
                    'https://splunk.jfrog.io/splunk/maven-splunk-release/spl2/com/splunk/spl/spl-lang-server-sockets/maven-metadata.xml',
                    metaPath,
                    progressBar,
                    'Checking for SPL2 updates',
                );
                const parser = new XMLParser();
                const metadata = fs.readFileSync(metaPath);
                const metaParsed = parser.parse(metadata);
                lspVersion = metaParsed?.metadata?.versioning?.release;
            } catch (err) {
                console.warn(`Error retrieving latest SPL2 version, err: ${err}`);
            }
        }
        const lspFilename = `spl-lang-server-sockets-${lspVersion}-all.jar`;
        const localLspPath = path.join(getLocalLspDir(context), lspFilename);
        // Check if local file exists before downloading
        if (!fs.existsSync(localLspPath)) {
            try {
                await downloadWithProgress(
                    `https://splunk.jfrog.io/splunk/maven-splunk/spl2/com/splunk/spl/spl-lang-server-sockets/${lspVersion}/${lspFilename}`,
                    localLspPath,
                    progressBar,
                    'Downloading SPL2 Language Server',
                );
            } catch (err) {
                reject(`Error downloading SPL2 Language Server, err: ${err}`);
            }
        }
        // Update this setting to indicate that this version is ready-to-use
        try {
            workspace.getConfiguration().update(configKeyLspVersion, lspVersion, true);
        } catch (err) {
            reject(`Error updating configuration '${configKeyLspVersion}', err: ${err}`);
        }
        resolve();
    });
}
