import * as assert from 'assert';
import * as path from 'path';
import * as vscode from 'vscode';
// import { Spl2NotebookSerializer } from '../../out/notebooks/spl2/serializer';
// import { Spl2Controller } from '../../out/notebooks/spl2/controller';
// import { installMissingSpl2Requirements, getLatestSpl2Release } from '../../out/notebooks/spl2/installer';
// import { startSpl2ClientAndServer } from '../../out/notebooks/spl2/initializer';

// back out of out/test/integration and into test/integration/documents because ts compile
// won't handle these files
const docsDir = path.join(__dirname, '..', '..', '..', 'test', 'integration', 'documents');
const blankDocUri = vscode.Uri.file(path.join(docsDir, 'blank.spl2nb'));

// Some very helpful pointers taken from here: https://vscode.rocks/testing/#end-to-end-testing
suite('SPL2 Language Server integration', async () => {
	vscode.window.showInformationMessage('Start all tests.');
	
	test('SPL2 Language detected in .spl2nb', async () => {
		const doc = await vscode.workspace.openNotebookDocument(blankDocUri);
		assert.ok(doc, `Blank example .spl2nb doc not loaded from path: ${blankDocUri}`);
		const editor = await vscode.window.showNotebookDocument(doc);
		await sleep(500);
		assert.ok(editor, 'Loading editor with blank example .spl2nb doc failed');
		assert.ok(editor.notebook, 'Loading editor.notebook with blank example .spl2nb doc failed');
		assert.strictEqual(editor.notebook.notebookType, 'spl2-notebook');
	}).timeout(60*1000); // 1 min
}).timeout(10*60*1000); // 10 min

function sleep(ms: number): Promise<void> {
	return new Promise(resolve => {
		setTimeout(resolve, ms)
	})
}