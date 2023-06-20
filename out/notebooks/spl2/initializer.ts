import * as child_process from 'child_process';
import { AddressInfo, Socket } from 'net';
import * as path from 'path';
import {
    commands,
	Disposable,
    ExtensionContext,
    workspace,
} from 'vscode';
import {
	LanguageClient,
	LanguageClientOptions,
	ServerOptions,
	State,
	StreamInfo,
} from 'vscode-languageclient/node';

import {
    configKeyAcceptedTerms,
    configKeyJavaPath,
    configKeyLspVersion,
    getLocalLspDir,
    getLspFilename,
    TermsAcceptanceStatus,
} from './installer';

interface ModuleItemId {
	kind: string,
	path: []
}

interface ResolveDatasetsParams {
	user: string,
	predicate: string,
	ids: ModuleItemId[]
}

interface ResolveDataset {
	owner: string,
	kind: string,
	id: string,
	path: string[],
	properties: Map<string, object>;
}

interface LSPLog {
	timestamp: string,
	level: string,
	message: string,
}

export async function startSpl2ClientAndServer(context: ExtensionContext): Promise<Spl2ClientServer> {
    return new Promise(async (resolve, reject) => {
        try {
            // If the user has already opted-out for good then stop here
            const termsStatus: TermsAcceptanceStatus = workspace.getConfiguration().get(configKeyAcceptedTerms);
            if (termsStatus === TermsAcceptanceStatus.DeclinedForever) {
                reject(
                    `User opted out of SPL2. To reset this adjust the '${configKeyAcceptedTerms}' ` +
                    `setting to = '${TermsAcceptanceStatus.DeclinedOnce}' in the Splunk Extension Settings.`
                );
                return;
            }
            const javaPath: string = workspace.getConfiguration().get(configKeyJavaPath);
            if (!javaPath) {
                reject(
                    'Error initializing SPL2, please specify a java executable in the Splunk Extension ' +
                    `Settings under '${configKeyJavaPath}'`
                );
                return;
            }
            const lspVersion: string = workspace.getConfiguration().get(configKeyLspVersion);
            if (!lspVersion) {
                reject(
                    'Error initializing SPL2, please specify the language server version in the Splunk ' +
                    `Extension Settings under '${configKeyLspVersion}'`
                );
                return;
            }
            const lspPath = path.join(getLocalLspDir(context), getLspFilename(lspVersion));
            
            const server = new Spl2ClientServer(context, javaPath, lspPath);
            await server.initialize();
            resolve(server);
        } catch (err) {
            reject(`Error initializing SPL2, err: ${err}`);
        }
    });
}

export class Spl2ClientServer {
    context: ExtensionContext;
    javaPath: string;
    lspPath: string;
    // Set during initialize():
    lspPort: number;
    client: LanguageClient;
    serverProcess: child_process.ChildProcess;

    constructor(context:ExtensionContext, javaPath: string, lspPath: string) {
        this.context = context;
        this.javaPath = javaPath;
        this.lspPath = lspPath;
        this.lspPort = -1;
        this.client = undefined;
        this.serverProcess = undefined;
    }

