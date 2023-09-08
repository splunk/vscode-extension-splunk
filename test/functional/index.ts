import * as path from 'path';
import * as Mocha from 'mocha';
import * as glob from 'glob';

// Example taken from: https://github.com/microsoft/vscode-extension-samples/tree/main/helloworld-test-sample
export function run(): Promise<void> {
	// Create the mocha test
	const mocha = new Mocha({
		ui: 'tdd'
	});
 
	const testsRoot = path.resolve(__dirname);
	
	return new Promise((resolve, reject) => {
		console.log(`Checking for *.test.js in ${testsRoot}`);
		glob('**/**.test.js', { cwd: testsRoot }, (err, files) => {
			if (err) {
				return reject(err);
			}

			// Add files to the test suite
			files.forEach(f => {
				console.log(`Found ${f}`);
				mocha.addFile(path.resolve(testsRoot, f))
			});

			try {
				// Run the mocha test
				mocha.run(failures => {
					if (failures > 0) {
						reject(new Error(`${failures} tests failed.`));
					} else {
						resolve();
					}
				});
			} catch (err) {
				console.error(err);
				reject(err);
			}
		});
	});
}
