import * as vscode from 'vscode';

import {
    cancelSearchJob,
    createSearchJob,
    getClient,
    getSearchJob,
    getSearchJobResults,
    wait,
} from './splunk';
import { splunkMessagesToOutputItems } from './utils/messages';

export class SplunkController {
    public notebookType: string;

    protected controllerId: string;
    protected label: string;
    protected supportedLanguages: string[];

    protected _controller: vscode.NotebookController;
    private _executionOrder = 0;
    private _interrupted = false;
    private _tokens = {};
    private _lastjob = undefined;

    readonly _spl_meta_help = `
    SPL-META Manual

    To set a token:
    <tokenname> = <tokenvalue>

    To display all tokens:
    token

    To reset token state:
    reset_tokens

    Special tokens:
    _lastjob: Contains the search id (sid) of the last query
    `;

    constructor(
            controllerId = 'splunk-notebook-controller',
            notebookType = 'splunk-notebook',
            label = 'SPL Note',
            supportedLanguages = ['markdown', 'splunk_search', 'splunk-spl-meta']
        ) {
        this.controllerId = controllerId;
        this.notebookType = notebookType;
        this.label = label;
        this.supportedLanguages = supportedLanguages;

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

    protected _execute(
        cells: vscode.NotebookCell[],
        _notebook: vscode.NotebookDocument,
        _controller: vscode.NotebookController
    ): void {
        for (let cell of cells) {
            if (cell.document.languageId == 'splunk-spl-meta') {
                this._doMetaExecution(cell);
            } else {
                this._doExecution(cell);
            }
        }
    }

    async interruptHandler(notebook: vscode.NotebookDocument): Promise<void> {
        console.log('interrupt handler called');
    }

    private async _doMetaExecution(cell: vscode.NotebookCell): Promise<void> {
        let lines = cell.document.getText().split('\n');
        const execution = this._controller.createNotebookCellExecution(cell);
        execution.start(Date.now());

        let outputItems: vscode.NotebookCellOutputItem[] = [];

        for (const line of lines) {
            if (line === 'tokens') {
            } else if (line == 'reset_tokens') {
                this._tokens = {};
                this._tokens['_lastjob'] = this._lastjob;
            } else if (line.includes('=')) {
                let tokenizedLine = line.split('=');

                if (tokenizedLine.length !== 2) {
                    execution.replaceOutput([
                        new vscode.NotebookCellOutput([
                            vscode.NotebookCellOutputItem.text(
                                'Could not parse token assignment' + '\n' + this._spl_meta_help
                            ),
                        ]),
                    ]);
                    execution.end(false, Date.now());
                }
                this._tokens[tokenizedLine[0].trim()] = tokenizedLine[1].trim();
            } else {
                execution.replaceOutput([
                    new vscode.NotebookCellOutput([
                        vscode.NotebookCellOutputItem.text(
                            'Could not parse instructions' + '\n' + this._spl_meta_help
                        ),
                    ]),
                ]);
                execution.end(false, Date.now());
            }
        }
        outputItems.push(vscode.NotebookCellOutputItem.json(this._tokens));

        execution.replaceOutput([new vscode.NotebookCellOutput(outputItems)]);
        execution.end(true, Date.now());
    }

    protected _startExecution(cell: vscode.NotebookCell): vscode.NotebookCellExecution {
        this._interrupted = false;
        console.log(cell);
        const execution = this._controller.createNotebookCellExecution(cell);
        execution.executionOrder = ++this._executionOrder;
        execution.start(Date.now());
        return execution;
    }

    private async _doExecution(cell: vscode.NotebookCell): Promise<void> {
        const execution = this._startExecution(cell);

        let query = cell.document.getText().trim().replace(/^\s+|\s+$/g, '');

        const service = getClient()
    
        let jobs = service.jobs();

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
        await this._finishExecution(job, cell, execution);
    }
    
    protected async _finishExecution(job: any, cell: vscode.NotebookCell, execution: vscode.NotebookCellExecution) {
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
            execution.replaceOutput([new vscode.NotebookCellOutput([], { job: job.properties() })]);
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
            let activeThemeKind = vscode.window.activeColorTheme.kind;
            let backgroundColor = new vscode.ThemeColor('notebook.editorBackground');    

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
                                    languageId: cell?.document?.languageId,
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
