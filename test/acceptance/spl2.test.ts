import * as assert from 'assert';
import * as path from 'path';
import * as vscode from 'vscode';

// back out of out/test/integration and into test/integration/documents because ts compile
// won't handle these files
const docsDir = path.join(__dirname, '..', '..', '..', 'test', 'acceptance', 'documents');
const blankDocUri = vscode.Uri.file(path.join(docsDir, 'blank.spl2nb'));

// Some very helpful pointers taken from here: https://vscode.rocks/testing/#end-to-end-testing
suite('SPL2 Language Server acceptance', async () => {
	vscode.window.showInformationMessage('Start all tests.');

	test.skip('Language detected in .spl2nb should be SPL2', async () => {
		await sleep(1000);
		console.log(`[DEBUG] opening ${blankDocUri} ...`);
		// TODO: both these approaches result in Error: NO provider registered for view type: 'spl2-notebook'
		// const cell = new vscode.NotebookCellData(vscode.NotebookCellKind.Code, '$q = from [{}]', 'splunk_spl2');
		// const doc = await vscode.workspace.openNotebookDocument('spl2-notebook', new vscode.NotebookData([cell]));
		const doc = await vscode.workspace.openNotebookDocument(blankDocUri);
		await sleep(1000);
		console.log(`[DEBUG] showing ${blankDocUri} ...`);
		const editor = await vscode.window.showNotebookDocument(doc);
		assert.ok(editor, 'Loading editor with blank example .spl2nb doc failed');
		console.log(`[DEBUG] showing ${blankDocUri} ...`);
		await sleep(1000);
		console.log(`[DEBUG] accessing editor.notebook = ${editor.notebook} ...`);
		const nb = editor.notebook;
		assert.ok(nb, 'Loading editor.notebook with blank example .spl2nb doc failed');
		assert.strictEqual(nb.notebookType, 'spl2-notebook');
		assert.strictEqual(nb.cellAt(0).document.languageId, 'splunk_spl2');
	}).timeout(2*60*1000); // 2 min
}).timeout(10*60*1000); // 10 min

function sleep(ms: number): Promise<void> {
	return new Promise(resolve => {
		setTimeout(resolve, ms)
	})
}