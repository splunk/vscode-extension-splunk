import * as vscode from 'vscode';

import {
    cancelSearchJob,
    dispatchSpl2Module,
    getClient,
    getSearchJob,
    getSearchJobResults,
    wait,
} from '../splunk';
import { splunkMessagesToOutputItems } from '../utils';

// TODO: refactor to inherit/compose with SplunkController for DRYness
export class Spl2Controller {
    readonly controllerId = 'spl2-notebook-controller';
    readonly notebookType = 'spl2-notebook';
    readonly label = 'SPL2 Note';
    readonly supportedLanguages = ['splunk_spl2'];

    private readonly _controller: vscode.NotebookController;
    private _executionOrder = 0;
    private _interrupted = false;

    constructor() {
        this._controller = vscode.notebooks.createNotebookController(
            this.controllerId,
            this.notebookType,
            this.label,
        );

        this._controller.supportedLanguages = this.supportedLanguages;
        this._controller.supportsExecutionOrder = true;
        this._controller.executeHandler = this._execute.bind(this);
    }

    dispose(): void {
        this._controller.dispose();
    }

    async runCell(cell: vscode.NotebookCell) {
        const notebookDocument = await vscode.workspace.openNotebookDocument(cell.document.uri)
        this._execute([cell], notebookDocument, this._controller);
    }

    private _execute(
        cells: vscode.NotebookCell[],
        _notebook: vscode.NotebookDocument,
        _controller: vscode.NotebookController
    ): void {
        for (let cell of cells) {
            if (cell.document.languageId == 'splunk_spl2') {
                this._doExecution(cell);
            }
        }
    }

    async interruptHandler(notebook: vscode.NotebookDocument): Promise<void> {
        console.log('interrupt handler called');
    }

    private async _doExecution(cell: vscode.NotebookCell): Promise<void> {
        this._interrupted = false;
        console.log(cell);
        const execution = this._controller.createNotebookCellExecution(cell);
        execution.executionOrder = ++this._executionOrder;
        execution.start(Date.now());

        const spl2Module = cell.document.getText().trim();
        const service = getClient();
    
        let activeThemeKind = vscode.window.activeColorTheme.kind;
        let backgroundColor = new vscode.ThemeColor('notebook.editorBackground');

        let job;
        try {
            job = await dispatchSpl2Module(service, spl2Module);
        } catch (failedResponse) {
            const messages = failedResponse.data.messages;
            const messageItems = splunkMessagesToOutputItems(messages);

            execution.replaceOutput([new vscode.NotebookCellOutput(messageItems)]);
            execution.end(false, Date.now());
            return;
        }

        execution.replaceOutput([new vscode.NotebookCellOutput([], { job: job.properties() })]);

        execution.token.onCancellationRequested(async () => {
            this._interrupted = true;

            let res: any = await cancelSearchJob(job);

            const messageItems = splunkMessagesToOutputItems(res.data.messages);
            execution.replaceOutput([new vscode.NotebookCellOutput(messageItems, { job: job.properties() })]);

            execution.end(undefined, Date.now());
        });

        let jobComplete = false;

        while (!jobComplete && !this._interrupted) {
            job = await getSearchJob(job);

            if (job.properties().isDone == true) {
                jobComplete = true;
                continue;
            } 
            wait(1000);
        }        

        if (job.properties().isFailed == true) {
            const messages = job.properties().messages;
            const messageItems = splunkMessagesToOutputItems(messages);

            execution.replaceOutput([new vscode.NotebookCellOutput(messageItems, { job: job.properties() })]);
            execution.end(false, Date.now());
            return
        }

        if (!this._interrupted) {
            let results: any = await getSearchJobResults(job);

            execution.replaceOutput([
                new vscode.NotebookCellOutput(
                    [
                        vscode.NotebookCellOutputItem.json(
                            {
                                results: results.data,
                                _meta: {
                                    backgroundColor: backgroundColor,
                                    colorMode: activeThemeKind,
                                    cellMeta: cell.metadata,
                                },
                            },
                            'application/splunk/events'
                        ),
                        vscode.NotebookCellOutputItem.json(job.properties()),
                    ],
                    { job: job.properties() }
                ),
            ]);

            execution.end(true, Date.now());
        }
    }
}
