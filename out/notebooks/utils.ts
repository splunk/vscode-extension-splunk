import * as vscode from 'vscode'

export interface SplunkMessage {
    type: string,
    code: string,
    text: string
}

export function splunkMessagesToOutputItems(messages: SplunkMessage[]) : vscode.NotebookCellOutputItem[] {
    return messages.map(msg => splunkMessageToOutputItem(msg))
}

export function splunkMessageToOutputItem(message: SplunkMessage) : vscode.NotebookCellOutputItem {

    const outputItem = vscode.NotebookCellOutputItem.text(
        `${message.type}: ${message.code ? message.code + ' - ' : ''} ${message.text}`
    )
    return outputItem
}

