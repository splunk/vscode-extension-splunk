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
    let vscodeExecutablePath = await downloadAndUnzipVSCode('stable');

    // Fix for macOS: VS Code renamed the binary from "Electron" to "Code"
    // The @vscode/test-electron library may return the wrong path
    if (process.platform === 'darwin') {
      if (!fs.existsSync(vscodeExecutablePath) && vscodeExecutablePath.endsWith('Electron')) {
        const codePath = vscodeExecutablePath.replace(/Electron$/, 'Code');
        if (fs.existsSync(codePath)) {
          vscodeExecutablePath = codePath;
        }
      }

      try {
        if (fs.existsSync(vscodeExecutablePath)) {
          fs.chmodSync(vscodeExecutablePath, 0o755);
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