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

// Some pointers taken from here: https://vscode.rocks/testing/#end-to-end-testing
suite('SPL2 Language Server integration', async () => {
	try {
		vscode.window.showInformationMessage('Start all tests.');
		const splunkExt = vscode.extensions.getExtension('Splunk.splunk');
		const blankDocUri = vscode.Uri.file(path.join(docsDir, 'blank.spl2nb'));
		const doc = await vscode.workspace.openNotebookDocument(blankDocUri);
		const editor = await vscode.window.showNotebookDocument(doc);
		const nb = editor.notebook;
	} catch (e) {
		console.log(e);
		assert.fail(e);
	}

	test('Sample test', () => {
		assert.strictEqual([1, 2, 3].indexOf(5), -1);
		assert.strictEqual([1, 2, 3].indexOf(0), -1);
	}).timeout(60*1000); // 1 min
}).timeout(10*60*1000); // 10 min
