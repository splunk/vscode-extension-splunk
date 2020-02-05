# Change Log

## [0.2.1]
- Added configuration checking for .conf file values:
  - `<boolean>`
  - `<0 or positive integer>`, `<unsigned integer>`, `<positive integer>`, `<non-negative integer>`
  - `<int>`, `<integer>`
  - `<decimal number>`, `<number>`, `<unsigned long>`, `<decimal>`, `<double>`
  
- Removed dependency on Remote SSH extension - this caused issues on systems using WSL.  See issue [#3](https://github.com/splunk/vscode-extension-splunk/issues/3).

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