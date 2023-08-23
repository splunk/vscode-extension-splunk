import * as assert from 'assert';
import { TextEncoder } from 'util';
import { Spl2NotebookSerializer } from '../out/notebooks/spl2/serializer';

describe('SPL2 should serialize and deserialize in backwards compatible fashion', () => {
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

	it('test .spl2nb contents should deserialize as expected', async () => {
        const out = await serializer.deserializeNotebook(new TextEncoder().encode(input));
        assert.ok(out);
	});
});
