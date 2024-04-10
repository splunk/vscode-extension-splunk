#   Version 9.2.0
#
############################################################################
# OVERVIEW
############################################################################
# This file contains descriptions of Splunk Web features used to configure
# Splunk Enterprise. You can use the settings to configure Splunk Web features.
# These features are replicated in a search head cluster environment.
#
# Each stanza controls a different web feature.
#
# For more information on configuration files, including precedence, search for
# "Use Splunk Web to manage configuration files" in the Admin Manual in the Splunk Docs.

[feature:search_v2_endpoint]

enable_search_v2_endpoint = <boolean>
* Determines whether Splunk Web uses the v2 search endpoint.
* A value of "true" means Splunk Web will use the v2 search endpoint.
* Default: true

[feature:quarantine_files]

enable_jQuery2 = <boolean>
* DEPRECATED.
* Determines whether or not Splunk Web can use jQuery 2 JavaScript files
  packaged with the Splunk platform.
* A "false" value means Splunk Web cannot use jQuery 2 JavaScript files
  packaged with the Splunk platform.
* CAUTION: Do not change this setting.
* Default: false

enable_unsupported_hotlinked_imports = <boolean>
* Determines whether or not Splunk Web can use unsupported JavaScript
  files that the Splunk platform will delete in a future release.
* Unsupported hotlinked imports are dependencies in your Simple XML Custom
  JavaScript Extensions that directly reference Splunk software.
* A "false" value means Splunk Web cannot use hotlinked imports
  that the Splunk platform will delete in a future release.
* CAUTION: Do not change this setting.
* Default: false

[feature:dashboards_csp]

enable_dashboards_external_content_restriction = <boolean>
* Whether or not Splunk Web restricts the loading of external content in Studio Dashboards or
  Classic Dashboards.
* A value of "true" means the following:
  * For Studio Dashboards, Splunk Web sets the Content-Security-Policy header, causing the
    browser to block images from external domains not included in the Dashboards Trusted
    Domains List (DTDL).
  * For Classic Dashboards, when the user loads a dashboard with external URLs not included
    in the DTDL, the user sees a warning modal. The user can decide to load the dashboard
    with external content or without external content.
* A value of "false" means the following:
  * For Studio Dashboards, Splunk Web does not set the Content-Security-Policy header. All
    external images load as usual and the browser does not block images.
  * For Classic Dashboards, all external content loads without warnings.
* Default: true

enable_dashboards_redirection_restriction = <boolean>
* Whether or not Splunk Web restricts redirecting to external content from Studio Dashboards or
  Classic Dashboards.
* A value of "true" means that the user sees a warning modal when redirecting to an external
  URL not included in the Dashboards Trusted Domains List. The user has the option to continue
  with the redirect or to cancel the redirect.
* A value of "false" means that nothing warns the user when redirecting to an external URL.
* Default: true

dashboards_trusted_domain.<name> = <string>
* A list of external domains that Splunk Web trusts for content loads and redirects. This list is
  called the Dashboards Trusted Domains List (DTDL).
* You must prefix each trusted domain on its own line with the string "dashboards_trusted_domain."
* The list has a maximum size of 6500 characters, after which any excess content will be ignored.
* If web-features.conf:'enable_dashboards_external_content_restriction' has a value of "true",
  then the following happens:
  * In Studio Dashboards, Splunk Web includes the DTDL in the Content-Security-Policy (CSP) page
    header.
    * The CSP header determines which domains Studio Dashboard can use to load images.
    * By default, 'self', data:, and blob: are added to the CSP header.
    * The browser prevents the loading of images from URLs not within the DTDL.
  * In Classic Dashboards, if the dashboard uses external URLs not included in the DTDL to load
    content, the user sees a warning modal.
* If web-features.conf:'enable_dashboards_external_content_restriction' has a value of "false" then
  the DTDL does not effect Dashboard loading and external content loads without warning.
* If web-features.conf:'enable_dashboards_redirection_restriction' has a value of "true", users
  see a warning modal when redirecting to an external URL not included in the DTDL.
* If web-features.conf:'enable_dashboards_redirection_restriction' has a value of "false" then the
  DTDL does not affect when a user redirects to an external URL, and no warning modal appears.
