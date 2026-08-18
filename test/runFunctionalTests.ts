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
    // downloadAndUnzipVSCode returns path like: .../Visual Studio Code.app/Contents/MacOS/Electron
    // or .../Visual Studio Code.app/Contents/Resources/app/bin/code on some versions
    if (process.platform === 'darwin') {
      console.log(`VS Code executable path: ${vscodeExecutablePath}`);
      
      // Try to chmod the returned path directly
      try {
        if (fs.existsSync(vscodeExecutablePath)) {
          fs.chmodSync(vscodeExecutablePath, 0o755);
          console.log(`Set permissions on: ${vscodeExecutablePath}`);
        }
      } catch (e) {
        console.warn(`Could not chmod VS Code executable: ${e}`);
      }

      // Also try the Electron binary if the path is to the .app
      if (vscodeExecutablePath.endsWith('.app')) {
        const electronPath = path.join(vscodeExecutablePath, 'Contents', 'MacOS', 'Electron');
        try {
          if (fs.existsSync(electronPath)) {
            fs.chmodSync(electronPath, 0o755);
            console.log(`Set permissions on Electron: ${electronPath}`);
          }
        } catch (e) {
          console.warn(`Could not chmod Electron: ${e}`);
        }
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