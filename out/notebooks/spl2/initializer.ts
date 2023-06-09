import { ExtensionContext, workspace } from 'vscode';
import {
    configKeyAcceptedTerms,
    configKeyJavaPath,
    configKeyLspVersion,
    TermsAcceptanceStatus
} from './installer';

export async function startSpl2ClientAndServer(context: ExtensionContext): Promise<void> {
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
        const javaPath = workspace.getConfiguration().get(configKeyJavaPath);
        const lspVersion = workspace.getConfiguration().get(configKeyLspVersion);
        // TODO test for open port and start client and server
        reject('LSP initialization not implemented');
    });
}