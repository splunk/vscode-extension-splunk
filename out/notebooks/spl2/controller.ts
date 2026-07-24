import * as vscode from 'vscode';

import { dispatchSpl2Module } from '../splunk';
import { SplunkController } from '../controller';
import { splunkMessagesToOutputItems } from '../utils/messages';
import { getAppSubNamespace } from './serializer';

export class Spl2Controller extends SplunkController {
    constructor() {
        super('spl2-notebook-controller', 'spl2-notebook', 'SPL2 Note', ['splunk_spl2']);
        this._controller.executeHandler = this._execute.bind(this);
    }

    protected _execute(
        cells: vscode.NotebookCell[],
        _notebook: vscode.NotebookDocument,
        _controller: vscode.NotebookController
    ): void {
        for (let cell of cells) {
            if (cell.document.languageId == 'splunk_spl2') {
                this._doSpl2Execution(cell);
            }
        }
    }

    private async _doSpl2Execution(cell: vscode.NotebookCell): Promise<void> {
        const execution = super._startExecution(cell);

        const spl2Module = cell.document.getText().trim();
        let fullNamespace: string = cell?.metadata?.splunk?.namespace || '';
        // Get apps.<app>[.optional.sub.namespaces] from fullNamespace
        const [app, subNamespace] = getAppSubNamespace(fullNamespace);
        const earliest = cell?.metadata?.splunk?.earliestTime;
        const latest = cell?.metadata?.splunk?.latestTime;
    
        let job;
        try {
            await this.refreshService();
            job = await dispatchSpl2Module(
                this._service,
                spl2Module,
                app,
                subNamespace,
                earliest,
                latest,
            );
            await super._finishExecution(job, cell, execution);
        } catch (failedResponse) {
            let outputItems: vscode.NotebookCellOutputItem[] = [];
            if (!failedResponse.data || !failedResponse.data.messages) {
                outputItems = [vscode.NotebookCellOutputItem.error(failedResponse)];
            } else {
                const messages = failedResponse.data.messages;
                outputItems = splunkMessagesToOutputItems(messages);
            }

            execution.replaceOutput([new vscode.NotebookCellOutput(outputItems)]);
            execution.end(false, Date.now());
        }
    }
}
