import * as cp from 'child_process';
import * as path from 'path';
import {
  downloadAndUnzipVSCode,
  resolveCliArgsFromVSCodeExecutablePath,
  runTests
} from '@vscode/test-electron';
import { version } from '../package.json';

// We refer to these as acceptance tests because they are executed against the actual compiled
// and webpacked .vsix file that's a potential release candidate.
// Example taken from: https://code.visualstudio.com/api/working-with-extensions/testing-extension#custom-setup-with-vscodetestelectron
async function main() {
  try {
    const extensionDevelopmentPath = path.resolve(__dirname, '..'); // root of repo
    const acceptanceTestsPath = path.resolve(__dirname, './acceptance/index');
    const vscodeExecutablePath = await downloadAndUnzipVSCode('stable');
    const [cliPath, ...args] = resolveCliArgsFromVSCodeExecutablePath(vscodeExecutablePath);

    // Use cp.spawn / cp.exec for custom setup
    cp.spawnSync(
      cliPath,
      [...args, '--install-extension', `splunk-${version}.vsix`], //TODO: use ${packageJSON.version}
      {
        encoding: 'utf-8',
        stdio: 'inherit'
      }
    );

    // Run the extension test
    await runTests({
      // Use the specified `code` executable
      vscodeExecutablePath,
      extensionDevelopmentPath,
      extensionTestsPath: acceptanceTestsPath
    });
  } catch (err) {
    console.error(`Failed to run tests: ${err}`);
    process.exit(1);
  }
}

main();
