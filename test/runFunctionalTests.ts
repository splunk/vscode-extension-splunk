import * as path from 'path';
import * as fs from 'fs';
import {
  downloadAndUnzipVSCode,
  runTests
} from '@vscode/test-electron';

async function main() {
  try {
    const extensionDevelopmentPath = path.resolve(__dirname, '..');
    const functionalTestsPath = path.resolve(__dirname, './functional/index');
    const vscodeExecutablePath = await downloadAndUnzipVSCode('stable');

    // Ensure the executable has correct permissions (macOS ARM runner fix)
    if (process.platform === 'darwin') {
      const electronPath = path.join(
        path.dirname(vscodeExecutablePath),
        'Visual Studio Code.app',
        'Contents',
        'MacOS',
        'Electron'
      );
      try {
        if (fs.existsSync(electronPath)) {
          fs.chmodSync(electronPath, 0o755);
          console.log(`Set permissions on: ${electronPath}`);
        }
      } catch (e) {
        console.warn(`Could not chmod VS Code executable: ${e}`);
      }
    }

    await runTests({
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