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
    _vscode: {
        metadata: { [key: string]: any };
        outputs?: RawCellOutput[];
    };
}

export class Spl2NotebookSerializer implements vscode.NotebookSerializer {
    async deserializeNotebook(
        content: Uint8Array,
        token: vscode.CancellationToken
    ): Promise<vscode.NotebookData> {
        var contents = new TextDecoder().decode(content);

        let raw: Spl2ModulesJson;

        try {
            raw = <Spl2ModulesJson>JSON.parse(contents);
        } catch (err) {
            raw = <Spl2ModulesJson>{
                modules: [],
                app: "apps.search",
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
        token: vscode.CancellationToken
    ): Promise<Uint8Array> {
        let contents: Spl2ModulesJson = <Spl2ModulesJson>{
            modules: [],
            app: "apps.search",
        };

        let indx = 1;
        for (const cell of data.cells) {
            contents.modules.push(<Spl2ModuleCell>{
                name: `module${indx++}`,
                namespace: "",
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