* Examples:
  * Only allow images from splunk.com and mozilla.org:
      dashboards_trusted_domain.endpoint1 = www.splunk.com
      dashboards_trusted_domain.endpoint2 = www.mozilla.org
  * Allow images from all external domains:
      dashboards_trusted_domain.endpoint1 = *
  * Only allow images starting with splunk.com/download/
      dashboards_trusted_domain.endpoint1 = www.splunk.com/download/
* Further documentation can be found by:
  * searching for "Content Security Policy" on the Mozilla Developer Network Docs website.
  * searching for and reading the Content Security Policy Quick Reference Guide.
* Default: Not set

internal.dashboards_trusted_domain.<name> = <string>
* A list of internal domains that Splunk Web trusts for content loading and redirection. When
  checking for URL trustworthiness, these domains combine with the Dashboards Trusted Domains
  List. Refer to web-features.conf:'dashboards_trusted_domain.<name>' for information on usage.
* Do not modify these values.
* Default: List of trusted Splunk Platform domains.

[feature:highcharts_accessibility]

disable_highcharts_accessibility = <boolean>
* Disable accessibility module in the highcharts charting library.
* DEPRECATED.
* A value of "true" means that Splunk Web will not use the accessibility module in the Highcharts
  charting library.
* CAUTION: Do not change this setting.
* Default: true

[feature:dashboard_studio]

activate_conversion_report = <boolean>
* Controls whether conversion related information is added to the XML of Studio Dashboards
* converted from Classic Dashboards.
* A value of "true" means that conversion information is added to Studio Dashboards.
* Do not modify this value.
* Default: true

enable_inputs_on_canvas = <boolean>
* Allows inputs directly on the canvas in Dashboard Studio.
* A value of "true" will allow inputs directly on the dashboard canvas in Dashboard Studio.
* Do not modify this value.
* Default: true

enable_show_hide = <boolean>
* Allows absolute "Show/Hide" panels in Dashboard Studio.
* A value of "true" will allow "Show/Hide" panels in the editor of Dashboard Studio.
* Do not modify this value.
* Default: true

enable_events_viz = <boolean>
* Allows "splunk.events" visualization type in Dashboard Studio.
* A value of "true" means the "splunk.events" visualization type is available in Dashboard Studio.
* Do not modify this value.
* Default: true

activate_workflow_actions_for_events_viz = <boolean>
* Allows workflow actions in the events visualization in Dashboard Studio.
* A value of "true" means that workflow actions will appear on the events visualization in Dashboard Studio.
* Do not modify this value.
* Default: true

activate_link_to_report = <boolean>
* Allows the Link to Report Interaction in Dashboard Studio.
* A value of "true" means the Link to Report Interaction is available in Dashboard Studio.
* Do not modify this value.
* Default: true

activate_link_to_search = <boolean>
* Allows the Link to Search Interaction in Dashboard Studio.
* A value of "true" means the Link to Search Interaction is available in Dashboard Studio.
* Do not modify this value.
* Default: true

activate_trellis_for_visualizations = <boolean>
* Allows trellis layout for supported visualizations in Dashboard Studio.
* A value of "true" means trellis layout is available for supported visualizations in Dashboard Studio.
* Do not modify this value.
* Default: true

activate_expanded_source_editor = <boolean>
* Uses a larger inline source editor for Dashboard Studio.
* A value of "true" means the expanded source editor is available in Dashboard Studio.
* Do not modify this value.
* Default: true

activate_dsl_webworkers_for_visualizations = <boolean>
* Uses WebWorkers for Dynamic Options Syntax execution to isolate from overall dashboard loading and performance.
* A value of "true" means the WebWorkers are being used in Dashboard Studio.
* Do not modify this value.
* Default: false

activate_save_report_to_dashboard_studio = <boolean>
* Determines if users see an Add to Dashboard dropdown list in the Splunk Web Reports page and Save Search to Report dialogs.
  The dropdown menu allows adding a report to a new or existing Dashboard Studio dashboard.
* A value of "false" means Splunk Web does not display the dropdown menu, and users can only add reports to Classic Simple XML dashboards.
* Do not modify this value.
* Default: true

