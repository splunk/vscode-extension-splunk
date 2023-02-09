import { TextDecoder, TextEncoder } from 'util';
import * as vscode from 'vscode';

interface CellDisplayOutput {
    output_type: 'display_data' | 'execute_result';
    data: { [key: string]: any };
}

export type RawCellOutput = CellDisplayOutput;

interface RawNotebookCell {
    language: string;
    value: string;
    kind: vscode.NotebookCellKind;
    metadata: { [key: string]: any };
    outputs?: RawCellOutput[];
}

function transformOutputFromCore(output: vscode.NotebookCellOutput): RawCellOutput {

    const cellOutput: RawCellOutput = {output_type: "execute_result", data: {}}

    for (const outputItem of output.items) {
        cellOutput.data[outputItem.mime] = JSON.stringify(outputItem.data)
    }

    return cellOutput
}

function transformOutputToCore(rawOutput: RawCellOutput): vscode.NotebookCellOutput {
    const cellOutput: vscode.NotebookCellOutput = new vscode.NotebookCellOutput([])

    for (const [key, value] of Object.entries(rawOutput.data)) {
        let loadedValue = JSON.parse(value)
        let data;
        if (loadedValue.type === 'Buffer') {
            data = Buffer.from(loadedValue.data)
        }
        
        cellOutput.items.push({
            "mime": key,
            "data": data 
        })
    }
    return cellOutput
}

export class SplunkNotebookSerializer implements vscode.NotebookSerializer {
    async deserializeNotebook(
        content: Uint8Array,
        token: vscode.CancellationToken
    ): Promise<vscode.NotebookData> {
        var contents = new TextDecoder().decode(content);

        let raw: RawNotebookCell[];

        try {
            raw = <RawNotebookCell[]>JSON.parse(contents);
        } catch {
            raw = [];
        }

        const cells = raw.map((item) => {
            let newCell = new vscode.NotebookCellData(item.kind, item.value, item.language);

            newCell.metadata = item.metadata || {};
            newCell.outputs = item.outputs.map(output => transformOutputToCore(output))

            return newCell;
        });

        return new vscode.NotebookData(cells);
    }

    async serializeNotebook(
        data: vscode.NotebookData,
        token: vscode.CancellationToken
    ): Promise<Uint8Array> {
        let contents: RawNotebookCell[] = [];

        for (const cell of data.cells) {
            contents.push({
                kind: cell.kind,
                language: cell.languageId,
                value: cell.value,
                metadata: cell.metadata,
                outputs: cell.outputs.map((output) => transformOutputFromCore(output)),
            });
        }

        return new TextEncoder().encode(JSON.stringify(contents));
    }
}
