import { ExtensionContext, workspace } from 'vscode';

// Keys used to store/retrieve state related to this extension
export const configKeyAcceptedTerms = 'splunk.spl2.acceptedTerms';
export const configKeyJavaPath = 'splunk.spl2.javaPath';
export const configKeyLSPVersion = 'splunk.spl2.languageServerVersion';

export enum TermsAcceptanceStatus {
    DeclinedForever = "declined (forever)",
    DeclinedOnce = "declined (once)",
    Accepted = "accepted",
}

export async function getMissingSpl2Requirements(context: ExtensionContext): Promise<void> {
    return new Promise((resolve, reject) => {
        // If the user has already opted-out for good then stop here
        const termsStatus: TermsAcceptanceStatus = workspace.getConfiguration().get(configKeyAcceptedTerms);
        if (termsStatus === TermsAcceptanceStatus.DeclinedForever) {
            reject(
                `User opted out of SPL2. To reset this adjust the '${configKeyAcceptedTerms}' ` +
                `setting to = '${TermsAcceptanceStatus.DeclinedOnce}' in the Splunk Extension Settings.`
            );
            return;
        }
        // TODO:
        // Check for compatible Java version installed already
        //  a) JAVA_HOME first
        //  b) JDK we installed in context.globalStorageUri.fsPath
        // Check workspaceState for current LSP version
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

export async function getLatestSpl2Release(context: ExtensionContext): Promise<void> {
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
