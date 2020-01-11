# Visual Studio Code Extension for Splunk

The Visual Studio Code Extension for Splunk helps developers create, test, and debug Splunk Enterprise apps, add-ons, custom commands, REST handlers, etc.  The extension helps Splunk administrators edit Splunk .conf files by providing stanza and setting completions as well as setting checking.  For individuals living in Visual Studio Code, integrations are built in to run Splunk searches and display Splunk visualizations in Visual Studio Code.

## Working with .conf files

![Splunk Extension Demo](images/demo1.gif)

* Syntax highlighting for .conf files
* IntelliSense for stanzas and parameters
* Stanza folding
* Linting

## Running Saved Searches

Visual Studio Code communicates with the Splunk REST API to enumerate saved searches and displays the reports in the editor.

![Splunk Saved Search](https://raw.githubusercontent.com/wiki/splunk/vscode-extension-splunk/images/saved_search_activity_bar.gif)



## Viewing Reports

Visual Studio Code communicates with the Splunk REST API to enumerate reports and displays the reports in the editor.

![Splunk Report](https://raw.githubusercontent.com/wiki/splunk/vscode-extension-splunk/images/embedded_view.gif)


This extension also provides capabilities for debugging user-generated Python code run by Splunk Enterprise (local or remote):

* Debug configurations
* Breakpoints
* Step into/over
* Variable inspection

Splunk Enterprise can be running on the same machine as Visual Studio Code, on a remote machine, or in a public cloud provider.


## Support

This software is released as-is. Splunk provides no warranty and no support on this software.
If you have any issues with the software, please file an issue on the repository.

## Release Notes


### 0.2.0

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

### 0.1.0

Initial release

* Grammar adapted from the [Sublime Text syntax highlighting for .conf files](https://github.com/shakeelmohamed/sublime-splunk-conf-highlighting) repo.