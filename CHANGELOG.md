# Change Log

## [0.2.5]
- An update to Visual Studio Code changed how Diagnostics are initialized which broke linting. Version 0.2.5 addresses this issue.

## [0.2.4]
- Fixed an issue when running ad-hoc searches from the command palette.
- Fixed an issue displaying invalid interval for `script:/// stanzas`.  Issue [#21](https://github.com/splunk/vscode-extension-splunk/issues/21)
- Added support for 'disabled' settings in inputs.conf since 'disabled' is a valid setting, but it is not specified in the spec file.  Issue [#18](https://github.com/splunk/vscode-extension-splunk/issues/18)
- Fixed an issue where prefix stanzas where not recognized.  Examples: `[author=<name>]` [#22](https://github.com/splunk/vscode-extension-splunk/issues/22), `[eventtype=name]` [#24](https://github.com/splunk/vscode-extension-splunk/issues/24), `[role_<name>]` [#28](https://github.com/splunk/vscode-extension-splunk/issues/28)

## [0.2.3]
- Added support for multi-line values in .conf files.  See issue [#12](https://github.com/splunk/vscode-extension-splunk/issues/12)
- Fix for "The URL specified for the Splunk REST API is incorrect". See issue [#14](https://github.com/splunk/vscode-extension-splunk/issues/14)

## [0.2.2]
- Added configuration checking for .conf file values:
  - `<boolean>`
  - `<0 or positive integer>`, `<unsigned integer>`, `<positive integer>`, `<non-negative integer>`
  - `<int>`, `<integer>`
  - `<decimal number>`, `<number>`, `<unsigned long>`, `<decimal>`, `<double>`
  
- Removed dependency on Remote SSH extension - this caused issues on systems using WSL.  See issue [#3](https://github.com/splunk/vscode-extension-splunk/issues/3).
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