    async initialize(): Promise<void> {
        return new Promise(async (resolve, reject) => {
            // 59143 ~ SPLNK if you squint really hard :)
            this.lspPort = await getNextAvailablePort(59143, 10)
                .catch((err) => {
                    reject(`Unable to find available port for SPL2 language server`);
                }) || -1;
            if (this.lspPort === -1) {
                reject(`Unable to find available port for SPL2 language server`);
                return;
            }

            const serverOptions: ServerOptions = (): Promise<StreamInfo> => {
                return new Promise((resolve, reject) => {
                    const javaArgs: string[] = [
                        '-Xmx2g',
                        '-jar',
                        this.lspPath,
                        '--port',
                        `${this.lspPort}`,
                    ];
                    this.serverProcess = child_process.spawn(this.javaPath, javaArgs);
                    if (!this.serverProcess || !this.serverProcess.pid) {
                        reject(`Launching server with ${this.javaPath} ${javaArgs.join(' ')} failed.`);
                        return;
                    } else {
                        console.log(`SPL2 Language Server launched with pid: ${this.serverProcess.pid} and listening on port: ${this.lspPort}`);
                    }
                    this.serverProcess.stderr.on('data', stderr => {
                        console.warn(`[SPL2 Server]: ${stderr}`);
                    });
                    this.serverProcess.stdout.on('data', stdout => {
                        console.log(`[SPL2 Server]: ${stdout}`);
                        const lspLog: LSPLog = JSON.parse(stdout);
                        if (lspLog.message.includes('started listening on port')) {
                            console.log('SPL2 Server is up, starting client...');
                            // Ready for client
                            const socket = new Socket();
        
                            socket.on('connect', () => {
                                console.log('Client: connection established with server');
                                const address:AddressInfo = socket.address() as AddressInfo;
                                console.log(`Client is listening on port ${address.port}`);
                                resolve({
                                    writer: socket,
                                    reader: socket,
                                });
                            });
        
                            socket.on('close', () => {
                                setTimeout(() => {
                                    // TODO: fail after X attempts rather than retrying indefinitely
                                    console.log('Retrying connection');
                                    commands.executeCommand('workbench.action.reloadWindow');
                                }, 500);
                            });
        
                            socket.on('error', (err) => {
                                if (isNodeError(err) && err.code === 'ECONNRESET') {
                                    // expected when server is killed
                                    console.log('Server connection ended.');
                                    return;
                                }
                                console.warn(`error between LSP client/server encountered -> ${err}`);
                            });
        
                            socket.connect({
                                port: this.lspPort,
                            });
                        }
                    });
                });
            };
        
            // Options to control the language client
            const clientOptions: LanguageClientOptions = {
                documentSelector: [
                    { language: 'splunk_spl2' },
                ],
                initializationOptions: { profile: null },
            };
        
            // Create the language client and start the client.
            this.client = new LanguageClient(
                'spl2_client',
                'SPL2 Language Client',
                serverOptions,
                clientOptions
            );
        
            // Attach handlers for catalog item resolution.
            this.client.onDidChangeState((event) => {
                if (event.newState === State.Running) {
                    this.client.onRequest('spl/resolveDatasets', (resolveDatasetsParams: ResolveDatasetsParams): ResolveDataset[] => {
                        const id = resolveDatasetsParams.ids[0];
                        // TODO: implement dataset resolution based on existing indexes/datasets within module
                        return [];
                    });
        
                    this.client.onRequest('spl/resolveModule', (): void => {
                        // TODO: implement module resolution
                        return;
                    });
                }
            });
        
            // TODO: spl2/module and spl2/compile are not provided here,
            // though in the future the compile command can be implemented
            // to compile to SPL1 which can then be run on any Splunk deployment

            this.context.subscriptions.push(new Disposable(() => this.killServer()));
        
            // Start the client. This will also launch the server
            this.client.start();

            resolve();
        });
    }

    killServer(): void {
        if (this.serverProcess && this.serverProcess.pid) {
            console.log(`Terminating SPL2 Server pid ${this.serverProcess.pid} ...`);
            this.serverProcess.kill();
            this.serverProcess = undefined;
        }
    }
  
    deactivate(): Thenable<void> | undefined {
        this.killServer();
        if (!this.client) {
            return undefined;
        }
        return this.client.stop();
    }
}
  
/**
 * Helper to retrieve a socket using the supplied port and incrementing up
 * to maxAttempts
 * @param startPort Port to use to start testing with
 * @param attempts How many attempts to increment port before failing (default: 10)
 * @returns Promise<Socket> Socket with available port
 */
async function getNextAvailablePort(startPort: number, attempts: number): Promise<number> {
    const maxAttempts = attempts || 10;
    let attemptPort = startPort;
    const isSocketInUse = (port: number): Promise<boolean> => {
        return new Promise((resolve, reject) => {
            const socket = new Socket();
            socket.on('connect', () => {
                // If we connect then this implies the port is in use and listening
                socket.destroy();
                console.log(`Port ${port} in use`);
                resolve(true);
            });
    
            const timeoutMs = 400;
            socket.setTimeout(timeoutMs); // wait 400 ms before giving up
            socket.on('timeout', () => {
                // If we time out, assume port is unoccupied
                socket.destroy();
                console.log(`Port ${port} available (timeout)`);
                resolve(false);
            });
  
            socket.on('error', (err) => {
                socket.destroy();
                if (isNodeError(err) && err.code === 'ECONNREFUSED') {
                    // no connection implies this is not in use
                    console.log(`Port ${port} available`);
                    resolve(false);
                    return;
                }
                console.log(`Error connecting to ${port} err -> ${err}`);
                reject(err); // otherwise we seem to be erroring out for other reasons
            });
  
            console.log(`Trying port ${port} ...`);
            socket.connect(port);
      });
    };
  
    let socketInUse = true;
    while (socketInUse && attemptPort < startPort + maxAttempts) {
        socketInUse = await isSocketInUse(attemptPort);
        if (socketInUse) {
            attemptPort++;
        }
    }
    return new Promise((resolve, reject) => {
        if (socketInUse) {
            reject(`Unable to find available port after ${maxAttempts} attempts`);
            return;
        }
        resolve(attemptPort);
    });
  }
  
  /**
   * Convenience function to correctly type NodeJS errors that will
   * have properties such as 'code' as opposed to vanilla JS errors.
   * @param error Generic error to check for NodeJS.ErrnoException type
   * @returns Bool if error is a NodeJS error with associated properties
   */
  function isNodeError(error: Error): error is NodeJS.ErrnoException {
    return error instanceof Error;
  }