import * as vscode from 'vscode';

import {
    cancelSearchJob,
    createSearchJob,
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
    private _tokens = {};
    private _lastjob = undefined;

    constructor() {
        this._controller = vscode.notebooks.createNotebookController(
            this.controllerId,
            this.notebookType,
            this.label
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

        let query = cell.document.getText().trim().replace(/^\s+|\s+$/g, '');

        const service = getClient()
    
        let jobs = service.jobs();

        let activeThemeKind = vscode.window.activeColorTheme.kind;
        let backgroundColor = new vscode.ThemeColor('notebook.editorBackground');

        const tokenRegex = /\$([a-zA-Z0-9_.|]*?)\$/g;

        var controller = this;

        const replacer = function (match, p1, p2, p3, offset, string) {
            console.log(match, offset, string);

            const tokenName = match.replaceAll('$', '');
            console.log('token name', tokenName);
            if (tokenName in controller._tokens) {
                console.log(tokenName);
                return controller._tokens[tokenName];
            }
            return match;
        };

        const newQuery = query.replace(tokenRegex, replacer);

        query = newQuery;

        if (!query.startsWith('|')) {
            query = 'search ' + query;
        }

        let job;
        try {
            job = await createSearchJob(jobs, query, { output_mode: 'json_cols', 'status_buckets': 300 });
        } catch (failedResponse) {
            const messages = failedResponse.data.messages;
            const messageItems = splunkMessagesToOutputItems(messages);

            execution.replaceOutput([new vscode.NotebookCellOutput(messageItems)]);
            execution.end(false, Date.now());
            return;
        }

        let sid = job['sid'];
        this._lastjob = sid;
        this._tokens['_lastjob'] = this._lastjob;

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
