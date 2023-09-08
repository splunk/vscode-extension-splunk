import * as path from 'path';
import {
  downloadAndUnzipVSCode,
  runTests
} from '@vscode/test-electron';

// We refer to these as functional tests because they must be run within the test-electron framework
// which requires VSCode itself in order to resolve 'vscode' imports for the files being tested.
// Example taken from: https://code.visualstudio.com/api/working-with-extensions/testing-extension#custom-setup-with-vscodetestelectron
async function main() {
  try {
    const extensionDevelopmentPath = path.resolve(__dirname, '..'); // root of repo
    const functionalTestsPath = path.resolve(__dirname, './functional/index');
    const vscodeExecutablePath = await downloadAndUnzipVSCode('stable');
    
    // Run the extension test
    await runTests({
      // Use the specified `code` executable
      vscodeExecutablePath,
      extensionDevelopmentPath,
      extensionTestsPath: functionalTestsPath
    });
  } catch (err) {
    console.error(`Failed to run tests: ${err}`);
    process.exit(1);
  }
}

main();
