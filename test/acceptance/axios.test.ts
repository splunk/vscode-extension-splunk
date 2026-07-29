import * as assert from 'assert';
import * as http from 'http';
import { AddressInfo } from 'net';
import * as vscode from 'vscode';

// searchProvider.js re-reads vscode config on every `new SearchProvider()` / `new SavedSearchProvider()`,
// so it's safe to require at module load time.
const { SearchProvider, SavedSearchProvider } = require('../../searchProvider.js');

type RouteHandler = (req: http.IncomingMessage, res: http.ServerResponse, pathname: string) => void;

function sendJson(res: http.ServerResponse, status: number, body: unknown) {
	const payload = JSON.stringify(body);
	res.writeHead(status, { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) });
	res.end(payload);
}

function sendText(res: http.ServerResponse, status: number, body: string) {
	res.writeHead(status, { 'Content-Type': 'text/plain', 'Content-Length': Buffer.byteLength(body) });
	res.end(body);
}

// Drain the request body before responding so axios doesn't hang waiting on the socket.
function drain(req: http.IncomingMessage, respond: () => void) {
	req.resume();
	req.on('end', respond);
}

async function findUnusedPort(): Promise<number> {
	const probe = http.createServer();
	await new Promise<void>((resolve) => probe.listen(0, resolve));
	const port = (probe.address() as AddressInfo).port;
	await new Promise<void>((resolve) => probe.close(() => resolve()));
	return port;
}