activate_source_mode_validation = <boolean>
# Determines whether the source mode validation in Dashboard Studio is activated.
# A value of "true" means that source mode is validated in Dashboard Studio.
# Do not modify this value.
* Default: true




[feature::windows_rce]

enable_acuif_pages = <boolean>
* Determines whether to display the new Admin Config UI Framework
  version of the following Windows input pages: admin_win-event-log-collections,
  admin_win-perfmon, admin_win-wmi-collections, fwd_admin_win-perfmon.
* A value of "true" means that Splunk Cloud Platform will display the
  Admin Config UI Framework version of the page.
* Default: false

[feature:page_migration]

enable_triggered_alerts_vnext = <boolean>
* Determines whether or not Splunk Web loads the new triggered alerts page.
* DEPRECATED.
* A value of "true" means that Splunk Web does load the new triggered alerts page.
* CAUTION: Do not change this setting.
* Default: true

enable_home_vnext = <boolean>
* Determines whether or not Splunk Web loads the new home page.
* DEPRECATED.
* A value of "true" means that Splunk Web does load the new home page.
* CAUTION: Do not change this setting.
* Default: true

enable_datasets_vnext = <boolean>
* Determines whether or not Splunk Web loads the new datasets page.
* DEPRECATED.
* A value of "true" means that Splunk Web does load the new datasets page.
* CAUTION: Do not change this setting.
* Default: true

[feature:dashboard_inputs_localization]

enable_dashboard_inputs_localization = <boolean>
* Determines whether or not Splunk Web will attempt to localize input choices in
  Classic dashboards.
* A value of "true" means that localization for input choices will be enabled in
  Classic Dashboards.
* A value of "false" means that localization for input choices will be disabled in
  Classic Dashboards.
* Default: false

[feature:share_job]

enable_share_job_control = <boolean>
* Determines whether or not users can share jobs using the "Share Job" button in
  the Search app in Splunk Web.
* A value of "true" means that users can use the "Share Job" button in the
  Search app to share search jobs.
* A value of "false" means that users cannot use the "Share Job" button to
  share search jobs. Instead, they receive a notice that job sharing has
  been disabled and they can instead share a search query.
* Default: true

[feature:search_auto_format]

enable_autoformatted_comments = <boolean>
* Determines whether or not comments are auto-formatted by the search editor's auto-formatter.
* DEPRECATED.
* CAUTION: Do not change this setting.
* A value of "false" means that comments are not auto-formatted. Comment auto-formatting may
* result in undesirable output.
* Default: false

[feature:ui_prefs_optimizations]

optimize_ui_prefs_performance = <boolean>
* Determines whether or not Splunk Web will optimize performance of the API related to ui-prefs.conf.
* DEPRECATED.
* CAUTION: Do not change this setting.
* A value of "false" means that Splunk Web will not optimize performance of the API related to ui-prefs.
* Default: true

[feature:splunk_web_optimizations]

enable_app_bar_performance_optimizations = <boolean>
* Determines whether or not Splunk Web will optimize performance when generating the app bar.
* DEPRECATED.
* CAUTION: Do not change this setting.
* A value of "false" means that Splunk Web will not optimize performance when generating the app bar.
* Default: true

bypass_app_bar_performance_optimizations_apps = <comma separated list>
* Splunk Web will not optimize performance when generating the app bar for this comma separated list of apps.
* CAUTION: Do not change this setting.
* A value of "splunk_monitoring_console,search" means that Splunk Web will not optimize performance when generating the app bar for the splunk_monitoring_console and search apps.
* Default: ""

[feature:spotlight_search]

enable_spotlight_search = <boolean>
* Determines whether Splunk Web displays the Spotlight Search bar in the
  Settings menu.
* A value of "true" means that Splunk Web will display the Spotlight Search
  bar in the Settings menu.
* Default: false

[feature:o11y_preview]

enable_o11y_preview = <boolean>
* Determines whether Splunk Web displays the preview links and
  Splunk Observability preview sidebar in Search & Reporting.
* A value of "true" means that Splunk Web will show preview links and
  Splunk Observability preview sidebar in Search & Reporting.
* Default: true
