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
            assert.equal(statements[0], 'out');
        });
        it('should find each statement when several specified', () => {
            const module = `
                $out1 = from a;
                $out2 = from b;
                $out3 = from c;
            `;
            const statements = getModuleStatements(module);
            assert.equal(statements.length, 3);
            assert.equal(statements[0], 'out1');
            assert.equal(statements[1], 'out2');
            assert.equal(statements[2], 'out3');
        });
        it('should ignore single line comments', () => {
            const module = `
                //$out1 = from a;
                $out2 = from b; // $out3 = from c;
                // $out4 = from c;
            `;
            const statements = getModuleStatements(module);
            assert.equal(statements.length, 1);
            assert.equal(statements[0], 'out2');
        });
        it('should ignore block comments', () => {
            const module = `
                /*$out1 = from a;
                */$out2 /* * */= from b;
                /* $out3 = from c;*/
            `;
            const statements = getModuleStatements(module);
            assert.equal(statements.length, 1);
            assert.equal(statements[0], 'out2');
        });
        it('should handle complex comment, field, and function scenarios', () => {
            const module = `
                $out1 = from [{s:1}] | eval '
                  $fieldtemp1 = ' = value1 | eval ' \\'
                  $fieldtemp2 = ' = value2 | eval field1 = 
                  " \\" $stringtemp1 = value3"
                | eval foo = map([1,2], $it -> {
                    $lp1 = 1;
                    return $f;
                });
                function func1()
                dataset ds1 {
                  '
                  $dsfield = ': "value"
                }
                function func2() {
                  $p1 = 1;
                  $p2 = $p1 + 1;
                  return $p2
                } $out2 = from [{s:2}] | where '$foo=bar'=2;
                $out3  /* $f1 = 1;
                $f2 = 2
                */ = from [{s:3}];
                $out4 = from [{'
                $fieldval = ': "error"}];`;
            const statements = getModuleStatements(module);
            assert.equal(statements.length, 4);
            assert.equal(statements[0], 'out1');
            assert.equal(statements[1], 'out2');
            assert.equal(statements[2], 'out3');
            assert.equal(statements[3], 'out4');
        });
    });
});