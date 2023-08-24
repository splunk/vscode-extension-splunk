import * as assert from 'assert';
import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';
import { Spl2NotebookSerializer } from '../../out/notebooks/spl2/serializer';
import {
	configKeyAcceptedTerms,
	configKeyJavaPath,
	configKeyLspVersion,
	getLatestSpl2Release,
	getLspFilename,
	getLocalLspDir,
	installMissingSpl2Requirements,
	TermsAcceptanceStatus } from '../../out/notebooks/spl2/installer';

// import { startSpl2ClientAndServer } from '../../out/notebooks/spl2/initializer';
suite('SPL2 Language Server functional', async () => {
	const serializer = new Spl2NotebookSerializer();
	// NOTE: if you find yourself changing this input notebook data then it's likely that
	// you may be making a breaking change to the SPL2 notebook format which would break
	// users with existing notebooks in this format! Consider changing the serializer.ts
	// code instead to accomodate a backwards-compatible deserialization of this (potentially
	// legacy) notebook format.
    const input = `{
		"modules": [
			{
				"name": "_default",
				"namespace": "apps.search",
				"definition": "$data = from my_index_1",
				"_vscode": {
					"metadata": {
						"splunk": {
							"moduleName": "_default",
							"namespace": "apps.search",
							"earliestTime": "-2h",
							"latestTime": "-1h"
						}
					},
					"outputs": []
				}
			},
			{
				"name": "my_module",
				"namespace": "apps.my_spl2_app",
				"definition": "$data = from my_index_2",
				"_vscode": {
					"metadata": {
						"splunk": {
							"moduleName": "my_module",
							"namespace": "apps.my_spl2_app"
						}
					},
					"outputs": []
				}
			}
		],
		"app": "apps.my_spl2_app"
		}`;

	test('.spl2nb contents should deserialize and serialize as expected', async () => {
        const notebookData = await serializer.deserializeNotebook(new TextEncoder().encode(input));
        assert.ok(notebookData);
		assert.strictEqual(notebookData.cells.length, 2);
		const cell1 = notebookData.cells[0];
		assert.strictEqual(cell1.kind, vscode.NotebookCellKind.Code);
		assert.strictEqual(cell1.value, '$data = from my_index_1');
		assert.strictEqual(cell1.languageId, 'splunk_spl2');
		assert.ok(cell1?.metadata?.splunk);
		assert.strictEqual(cell1.metadata.splunk.earliestTime, '-2h');
		assert.strictEqual(cell1.metadata.splunk.latestTime, '-1h');
		assert.strictEqual(cell1.metadata.splunk.moduleName, '_default');
		assert.strictEqual(cell1.metadata.splunk.namespace, 'apps.search');
		assert.strictEqual(cell1.outputs?.length, 0);
		const cell2 = notebookData.cells[1];
		assert.strictEqual(cell2.kind, vscode.NotebookCellKind.Code);
		assert.strictEqual(cell2.value, '$data = from my_index_2');
		assert.strictEqual(cell2.languageId, 'splunk_spl2');
		assert.ok(cell2?.metadata?.splunk);
		assert.strictEqual(cell2.metadata.splunk.moduleName, 'my_module');
		assert.strictEqual(cell2.metadata.splunk.namespace, 'apps.my_spl2_app');

		// now test serialize
		const inputJSON = JSON.parse(input);
		const output = await serializer.serializeNotebook(notebookData);
		var outputStr = new TextDecoder().decode(output);
		const outputJSON = JSON.parse(outputStr);
		assert.deepStrictEqual(inputJSON, outputJSON, 'De-serialized and re-serialized notebook does not match original input');
	});

	test('should install Java and language server prerequisites', async () => {
		const progressBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
		// Before running tests, let's accept the terms of use since the UI can't be used to do this
		// Record preference so user is not asked again
		await vscode.workspace.getConfiguration().update(configKeyAcceptedTerms, TermsAcceptanceStatus.Accepted, true);
		const storagePath = path.join(__dirname, '..', '..', '..', '.vscode-test', 'user-data', 'User', 'globalStorage', 'spl2-tests');
		fs.mkdirSync(storagePath);
		// Periodically log the current progress since we have no UI to provide feedback in CI
		const tid = setInterval(() => console.log(`[Progress Bar]: ${progressBar.text}`), 500);
		const installedLatestLsp = await installMissingSpl2Requirements(storagePath, progressBar);
		clearInterval(tid);
		assert.strictEqual(installedLatestLsp, true);
		// Check for installed java and lsp
		const javaPath: string = vscode.workspace.getConfiguration().get(configKeyJavaPath) || "";
		assert.ok(javaPath);
		assert.strictEqual(fs.existsSync(javaPath), true);
		const lspVersion: string = vscode.workspace.getConfiguration().get(configKeyLspVersion) || "";
		assert.ok(lspVersion);
		const lspPath = path.join(getLocalLspDir(storagePath), getLspFilename(lspVersion));
		assert.ok(lspPath);
		assert.strictEqual(fs.existsSync(lspPath), true);
	}).timeout(1*60*1000); // 1 minute
}).timeout(5*60*1000); // 5 minutes
