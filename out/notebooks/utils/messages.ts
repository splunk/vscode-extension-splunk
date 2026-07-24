import * as vscode from 'vscode'

export interface SplunkMessage {
    type: string,
    code: string,
    text: string,
    details?: string,
}

export function splunkMessagesToOutputItems(messages: SplunkMessage[]) : vscode.NotebookCellOutputItem[] {
    return messages.map(msg => splunkMessageToOutputItem(msg))
}

export function splunkMessageToOutputItem(message: SplunkMessage) : vscode.NotebookCellOutputItem {

    const outputItem = vscode.NotebookCellOutputItem.text(
        (message.details == undefined)
        ? `${message.type}: ${message.code ? message.code + ' - ' : ''} ${message.text}`
        : `${message.type}: ${message.code ? message.code + ' - ' : ''} ${message.text}. Details: ${message.details}`
    )
    return outputItem
}

