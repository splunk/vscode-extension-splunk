import * as assert from 'assert';
import * as vscode from 'vscode';
import { Spl2NotebookSerializer } from '../../out/notebooks/spl2/serializer';
// import { Spl2Controller } from '../../out/notebooks/spl2/controller';
// import { installMissingSpl2Requirements, getLatestSpl2Release } from '../../out/notebooks/spl2/installer';
// import { startSpl2ClientAndServer } from '../../out/notebooks/spl2/initializer';
suite('SPL2 Language Server functional', async () => {
	const serializer = new Spl2NotebookSerializer();
    const input = `{
		"modules": [
			{
				"name": "my_module",
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
				"name": "apps.baz",
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

	test('test .spl2nb contents should deserialize and serialize as expected', async () => {
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
	});
});
