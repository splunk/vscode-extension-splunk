import * as child_process from 'child_process';
import { AddressInfo, Socket } from 'net';
import * as path from 'path';
import {
    StatusBarItem,
    window,
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

export async function startSpl2ClientAndServer(globalStoragePath: string, progressBar: StatusBarItem, portToAttempt: number, onClose: (nextPort: number) => void): Promise<Spl2ClientServer> {
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
            const lspPath = path.join(getLocalLspDir(globalStoragePath), getLspFilename(lspVersion));
            
            const server = new Spl2ClientServer(progressBar, javaPath, lspPath, portToAttempt, onClose);
            await server.initialize();
            resolve(server);
        } catch (err) {
            reject(`Error initializing SPL2, err: ${err}`);
        }
    });
}

export class Spl2ClientServer {
    progressBar: StatusBarItem;
    javaPath: string;
    lspPath: string;
    retries: number;
    restarting: boolean;
    portToAttempt: number;
    onClose: (nextPort: number) => void;
    // Set during initialize():
    lspPort: number;
    client: LanguageClient;
    serverProcess: child_process.ChildProcess;
    socket: Socket;

    constructor(progressBar: StatusBarItem, javaPath: string, lspPath: string, portToAttempt: number, onClose: (nextPort: number) => void) {
        this.progressBar = progressBar;
        this.javaPath = javaPath;
        this.lspPath = lspPath;
        this.retries = 0;
        this.restarting = false;
        this.lspPort = -1;
        this.client = undefined;
        this.serverProcess = undefined;
        this.socket = undefined;
        this.portToAttempt = portToAttempt;
        this.onClose = onClose;
    }

    async initialize(): Promise<void> {
        this.progressBar.text = 'Starting SPL2 Language Server';
        this.progressBar.show();
        return new Promise(async (resolve, reject) => {
            this.lspPort = await getNextAvailablePort(this.portToAttempt, 10)
                .catch((err) => {
                    reject(`Unable to find available port for SPL2 language server, err: ${err}`);
                }) || -1;
            if (this.lspPort === -1) {
                reject(`Unable to find available port for SPL2 language server`);
                return;
            }

            const serverOptions: ServerOptions = this.setupNewServer();
        
            // Options to control the language client
            const clientOptions: LanguageClientOptions = {
                documentSelector: [
                    { language: 'splunk_spl2', pattern: '**∕*.spl2'},
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
                    this.progressBar.text = 'SPL2 Language Server Running';
                } else if (event.newState === State.Starting) {
                    this.progressBar.text = 'SPL2 Language Server Starting';
                } else {
                    this.progressBar.text = 'SPL2 Language Server Stopped';
                }
                this.progressBar.show();
            });
        
            // TODO: spl2/module and spl2/compile are not provided here,
            // though in the future the compile command can be implemented
            // to compile to SPL1 which can then be run on any Splunk deployment

            // Start the client. This will also launch the server
            this.client.start();

            resolve();
        });
    }
    
    setupNewServer(): ServerOptions {
        return (): Promise<StreamInfo> => {
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
                    if (stderr.includes('Cannot invoke "java.net.ServerSocket.close()"')) {
                        if (this.restarting) {
                            return;
                        }
                        // this indicates a socket issue, try next port
                        console.warn('Connection lost, bumping port and retrying ...');
                        this.onClose(this.lspPort + 1);
                    } else if (stderr.includes('Unable to access jarfile')) {
                        // Jar file likely does not exists/permissions insufficient, fail now
                        window.showErrorMessage(
                            `SPL2 Server unable to access jarfile at ${this.lspPath}, ` +
                            'check Splunk Extension Settings');
                        this.deactivate();
                    }
                });
                this.serverProcess.stdout.on('data', stdout => {
                    console.log(`[SPL2 Server]: ${stdout}`);
                    const lspLog: LSPLog = JSON.parse(stdout);
                    if (lspLog.message.includes('started listening on port')) {
                        console.log('SPL2 Server is up, starting client...');
                        // Ready for client
                        this.socket = new Socket();
    
                        this.socket.on('connect', () => {
                            console.log('Client: connection established with server');
                            const address:AddressInfo = this.socket.address() as AddressInfo;
                            console.log(`Client is listening on port ${address.port}`);
                            // Reset retries after a successful connection
                            this.retries = 0;
                            this.restarting = false;
                            resolve({
                                writer: this.socket,
                                reader: this.socket,
                                // detached: true,
                            });
                        });
    
                        this.socket.on('close', () => {
                            if (this.restarting) {
                                return;
                            }
                            this.restarting = true;
                            console.warn('Connection lost, bumping port and retrying ...');
                            this.onClose(this.lspPort + 1);
                        });
    
                        this.socket.on('error', (err) => {
                            if (isNodeError(err) && err.code === 'ECONNRESET') {
                                // expected when server is killed
                                console.log('Server connection ended.');
                                return;
                            }
                            console.warn(`error between LSP client/server encountered -> ${err}`);
                        });
    
                        this.socket.connect({
                            port: this.lspPort,
                        });
                    }
                });
            });
        };
    }

    killServer(): void {
        console.log(`killServer() called`);
        if (this.serverProcess && this.serverProcess.pid) {
            console.log(`Terminating SPL2 Server pid ${this.serverProcess.pid} ...`);
            this.serverProcess.kill();
            this.serverProcess = undefined;
        }
    }
  
    deactivate(): Promise<void> {
        this.progressBar.text = 'SPL2 Language Server deactivated';
        this.progressBar.show();
        try {
            this?.socket.destroy();
            this.killServer();
            if (this?.client?.isRunning()) {
                return this?.client.stop();
            }
        } catch (err) {
            console.warn(`Error deactivating SPL2 client/server, err: ${err}`);
        }
        return Promise.resolve();
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