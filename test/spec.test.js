//const { strictEqual } = require('assert');
const { assert } = require('chai');
const path = require('path');
const specFolderLocation = './spec_files';
const splunkSpec = require("../out/spec.js");
const extensionPath = path.resolve(__dirname, '../');
const specFileVersion = "9.0";

describe('app.conf', () => {
	let specFileName = "app.conf.spec";
	let specFilePath = path.join(specFolderLocation, specFileVersion, specFileName)
	let specConfig = splunkSpec.getSpecConfig(extensionPath, specFilePath);

	it('stanza "[author=authorname]" should be valid', () => {
		assert.equal(splunkSpec.isStanzaValid(specConfig, "[author=authorname]"), true);
	});
});

describe('authorize.conf', () => {
	let specFileName = "authorize.conf.spec";
	let specFilePath = path.join(specFolderLocation, specFileVersion, specFileName)
	let specConfig = splunkSpec.getSpecConfig(extensionPath, specFilePath);

	it('stanza "[role_org_custom]" should be valid', () => {
		assert.equal(splunkSpec.isStanzaValid(specConfig, "[role_org_custom]"), true);
	});
});

describe('outputs.conf', () => {
	let specFileName = "outputs.conf.spec";
	let specFilePath = path.join(specFolderLocation, specFileVersion, specFileName)
	let specConfig = splunkSpec.getSpecConfig(extensionPath, specFilePath);

	it('setting "useAck = true" should be valid for stanza [tcpout:default-autolb-group]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[tcpout:default-autolb-group]", "useAck = true"), true);
	});
});

describe('authentication.conf', () => {
	let specFileName = "authentication.conf.spec";
	let specFilePath = path.join(specFolderLocation, specFileVersion, specFileName)
	let specConfig = splunkSpec.getSpecConfig(extensionPath, specFilePath);

	it('setting "clientCert = my_valid_string" should be valid for stanza [saml]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[saml]", "clientCert = my_valid_string"), true);
	});
	it('setting "entityId = my_valid_string" should be valid for stanza [saml]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[saml]", "entityId = my_valid_string"), true);
	});
	it('setting "user1 = admin::user1::user1@email.com" should be valid for stanza [userToRoleMap_SAML]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[userToRoleMap_SAML]", "user1 = admin::user1::user1@email.com"), true);
	});
	it('setting "authType = Splunk" should be valid for stanza [authentication]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[authentication]", "authType = Splunk"), true);
	});
});

describe('distsearch.conf', () => {
	let specFileName = "distsearch.conf.spec";
	let specFilePath = path.join(specFolderLocation, specFileVersion, specFileName)
	let specConfig = splunkSpec.getSpecConfig(extensionPath, specFilePath);

	it('stanza "[replicationBlacklist]" should be valid', () => {
		assert.equal(splunkSpec.isStanzaValid(specConfig, "[replicationBlacklist]"), true);
	});

	it('stanza "[default]" should be valid', () => {
		assert.equal(splunkSpec.isStanzaValid(specConfig, "[default]"), true);
	});
});

describe('indexes.conf', () => {
	let specFileName = "indexes.conf.spec";
	let specFilePath = path.join(specFolderLocation, specFileVersion, specFileName)
	let specConfig = splunkSpec.getSpecConfig(extensionPath, specFilePath);

	it('setting "repFactor = auto" should be valid for stanza [default]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[default]", "repFactor = auto"), true);
	});

	it('setting "frozenTimePeriodInSecs = 47347200" should be valid for stanza [default]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[default]", "frozenTimePeriodInSecs = 47347200"), true);
	});

	it('setting "maxHotSpanSecs = 2678400" should be valid for stanza [default]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[default]", "maxHotSpanSecs = 2678400"), true);
	});

	it('setting "maxTotalDataSizeMB = 512000" should be valid for stanza [default]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[default]", "maxTotalDataSizeMB = 512000"), true);
	});

	it('setting "enableDataIntegrityControl = 0" should be valid for stanza [default]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[default]", "enableDataIntegrityControl = 0"), true);
	});

	it('setting "enableTsidxReduction = 0" should be valid for stanza [default]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[default]", "enableTsidxReduction = 0"), true);
	});

	it('setting "bucketRebuildMemoryHint = 0" should be valid for stanza [default]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[default]", "bucketRebuildMemoryHint = 0"), true);
	});

	it('setting "bucketRebuildMemoryHint = auto" should be valid for stanza [default]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[default]", "bucketRebuildMemoryHint = auto"), true);
	});

	it('setting "bucketRebuildMemoryHint = 10MB" should be valid for stanza [default]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[default]", "bucketRebuildMemoryHint = 10MB"), true);
	});

	it('setting "bucketRebuildMemoryHint = 10MBf" should be invalid for stanza [default]', () => {
		assert.notEqual(splunkSpec.isSettingValid(specConfig, "[default]", "bucketRebuildMemoryHint = 10MBf"), true);
	});
});

