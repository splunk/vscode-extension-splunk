#   Version 9.4.3
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
# Make any changes to system defaults by overriding them in
# $SPLUNK_HOME/etc/system/local
# For more details about configuration precedence, see "Configuration file precedence" in the Admin Manual in the Splunk Docs.
#
# For more information on configuration files, search for
# "Use Splunk Web to manage configuration files" in the Admin Manual in the Splunk Docs.

[feature:search_v2_endpoint]

enable_search_v2_endpoint = <boolean>
* REMOVED. This setting no longer has any effect.
* Determines whether Splunk Web uses the v2 search endpoint.
* A value of "true" means Splunk Web uses the v2 search endpoint.
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

activate_downsampling = <boolean>
* This setting turns on or off the downsampling feature in Dashboard Studio.
* A value of "true" activates the downsampling of data in time series charts and charts with a strictly increasing numeric x-axis in Dashboard Studio.
* Default: true

enable_show_hide = <boolean>
* Allows absolute "Show/Hide" panels in Dashboard Studio.
* A value of "true" will allow "Show/Hide" panels in the editor of Dashboard Studio.
* Do not modify this value.
* Default: true

activate_dsl_webworkers_for_visualizations = <boolean>
* Uses WebWorkers for Dynamic Options Syntax execution to isolate from overall dashboard loading and performance.
* A value of "true" means the WebWorkers are being used in Dashboard Studio.
* Do not modify this value.
* Default: false

lazy_load_data_frames_for_visualizations = <boolean>
* This setting turns on or off the feature that delays rendering data frames in visualizations within Dashboard Studio until the content is required.
* A value of "true" means data frames will be lazy loaded during the execution of Dynamic Options Syntax, which styles visualizations based on connected data.
* The setting will be removed without notice in a future release.
* Do not modify this value.
* Default: true

bypass_clonedeep_options_scope_for_visualizations = <boolean>
* This setting turns on or off the cloning of the original data source during Dynamic Options Syntax execution for visualizations in Dashboard Studio.
* A value of "true" means the original data source will not be cloned during the execution of Dynamic Options Syntax, which styles visualizations based on connected data.
* The setting will be removed without notice in a future release.
* Do not modify this value.
* Default: true

execute_chain_searches_with_tokens_in_search_process = <boolean>
* This setting determines whether Dashboard Studio runs chain searches that use tokens ahead of time in the search process instead of the main splunkd process. If the base search is a scheduled save search, the search runs in the main splunkd process.
* A value of "true" means that Dashboard Studio runs chain searches that use tokens ahead of time in the search process.
* A value of "false" means that Dashboard Studio runs chain searches that use tokens in the main splunkd process rather than ahead of time in the search process.
* Default: false

activate_dashboard_versioning = <boolean>
* This setting turns on or off UI to save, view, and restore Dashboard Studio versions.
* A value of "true" means that Dashboard Studio dashboards can be saved with a commit message, and previous versions can be viewed and restored from the UI.
* The setting will be removed without notice in a future release.
* Default: true

activate_add_saved_searches_from_studio = <boolean>
* This setting activates the UI that adds a new Saved Search datasource directly from Dashboard Studio.
* A value of "true" means that the option to add a new Saved Search appears in the Dashboard Studio UI.
* The setting will be removed without notice in a future release.
* Default: true

activate_o11y_dashboards = <boolean>
* This setting turns on or off all observability functionality within Dashboard Studio.
* A value of "true" activates observability functionality. The activation of future observability features might be controlled separately.
* A setup to connect with an instance of observability will still be required.
* A value of "false" deactivates all observability functionality.
* The setting will be removed without notice in a future release.
* Do not modify this value.
* Default: true

[feature:pdfgen]
activate_chromium_legacy_export = <boolean>
* Whether or not the Chromium web engine generates PDF exports for Simple XML dashboards, reports, and alerts.
* A value of "true" means that Chromium generates PDF exports for these dashboards, reports, and alerts.
* A value of "false" means that the Node.js runtime generates the PDF exports.
* The value for this setting does not affect exports from Dashboard Studio.
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

enable_authoverview_vnext = <boolean>
* Whether or not Splunk Web loads the updated authentication methods page that
  uses the React JavaScript library.
* A value of "true" means that Splunk Web loads the updated authentication methods 
  page that uses the React JavaScript library.
* A value of "false" means that Splunk Web loads the existing authentication methods
  page.
* Default: true

enable_react_users_page = <boolean>
* Whether or not Splunk Web loads the "Users" page that uses the React JavaScript library.
* A value of "true" means that Splunk Web loads the "Users" page
  implemented with the React library instead of the Backbone library.
* A value of "false" means that Splunk Web loads the page that uses the existing Backbone
  library.
* Default: true

enable_password_management_page_vnext = <boolean>
* Determines whether or not Splunk Web loads the "Password Management" page that uses
  the React JavaScript library.
* A value of "true" means that Splunk Web loads the new "Password Management" page
  implemented with the React library instead of the Backbone library.
* A value of "false" means that Splunk Web loads the page that uses the existing
  Backbone library.

