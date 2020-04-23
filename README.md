# Visual Studio Code Extension for Splunk


The Visual Studio Code Extension for Splunk helps developers create, test, and debug Splunk Enterprise apps, add-ons, custom commands, REST handlers, etc.  The extension helps Splunk administrators edit Splunk .conf files by providing stanza and setting completions as well as setting checking.  For individuals living in Visual Studio Code, integrations are built in to run Splunk searches and display Splunk visualizations in Visual Studio Code.

## Working with .conf files

![Splunk Extension Demo](https://raw.githubusercontent.com/splunk/vscode-extension-splunk/master/images/demo1.gif)

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

## Documentation
Documentation can be found in the [wiki](https://github.com/splunk/vscode-extension-splunk/wiki) hosted on the public repository.

[https://github.com/splunk/vscode-extension-splunk/wiki](https://github.com/splunk/vscode-extension-splunk/wiki)

## Support

This software is released as-is. Splunk provides no warranty and no support on this software.
If you have any issues with the software, please file an issue on the repository.