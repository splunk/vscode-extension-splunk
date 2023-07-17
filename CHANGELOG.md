# Change Log

Complete documentation is available at the [extension wiki](https://github.com/splunk/vscode-extension-splunk/wiki)

## [0.3.1]
Minor updates to SPL language server handling.

## [0.3.0]
### New Features
- Added SPL Notebook functionality.  Splunk Notebooks provide the ability to author SPL Notes, execute SPL Notes as search jobs, and view results in Visual Studio Code.

### Issues fixed
- Updated setting checking for additional types. Issues [#74](https://github.com/splunk/vscode-extension-splunk/issues/74) and [#84](https://github.com/splunk/vscode-extension-splunk/issues/84)
- Added hander for setting changes. Issue [#80](https://github.com/splunk/vscode-extension-splunk/issues/80) 
- Updated stanza separator handling. Issues [#71](https://github.com/splunk/vscode-extension-splunk/issues/71), [#72](https://github.com/splunk/vscode-extension-splunk/issues/72), [#73](https://github.com/splunk/vscode-extension-splunk/issues/73) and [#75](https://github.com/splunk/vscode-extension-splunk/issues/75)
- Updated handling of `inputs.conf`. Issue [#71](https://github.com/splunk/vscode-extension-splunk/issues/71)
- Updated SSL setting handling to address the error message “Could not enumerate saved searches. self signed certificate in certificate chain". Issue [#69](https://github.com/splunk/vscode-extension-splunk/issues/69)
 

## [0.2.10]
- Added spec files for Splunk 9.0
- Added CIM tags to auto complete and linting when editing tags.conf. Issue [#25](https://github.com/splunk/vscode-extension-splunk/issues/25)
- Fixed issue where free form stanza settings appeared invalid. Issue [#60](https://github.com/splunk/vscode-extension-splunk/issues/60)
- Fixed issue that marked some `[default]` stanzas as invalid. Issue [#62](https://github.com/splunk/vscode-extension-splunk/issues/62)
- Fixed issue that marked python.version settings invalid for modular inputs in inputs.conf. Issue [#50](https://github.com/splunk/vscode-extension-splunk/issues/50)
- Fixed issues with searchbnf.conf files. Issue [#49](https://github.com/splunk/vscode-extension-splunk/issues/49)
- Added version to spec config object so that special version comparisons and fixes can be implemented. See issue [#53](https://github.com/splunk/vscode-extension-splunk/issues/53)
- Added option to enable certificate verification. See issue [#63](https://github.com/splunk/vscode-extension-splunk/issues/63)

## [0.2.8]
- Added spec files for Splunk 8.1 and 8.2
- Slight code refactor to support unit testing. Also, Mocha unit tests were added.
- Fixed issue where settings containing curly braces (`{}`) did not render choices. Issue [#40](https://github.com/splunk/vscode-extension-splunk/issues/40)
- Fixed syntax highlighting issue for settings that contain a comma (`,`). Issue [#42](https://github.com/splunk/vscode-extension-splunk/issues/42)
- Added support for `eventgen.conf` files. Issue [#27](https://github.com/splunk/vscode-extension-splunk/issues/27)
- Replaced [request](https://www.npmjs.com/package/request) package with [axios](https://www.npmjs.com/package/axios) since request has been deprecated.
- Added dynamic snippets. Issue [#20](https://github.com/splunk/vscode-extension-splunk/issues/20)
- Added snippets for globalConfig.json files.

## [0.2.6]
- Fixed an issue where setting names contained `<name>`. Issue [#33](https://github.com/splunk/vscode-extension-splunk/issues/33)
- Fixed an issue reading serverclass.conf.spec. Issue [#35](https://github.com/splunk/vscode-extension-splunk/issues/35)
- Fixed a Windows path issue when creating custom search commands, custom REST handlers, and modular visualizations. Issue [#36](https://github.com/splunk/vscode-extension-splunk/issues/36)
- Added functionality to preview the UI that [ucc-gen](https://github.com/splunk/addonfactory-ucc-generator) creates from `globalConfig.json`. To use this functionality, create a `globalConfig.json` file ([reference](https://github.com/splunk/addonfactory-ucc-generator/blob/main/tests/data/globalConfig.json)), then right-click and choose Preview globalConfig.json.

![Preview globalConfig.json](https://raw.githubusercontent.com/wiki/splunk/vscode-extension-splunk/images/previewGlobalConfig.png)

## [0.2.5]
- An update to Visual Studio Code changed how Diagnostics are initialized which broke linting. Version 0.2.5 addresses this issue.

## [0.2.4]
- Fixed an issue when running ad-hoc searches from the command palette.
- Fixed an issue displaying invalid interval for `script:/// stanzas`. Issue [#21](https://github.com/splunk/vscode-extension-splunk/issues/21)
- Added support for 'disabled' settings in inputs.conf since 'disabled' is a valid setting, but it is not specified in the spec file. Issue [#18](https://github.com/splunk/vscode-extension-splunk/issues/18)
- Fixed an issue where prefix stanzas were not recognized. Examples: `[author=<name>]` [#22](https://github.com/splunk/vscode-extension-splunk/issues/22), `[eventtype=name]` [#24](https://github.com/splunk/vscode-extension-splunk/issues/24), `[role_<name>]` [#28](https://github.com/splunk/vscode-extension-splunk/issues/28)

## [0.2.3]
- Added support for multi-line values in .conf files. See issue [#12](https://github.com/splunk/vscode-extension-splunk/issues/12)
- Fix for "The URL specified for the Splunk REST API is incorrect". See issue [#14](https://github.com/splunk/vscode-extension-splunk/issues/14)

## [0.2.2]
- Added configuration checking for .conf file values:
- `<boolean>`
- `<0 or positive integer>`, `<unsigned integer>`, `<positive integer>`, `<non-negative integer>`
- `<int>`, `<integer>`
- `<decimal number>`, `<number>`, `<unsigned long>`, `<decimal>`, `<double>`
- Removed dependency on Remote SSH extension - this caused issues on systems using WSL. See issue [#3](https://github.com/splunk/vscode-extension-splunk/issues/3).
- Added a command to create a custom Splunk REST handler:
- `splunk.new.resthandler` - creates scaffolding for a custom Splunk REST handler

## [0.2.0]

- Added the following commands:
- `splunk.search.adhoc` - run an ad-hoc search. Results render in Splunk channel in the OUTPUT view tab.
- `splunk.savedSearch.run` - runs a Splunk saved search. Results render in Splunk channel in the OUTPUT view tab.
- `splunk.savedSearches.refresh` - requests Saved searches from the configured Splunk instance.
- `splunk.new.modviz` - creates scaffolding for a Splunk custom visualization.
- `splunk.new.command` - creates scaffolding for a Splunk custom search command.
- `splunk.embeddedReport.show` - shows a Splunk embedded report in a Visual Studio Code panel.

- Added the following views:
- `savedSearches` - displays Splunk saved searches in the Splunk view container
- `embeddedReports` - displays Splunk embedded reports in the Splunk view container


## [0.1.0]

- Initial release
- Grammar adapted from the [Sublime Text syntax highlighting for .conf files](https://github.com/shakeelmohamed/sublime-splunk-conf-highlighting) repo.