enable_authentication_providers_LDAP_vnext = <boolean>
* Whether or not Splunk Web loads the updated "LDAP" configuration page
  that uses the React JavaScript library.
* A value of "true" means that Splunk Web loads the updated "LDAP" page
  implemented with the React library instead of the XML implementation.
* A value of "false" means that Splunk Web loads the page that uses the existing XML
  implementation.
* Default: true

enable_admin_LDAP-groups_vnext = <boolean>
* Whether or not Splunk Web loads the updated "LDAP-groups" page that uses the
  React JavaScript library.
* A value of "true" means that Splunk Web loads the "LDAP-groups" page
  implemented with the React library instead of the XML implementation.
* A value of "false" means that Splunk Web loads the page that uses the existing XML
  implementation.
* Default: true

enable_authorization_tokens_vnext = <boolean>
* Whether or not Splunk Web loads the updated "Tokens" page that uses the
  React JavaScript library.
* A value of "true" means that Splunk Web loads the "Tokens" page
  implemented with the React library instead of the Backbone library.
* A value of "false" means that Splunk Web loads the page that uses the existing
  Backbone library.

enable_duo_mfa_vnext = <boolean>
* Determines whether Splunk Web loads the updated "Duo-MFA" configuration 
  page that uses the React JavaScript library.
* A value of "true" means that Splunk Web loads the "Duo-MFA" page
  implemented with the React library instead of the XML implementation.
* A value of "false" means that Splunk Web loads the page that uses the 
  existing XML implementation.
* Default: true

enable_authorization_roles_vnext = <boolean>
* Whether or not Splunk Web loads the updated "Authorization
  roles" page.
* A value of "true" means that Splunk Web loads the "Authorization roles"
  page using separate pages for edits.
* A value of "false" means that Splunk Web loads the existing "Roles" page
  using modals for edits.
* Default: true

enable_authentication_users_vnext = <boolean>
* Whether or not Splunk Web loads the updated "Users" page,
  which uses separate pages for edits.
* A value of "true" means that Splunk Web loads the updated "Users" page,
  which uses separate pages for edits.
* A value of "false" means that Splunk Web loads the previous "Users" page,
  which uses modals for edits.
* Default: true

enable_reports_vnext = <boolean>
* Determines whether or not Splunk Web loads the new reports page.
* A value of "true" means that Splunk Web does load the new reports page.
* Do not modify this value.
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

enable_app_bar_caching = <boolean>
# Splunk Web will cache the app bar to optimize performance when generating the app bar.
# CAUTION: Do not change this setting.
* A value of "false" means that Splunk Web will not cache the app bar and not optimize performance when generating the app bar.
* Default: true

[feature:spotlight_search]

enable_spotlight_search = <boolean>
* Determines whether Splunk Web displays the Spotlight Search bar in the
  Settings menu.
* A value of "true" means that Splunk Web will display the Spotlight Search
  bar in the Settings menu.
* Default: true

[feature:search_sidebar]

enable_sidebar_preview = <boolean>
* Determines whether the Search & Reporting app displays a "preview"
  column for events, and allows the preview sidebar in the Events view.
* A value of "true" means that Splunk Web will show preview links and
  the preview sidebar will render.

[feature:field_filters]

enable_field_filters_ui = <boolean>
* Determines whether Splunk Web displays field filters.
* A value of "false" means that field filters are not visible in Splunk Web.
* Default: true

[feature:identity_sidecar_scim]

enabled = <boolean>
* Whether or not Splunk Web displays Automated User Management (AUM) controls for System
  for Cross-Domain Identity Management (SCIM) in the SAML configuration dialog page.
* A value of "true" means that Splunk Web shows AUM controls in the SAML
  configuration dialog.
* A value of "false" means that Splunk Web does not show AUM controls in
  the SAML configuration dialog.
* Default: true

[feature:system_namespace_redirection]

enable_system_namespace_redirection = <boolean>
* Determines whether or not Splunk Web redirects pages with the system app namespace.
* A value of "true" means that Splunk Web redirects pages with the system app 
  namespace.
* A value of "false" means that Splunk Web does not redirect pages with the 
  system app namespace.
* CAUTION: Do not change this setting.
* Default: true



[feature:appserver]

python.version = <string>
* Determines whether the appserver uses Python 3.9 or Python 3.7.
* A value of "python3.9" means that the appserver uses Python 3.9.
* A value of "python3.7" means that the appserver uses Python 3.7.
* A value of "latest" means that the appserver uses latest version of Python available in the release.
* Default: latest

[feature:federated_search]
enable_ipv6_validations = <boolean>
* Whether or not Splunk Web lets users enter IPv6 addresses and Classless
  Inter-Domain Routing (CIDR) ranges into address input forms.
* A value of "true" means that Splunk Web accepts IPv6 addresses and
  CIDR ranges in address input forms.
* A value of "false" means that Splunk Web accepts only IPv4 addresses
  and CIDR ranges in address input forms, and rejects IPv6 addresses
  and CIDR ranges.
* Default: true

