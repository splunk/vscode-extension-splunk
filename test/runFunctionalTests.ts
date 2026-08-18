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
    if (process.platform === 'darwin') {
      console.log(`VS Code executable path: ${vscodeExecutablePath}`);
      console.log(`File exists: ${fs.existsSync(vscodeExecutablePath)}`);
      
      // Check file stats
      try {
        const stats = fs.statSync(vscodeExecutablePath);
        console.log(`File mode before chmod: ${stats.mode.toString(8)}`);
      } catch (e) {
        console.log(`Could not stat file: ${e}`);
      }

      // Try to chmod the returned path directly
      try {
        fs.chmodSync(vscodeExecutablePath, 0o755);
        console.log(`Set permissions on: ${vscodeExecutablePath}`);
        const statsAfter = fs.statSync(vscodeExecutablePath);
        console.log(`File mode after chmod: ${statsAfter.mode.toString(8)}`);
      } catch (e) {
        console.warn(`Could not chmod VS Code executable: ${e}`);
      }

      // List the directory contents to debug
      try {
        const dir = path.dirname(vscodeExecutablePath);
        const files = fs.readdirSync(dir);
        console.log(`Contents of ${dir}: ${files.join(', ')}`);
      } catch (e) {
        console.log(`Could not list directory: ${e}`);
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