describe('inputs.conf', () => {
	let specFileName = "inputs.conf.spec";
	let specFilePath = path.join(specFolderLocation, specFileVersion, specFileName)
	let specConfig = splunkSpec.getSpecConfig(extensionPath, specFilePath);

	it('stanza "[script:///opt/splunk/etc/apps/ta-myscript/script.sh]" should be valid', () => {
		assert.equal(splunkSpec.isStanzaValid(specConfig, "[script:///opt/splunk/etc/apps/ta-myscript/script.sh]"), true);
	});
	
	it('setting "disabled = 1" should be valid', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[script:///opt/splunk/etc/apps/ta-myscript/script.sh]", "disabled = 1"), true);
	});

	it('setting "interval = 600" should be valid', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[script://./bin/lsof.sh]", "interval = 600"), true);
	});

	it('setting python.version = python4 should be invalid', () => {
		assert.notEqual(splunkSpec.isSettingValid(specConfig, "[my_modular_input]", "python.version = python4"), true);
	});

	it('setting python.version = python3 should be valid', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[my_modular_input]", "python.version = python3"), true);
	});

	it('setting "interval = 60" should be valid for stanza [WinPrintMon://name]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[WinPrintMon://name]", "interval = 60"), true);
	});

});

describe('searchbnf.conf', () => {
	let specFileName = "searchbnf.conf.spec";
	let specFilePath = path.join(specFolderLocation, specFileVersion, specFileName)
	let specConfig = splunkSpec.getSpecConfig(extensionPath, specFilePath);

	it('setting "syntax = mything" should be valid for stanza [mything-command]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[mything-command]", "syntax = mything"), true);
	});
});

describe('serverclass.conf', () => {
	let specFileName = "serverclass.conf.spec";
	let specFilePath = path.join(specFolderLocation, specFileVersion, specFileName)
	let specConfig = splunkSpec.getSpecConfig(extensionPath, specFilePath);

	it('setting "targetRepositoryLocation = path" should be valid for stanza [serverClass:serverClassName]', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[serverClass:serverClassName]", "targetRepositoryLocation = path"), true);
	});
});

describe('tags.conf', () => {
	let specFileName = "tags.conf.spec";
	let specFilePath = path.join(specFolderLocation, specFileVersion, specFileName)
	let specConfig = splunkSpec.getSpecConfig(extensionPath, specFilePath);

	it('stanza "[eventtype=eventtype]" should be valid', () => {
		assert.equal(splunkSpec.isStanzaValid(specConfig, "[eventtype=eventtype]"), true);
	});

	it('setting "authentication = enabled" should be valid', () => {
		assert.equal(splunkSpec.isSettingValid(specConfig, "[eventtype=eventtype]", "authentication = enabled"), true);
	});
});

describe('ui-tour.conf', () => {
	let specFileName = "ui-tour.conf.spec";
	let specFilePath = path.join(specFolderLocation, specFileVersion, specFileName)
	let specConfig = splunkSpec.getSpecConfig(extensionPath, specFilePath);

	it('stanza "[tour_name]" should be valid', () => {
		assert.equal(splunkSpec.isStanzaValid(specConfig, "[tour_name]"), true);
	});
});