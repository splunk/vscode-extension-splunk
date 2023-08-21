import { TextDecoder, TextEncoder } from 'util';
import {
    RawCellOutput,
    transformOutputFromCore,
    transformOutputToCore,
} from '../serializers';
import * as vscode from 'vscode';

// Hardcode a few values that will never change for SPL2 notebooks
const spl2CellKind = vscode.NotebookCellKind.Code;
const spl2CellLanguage = 'splunk_spl2';

interface Spl2ModulesJson {
    modules: Spl2ModuleCell[],
    app: string, // hardcoded to apps.search for now
}

interface Spl2ModuleCell {
    name: string; // hardcoded to module1, module2, etc for now
    namespace: string; // hardcoded to "" for now
    definition: string; // SPL2 statements
    _vscode?: {
        metadata: { [key: string]: any };
        outputs?: RawCellOutput[];
    };
}

/**
 * Utility function to extract apps.<app>.[sub.name.spaces] from full namespace
 * @param fullNamespace Full namespace to use for extraction
 * @returns Two element array containing [app, subnamespace] if fullNamespace matches
 *   apps.<app>.[sub.name.spaces], otherwise default to ['search', '']
 */
export function getAppSubNamespace(fullNamespace: string): [string, string] {
    let app: string = 'search'; // default
    let subNamespace: string = ''; // default
    if (fullNamespace.startsWith('apps.')) {
        // Find <app> from apps.<app>[.optional.sub.namespaces]
        let secondDotIndx = fullNamespace.indexOf('.', 'apps.'.length);
        secondDotIndx = secondDotIndx < 0 ? fullNamespace.length : secondDotIndx;
        app = fullNamespace.substring('apps.'.length, secondDotIndx);
        // Find .optional.sub.namespaces from apps.<app>[.optional.sub.namespaces]
        subNamespace = fullNamespace.substring(secondDotIndx + 1, fullNamespace.length);
    }
    return [app, subNamespace];
}

export class Spl2NotebookSerializer implements vscode.NotebookSerializer {
    async deserializeNotebook(
        content: Uint8Array,
        token: vscode.CancellationToken | null
    ): Promise<vscode.NotebookData> {
        var contents = new TextDecoder().decode(content);

        let raw: Spl2ModulesJson;

        try {
            raw = <Spl2ModulesJson>JSON.parse(contents);
        } catch (err) {
            raw = <Spl2ModulesJson>{
                modules: [],
                app: 'apps.search', // default
            };
        }

        const cells = raw.modules.map((module) => {
            let newCell = new vscode.NotebookCellData(spl2CellKind, module.definition, spl2CellLanguage);

            newCell.metadata = module._vscode.metadata || {};
            newCell.outputs = module._vscode.outputs.map(output => transformOutputToCore(output))

            return newCell;
        });

        return new vscode.NotebookData(cells);
    }

    async serializeNotebook(
        data: vscode.NotebookData,
        token: vscode.CancellationToken | null
    ): Promise<Uint8Array> {
        let contents: Spl2ModulesJson = <Spl2ModulesJson>{
            modules: [],
            app: 'apps.search', // default
        };

        let indx = 1;
        for (const cell of data.cells) {
            const metadata = cell.metadata || {};
            if (metadata?.splunk?.namespace !== undefined) {
                // Attempt to read app from namespace
                contents.app = `apps.${getAppSubNamespace(metadata?.splunk?.namespace)[0]}`;
            }
            contents.modules.push(<Spl2ModuleCell>{
                name: metadata?.splunk?.moduleName || `module${indx++}`,
                namespace: metadata?.splunk?.namespace || "",
                definition: cell.value,
                _vscode: {
                    metadata: cell.metadata,
                    outputs: cell.outputs.map((output) => transformOutputFromCore(output)),
                },
            });
        }

        return new TextEncoder().encode(JSON.stringify(contents, null, 2));
    }
}