suite('axios workflows (searchProvider, reload) acceptance', () => {
	let server: http.Server;
	let baseUrl: string;
	let unreachableUrl: string;
	let routeHandler: RouteHandler = (_req, res) => sendText(res, 404, 'not found');

	let capturedErrors: string[] = [];
	let capturedInfos: string[] = [];
	let originalShowErrorMessage: any;
	let originalShowInformationMessage: any;
	let originalConfig: Record<string, unknown> = {};

	const CONFIG_KEYS = [
		'splunk.commands.splunkRestUrl',
		'splunk.commands.token',
		'splunk.search.searchOutputMode',
		'splunk.commands.enableCertificateVerification'
	];

	suiteSetup(async () => {
		server = http.createServer((req, res) => {
			const pathname = (req.url || '').split('?')[0];
			// Deterministically report a version new enough that both searchProvider call sites use the v2 export API.
			if (pathname === '/services/server/info') {
				drain(req, () => sendJson(res, 200, { generator: { version: '9.2.0', instance_type: 'enterprise' } }));
				return;
			}
			drain(req, () => routeHandler(req, res, pathname));
		});
		await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve));
		baseUrl = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
		unreachableUrl = `http://127.0.0.1:${await findUnusedPort()}`;

		const config = vscode.workspace.getConfiguration();
		for (const key of CONFIG_KEYS) {
			originalConfig[key] = config.get(key);
		}
		await config.update('splunk.commands.splunkRestUrl', baseUrl, true);
		await config.update('splunk.commands.token', 'test-token', true);
		await config.update('splunk.search.searchOutputMode', 'json', true);
		await config.update('splunk.commands.enableCertificateVerification', false, true);

		originalShowErrorMessage = vscode.window.showErrorMessage;
		originalShowInformationMessage = vscode.window.showInformationMessage;
		(vscode.window as any).showErrorMessage = (msg: string) => { capturedErrors.push(msg); return Promise.resolve(undefined); };
		(vscode.window as any).showInformationMessage = (msg: string) => { capturedInfos.push(msg); return Promise.resolve(undefined); };
	});

	suiteTeardown(async () => {
		(vscode.window as any).showErrorMessage = originalShowErrorMessage;
		(vscode.window as any).showInformationMessage = originalShowInformationMessage;
		const config = vscode.workspace.getConfiguration();
		for (const key of CONFIG_KEYS) {
			await config.update(key, originalConfig[key], true);
		}
		await new Promise<void>((resolve) => server.close(() => resolve()));
	});

	setup(() => {
		capturedErrors = [];
		capturedInfos = [];
		routeHandler = (_req, res) => sendText(res, 404, 'not found');
	});

	test('SearchProvider.runSearch() returns response data on success', async () => {
		routeHandler = (_req, res, pathname) => {
			assert.ok(pathname.endsWith('/jobs/export'), `unexpected pathname ${pathname}`);
			sendText(res, 200, 'search results text');
		};
		const provider = new SearchProvider();
		const result = await provider.runSearch('index=main');
		assert.strictEqual(result, 'search results text');
		assert.strictEqual(capturedErrors.length, 0);
	});

	test('SearchProvider.runSearch() surfaces response body via error.response?.data on HTTP error', async () => {
		routeHandler = (_req, res) => sendText(res, 400, 'Invalid search query');
		const provider = new SearchProvider();
		const result = await provider.runSearch('index=main | this is not valid');
		assert.strictEqual(result, 'No results');
		assert.strictEqual(capturedErrors.length, 1);
		assert.match(capturedErrors[0], /Invalid search query/);
		assert.match(capturedErrors[0], /400/);
	});

	test('SearchProvider.runSearch() falls back to empty details when the request never gets a response', async () => {
		const config = vscode.workspace.getConfiguration();
		await config.update('splunk.commands.splunkRestUrl', unreachableUrl, true);
		try {
			const provider = new SearchProvider();
			// error.response is undefined for connection failures; runSearch must not throw despite that.
			const result = await provider.runSearch('index=main');
			assert.strictEqual(result, 'No results');
			assert.strictEqual(capturedErrors.length, 1);
			assert.doesNotMatch(capturedErrors[0], /undefined/);
		} finally {
			await config.update('splunk.commands.splunkRestUrl', baseUrl, true);
		}
	});

	test('SavedSearchProvider.runSavedSearch() returns response data on success', async () => {
		routeHandler = (_req, res, pathname) => {
			assert.ok(pathname.endsWith('/jobs/export'), `unexpected pathname ${pathname}`);
			sendText(res, 200, 'saved search results text');
		};
		const provider = new SavedSearchProvider();
		const result = await provider.runSavedSearch({ label: 'My Saved Search', owner: 'admin', app: 'search' });
		assert.strictEqual(result, 'saved search results text');
		assert.strictEqual(capturedErrors.length, 0);
	});

	test('SavedSearchProvider.runSavedSearch() surfaces response body via error.response?.data on HTTP error', async () => {
		routeHandler = (_req, res) => sendText(res, 500, 'Internal search error');
		const provider = new SavedSearchProvider();
		const result = await provider.runSavedSearch({ label: 'My Saved Search', owner: 'admin', app: 'search' });
		assert.strictEqual(result, 'No results');
		assert.strictEqual(capturedErrors.length, 1);
		assert.match(capturedErrors[0], /Internal search error/);
	});

	test('SavedSearchProvider.getSavedSearches() lists only enabled searches', async () => {
		routeHandler = (_req, res) => sendJson(res, 200, {
			entry: [
				{ name: 'enabled-search', acl: { app: 'search', owner: 'admin' }, links: {}, content: { disabled: false } },
				{ name: 'disabled-search', acl: { app: 'search', owner: 'admin' }, links: {}, content: { disabled: true } }
			]
		});
		const provider = new SavedSearchProvider();
		const results = await provider.getSavedSearches();
		assert.strictEqual(results.length, 1);
		assert.strictEqual(results[0].label, 'enabled-search');
		assert.strictEqual(capturedErrors.length, 0);
	});

	test('SavedSearchProvider.getSavedSearches() reports a connection-specific message on ECONNREFUSED', async () => {
		const config = vscode.workspace.getConfiguration();
		await config.update('splunk.commands.splunkRestUrl', unreachableUrl, true);
		try {
			const provider = new SavedSearchProvider();
			const results = await provider.getSavedSearches();
			assert.strictEqual(results.length, 0);
			assert.strictEqual(capturedErrors.length, 1);
			assert.match(capturedErrors[0], /Could not connect to Splunk server/);
		} finally {
			await config.update('splunk.commands.splunkRestUrl', baseUrl, true);
		}
	});

	suite('reload.js fullDebugRefresh()', () => {
		// reload.js reads splunk.commands.splunkRestUrl/token at require-time (module-level consts),
		// so it must be required only after config points at our fake server.
		let fullDebugRefresh: (channel: { appendLine: (s: string) => void; show: () => void }) => Promise<void>;

		suiteSetup(() => {
			({ fullDebugRefresh } = require('../../commands/reload.js'));
		});

		test('reloads all handlers except auth-services on success', async () => {
			routeHandler = (req, res, pathname) => {
				if (pathname === '/services/admin') {
					sendJson(res, 200, { entry: [{ name: 'entryA', links: { _reload: '/services/admin/entryA/_reload' } }] });
				} else if (pathname === '/services/data/ui') {
					sendJson(res, 200, {
						entry: [
							{ name: 'auth-services', links: { _reload: '/services/data/ui/auth-services/_reload' } },
							{ name: 'entryB', links: { _reload: '/services/data/ui/entryB/_reload' } }
						]
					});
				} else if (req.method === 'POST' && pathname.endsWith('/_reload')) {
					sendJson(res, 200, {});
				} else {
					sendText(res, 404, 'not found');
				}
			};
			const lines: string[] = [];
			await fullDebugRefresh({ appendLine: (s: string) => lines.push(s), show: () => {} });
			assert.strictEqual(capturedErrors.length, 0);
			assert.strictEqual(capturedInfos.length, 1);
			assert.match(capturedInfos[0], /Performed _reload on 2 EAI handlers/);
			assert.ok(lines.some(l => l.includes('entryA')));
			assert.ok(lines.some(l => l.includes('entryB')));
			assert.ok(!lines.some(l => l.includes('auth-services')));
		});

		test('shows an error message instead of throwing when the initial handler query fails', async () => {
			routeHandler = (_req, res, pathname) => {
				if (pathname === '/services/admin') {
					sendText(res, 500, 'server error enumerating handlers');
				} else {
					sendJson(res, 200, { entry: [] });
				}
			};
			const lines: string[] = [];
			await fullDebugRefresh({ appendLine: (s: string) => lines.push(s), show: () => {} });
			assert.strictEqual(lines.length, 0);
			assert.strictEqual(capturedInfos.length, 0);
			assert.strictEqual(capturedErrors.length, 1);
			assert.match(capturedErrors[0], /Could not enumerate handlers to refresh/);
		});
	});
});
