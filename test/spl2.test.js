const { assert } = require('chai');
const { getModuleStatements } = require("../out/notebooks/utils/parsing");

describe('splunk', () => {
    describe('getModuleStatements()', () => {
        it('should find a single statement', () => {
            const module = `
                $out = from a;
            `;
            const statements = getModuleStatements(module);
            assert.equal(statements.length, 1);
            assert.isAtLeast(statements[0].length, 2);
            assert.equal(statements[0][1], 'out');
        });
        it('should find each statement when several specified', () => {
            const module = `
                $out1 = from a;
                $out2 = from b;
                $out3 = from c;
            `;
            const statements = getModuleStatements(module);
            assert.equal(statements.length, 3);
            assert.isAtLeast(statements[0].length, 2);
            assert.isAtLeast(statements[1].length, 2);
            assert.isAtLeast(statements[2].length, 2);
            assert.equal(statements[0][1], 'out1');
            assert.equal(statements[1][1], 'out2');
            assert.equal(statements[2][1], 'out3');
        });
    });
});
