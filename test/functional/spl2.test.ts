import * as assert from 'assert';
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
				"definition": "$data = from [{\"foo\": \"bar\"}]",
				"_vscode": {
					"metadata": {
						"splunk": {
							"moduleName": "my_module",
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
				"definition": "$data = from [{\"bar\": \"baz\"}]",
				"_vscode": {
					"metadata": {
						"splunk": {
							"moduleName": "apps.baz",
							"namespace": "apps.my_spl2_app"
						}
					},
					"outputs": []
				}
			}
		],
		"app": "apps.my_spl2_app"
		}`;

	test('test .spl2nb contents should deserialize as expected', async () => {
        const out = await serializer.deserializeNotebook(new TextEncoder().encode(input));
        assert.ok(out);
		// TODO better assertions
	});
});
