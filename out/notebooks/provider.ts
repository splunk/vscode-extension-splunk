import * as vscode from 'vscode';
import { VIZ_TYPES } from './visualizations';

export class CellResultCountStatusBarProvider implements vscode.NotebookCellStatusBarItemProvider {
    _outputChannel: vscode.OutputChannel;

    constructor(outputChannel: vscode.OutputChannel) {
        this._outputChannel = outputChannel;
    }

    provideCellStatusBarItems(
        cell: vscode.NotebookCell,
        token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.NotebookCellStatusBarItem[]> {

        const items: vscode.NotebookCellStatusBarItem[] = [];

        if (cell.document.languageId !== "splunk_search" && cell.document.languageId !== "splunk_spl2") {
            return items
        }

        const visualizationPreference = cell.metadata?.splunk?.visualizationPreference;

        let label = '$(graph)';

        if (visualizationPreference) {
            const vizName = VIZ_TYPES.find((type) => type.value === visualizationPreference).label;
            label += ' ' + vizName;
        }
        items.push({
            text: label,
            alignment: vscode.NotebookCellStatusBarAlignment.Right,
            tooltip: visualizationPreference ? 'Modify Chart Preference' : 'Set Chart Preference',
            command: {
                title: 'Modify Visualization Preference',
                command: 'splunk.notebooks.addVisualizationPreference',
                arguments: [cell, this._outputChannel],
            },
        });

        const earliestPicker = {
            text: 'earliest',
            alignment: vscode.NotebookCellStatusBarAlignment.Right,
            tooltip: 'Earliest time',
            command: {
                title: 'Enter Earliest time',
                command: 'splunk.notebooks.enterEarliestTime',
                arguments: [cell],
            },
        };

        const latestPicker = {
            text: 'latest',
            alignment: vscode.NotebookCellStatusBarAlignment.Right,
            tooltip: 'Latest time',
            command: {
                title: 'Enter Latest time',
                command: 'splunk.notebooks.enterLatestTime',
                arguments: [cell],
            },
        };
        // earliest and latest time pickers are only supported for SPL2 at the moment
        if (cell.document.languageId === 'splunk_spl2') {
            items.push(earliestPicker);
            items.push(latestPicker);
        }

        if (cell.outputs.length === 1) {
            const meta = cell.outputs[0].metadata;

            if (meta) {
                if (meta.job !== undefined) {
                    if (
                        meta.job.dispatchState != 'DONE' &&
                        meta.job.isFailed != true &&
                        (meta.job.eventCount != undefined || meta.job.scanCount != undefined)
                    ) {
                        items.push({
                            text: `${meta.job.eventCount.toLocaleString()} of ${meta.job.scanCount.toLocaleString()} matched`,
                            tooltip: 'Dispatch State',
                            alignment: vscode.NotebookCellStatusBarAlignment.Left,
                        });
                    }
                    items.push({
                        text: `$(symbol-number) ${meta.job['sid']}`,
                        tooltip: 'Copy Job ID to clipboard',
                        alignment: vscode.NotebookCellStatusBarAlignment.Right,
                        command: {
                            "title": "Copy Job ID to clipboard",
                            "command": "splunk.notebooks.copyJobIdToClipboard",
                            "arguments": [cell]
                        }
                    });
                    // earliest and latest time pickers are only supported for SPL2 at the moment
                    if (cell.document.languageId === 'splunk_spl2') {
                        items.push(earliestPicker);
                        items.push(latestPicker);
                    }
                    items.push({
                        tooltip: 'Dispatch State',
                        text: `$(gear) ${meta.job['dispatchState'] ? meta.job['dispatchState'].toLowerCase() : ''}`,
                        alignment: vscode.NotebookCellStatusBarAlignment.Right,
                    });
                    items.push({
                        text: `$(list-selection)`,
                        tooltip: 'Search ID',
                        alignment: vscode.NotebookCellStatusBarAlignment.Right,
                        command: {
                            title: 'Open Job Search Log',
                            command: 'splunk.notebooks.openSearchLog',
                            arguments: [cell],
                        },
                    });
                }

                if (meta.job !== undefined && meta.job.dispatchState == 'DONE') {
                    const numResults = meta.job.eventCount;
                    const earliestTime = new Date(meta.job.earliestTime);
                    const latestTime = meta.job.latestTime !== undefined ? new Date(meta.job.latestTime).toLocaleString() : 'now';

                    items.push({
                        text: `${numResults.toLocaleString()} events from ${earliestTime.toLocaleString()} to ${
                            latestTime
                        }`,
                        tooltip: 'has outputs',
                        alignment: vscode.NotebookCellStatusBarAlignment.Left,
                    });
                }
            }
        }

        return items;
    }
}
