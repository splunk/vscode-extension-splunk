#   Version 10.4.2
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
* DEPRECATED: This setting has no effect. It will be removed without notice in a future release.

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

activate_o11y_dashboards = <boolean>
* This setting turns on or off all observability functionality within Dashboard Studio.
* A value of "true" activates observability functionality. The activation of future observability features might be controlled separately.
* A setup to connect with an instance of observability will still be required.
* A value of "false" deactivates all observability functionality.
* The setting will be removed without notice in a future release.
* Do not modify this value.
* Default: true

activate_o11y_service_graph = <boolean>
* This setting turns on or off observability service graph visualization and data source functionality within Dashboard Studio.
* A value of "true" means that Dashboard Studio can use service graph visualization and data source functionality.
* A setup to connect with an instance of observability will still be required.
* A value of "false" disables service graph visualization and data source functionality.
* The setting will be removed without notice in a future release.
* Do not modify this value.
* Default: true

activate_dashboard_publishing_and_view_without_login = <boolean>
* REMOVED. This setting has been removed and has no effect.

activate_custom_visualizations = <boolean>
* REMOVED. This setting has been removed and has no effect.

activate_studio_extension_framework = <boolean>
* Determines whether Dashboard Studio uses custom visualizations built
  with the Studio Extension Framework.
* A value of "true" means that Dashboard Studio displays custom
  visualizations built with the Studio Extension Framework.
* A value of "false" means that the Splunk platform supports only legacy
  custom visualizations.
* Do not modify this setting.
* Default: true

activate_conditional_visibility = <boolean>
* REMOVED. This setting has been removed and has no effect.

activate_spl2_datasources = <boolean>
* This setting determines whether users can access SPL2 data sources in
* Dashboard Studio.
* A value of "true" means users can access SPL2 data sources.
* A value of "false" means users cannot access SPL2 data sources.
* The setting will be removed without notice in a future release.
* Do not modify this value.
* Default: true

[feature:pdfgen]

activate_chromium_legacy_export = <boolean>
* REMOVED. This setting has been removed and has no effect.

activate_scheduled_export_upscaling = <boolean>
* Determines whether Dashboard Studio upscales scheduled exports, which
  improves image quality for large dashboards.
* A value of "true" activates automatic upscaling.
* A value of "false" deactivates upscaling. Instead, Dashboard Studio uses a
  1x scale factor, which might result in blurry visualizations and images for
  large dashboards.
* Default: true


[feature:new_data_management_experience]


enable_new_data_management_home = <boolean>
* Whether or not the Data Management link navigates to the Data Management
  app home page on the Splunk platform deployment.
* A value of "true" means the link navigates to the Data Management app home
  page on the Splunk platform deployment.
* A value of "false" means that the link does not work for Splunk Enterprise,
  and navigates to the landing page on the Splunk Cloud Services (SCS) tenant
  for Splunk Cloud Platform.
* Default: true


[feature::windows_rce]

enable_acuif_pages = <boolean>
* Determines whether to display the new Admin Config UI Framework
  version of the following Windows input pages: admin_win-event-log-collections,
  admin_win-perfmon, admin_win-wmi-collections, fwd_admin_win-perfmon.
* A value of "true" means that Splunk Cloud Platform will display the
  Admin Config UI Framework version of the page.
* Default: false

[feature:modern-nav]

enable_nav_vnext = <boolean>
* Determines whether or not Splunk Web loads the new Layout API.
* A value of "true" means Splunk Web loads the latest Layout API.
* A value of "false" means Splunk Web loads the legacy Layout API.
* Do not modify this value.
* Default: false

[feature:page_migration]
enable_data_ui_workflow-actions_vnext = <boolean>
* Controls whether Splunk Web loads the updated "Workflow actions" page in the 
  Data user interface (UI).
* A value of "true" means that Splunk Web loads the updated page implemented 
  with the React JavaScript library.
* A value of "false" means that Splunk Web loads the existing page.
* Default: true

enable_data_props_sourcetype-rename_vnext = <boolean>
* Controls whether Splunk Web loads the updated "Sourcetype renaming" page.
* A value of "true" means that Splunk Web loads the updated page implemented 
  with the React JavaScript library.
* A value of "false" means that Splunk Web loads the existing page.
* Default: true

enable_data_transforms_extractions_vnext = <boolean>
* Controls whether Splunk Web loads the updated "Extractions" management page.
* A value of "true" means that the Splunk Web component loads the updated
  page implemented with the React JavaScript library.
* A value of "false" means that Splunk Web loads the existing page.
* Default: true

enable_data_props_fieldaliases_vnext = <boolean>
* Controls whether Splunk Web loads the updated "Field aliases" page.
* A value of "true" means that Splunk Web loads the updated page implemented 
  with the React JavaScript library.
* A value of "false" means that Splunk Web loads the existing page.
* Default: true

enable_data_props_extractions_vnext = <boolean>
* Controls whether Splunk Web loads the updated "Field extractions" page.
* A value of "true" means that Splunk Web loads the updated page implemented 
  with the React JavaScript library.
* A value of "false" means that Splunk Web loads the existing page.
* Default: true

enable_data_props_calcfields_vnext = <boolean>
* Controls whether Splunk Web loads the updated "Calculated fields" page.
* A value of "true" means that Splunk Web loads the updated page implemented 
  with the React JavaScript library.
* A value of "false" means that Splunk Web loads the existing page.
* Default: true

enable_triggered_alerts_vnext = <boolean>
* Determines whether or not Splunk Web loads the new triggered alerts page.
* REMOVED. This setting has been removed and has no effect.

enable_home_vnext = <boolean>
* REMOVED. This setting has been removed and has no effect.

enable_datasets_vnext = <boolean>
* REMOVED. This setting has been removed and has no effect.

enable_job_manager_vnext = <boolean>
* Determines whether or not Splunk Web loads the new job manager page.
* DEPRECATED.
* A value of "true" means that Splunk Web does load the new job manager page.
* Do not modify this value.
* Default: true

enable_authoverview_vnext = <boolean>
* Whether or not Splunk Web loads the updated authentication methods page that
  uses the React JavaScript library.
* A value of "true" means that Splunk Web loads the updated authentication methods
  page that uses the React JavaScript library.
* A value of "false" means that Splunk Web loads the existing authentication methods
  page.
* Default: true

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
* REMOVED. Splunk removed an outdated version of the "Authorization roles" page.
  Configuring this setting no longer has any effect.
* Whether or not Splunk Web loads the updated "Authorization
  roles" page.
* Default: true

enable_authentication_users_vnext = <boolean>
* REMOVED. Splunk removed an outdated version of the "Users" page.
  Configuring this setting no longer has any effect.
* Whether or not Splunk Web loads the updated "Users" page,
  which uses separate pages for edits.
* Default: true

enable_data_indexes_cloud_vnext = <boolean>
* Whether or not Splunk Web loads the updated "Indexes" Cloud page.
* A value of "true" means that Splunk Web loads the updated "Indexes" Cloud
  page.
* A value of "false" means that Splunk Web loads the classic "Indexes" Cloud
  page.
* Default: true

enable_data_indexes_vnext = <boolean>
* Whether or not Splunk Web loads the updated "Indexes" page.
* A value of "true" means that Splunk Web loads the updated "Indexes" page.
* A value of "false" means that Splunk Web loads the classic "Indexes" page.
* Default: true

enable_reports_vnext = <boolean>
* Determines whether or not Splunk Web loads the new reports page.
* DEPRECATED.
* A value of "true" means that Splunk Web does load the new reports page.
* Do not modify this value.
* Default: true

enable_alerts_vnext = <boolean>
* DEPRECATED. This setting has been deprecated and has no effect.

enable_dashboards_vnext = <boolean>
* Determines whether or not Splunk Web loads the new dashboards listing page.
* A value of "true" means that Splunk Web loads the new dashboards listing page.
* A value of "false" means that Splunk Web loads the classic dashboards listing page.
* Default: true

enable_admin_alert_actions_vnext = <boolean>
* Determines whether or not Splunk Web loads the "Email Settings" page that uses
  the React JavaScript library.
* A value of "true" means that Splunk Web loads the modernized "Email Settings" page
  implemented with the React library instead of with Python and XML.
* A value of "false" means that Splunk Web loads the page that uses the existing
  Python and XML solution.

enable_saml_vnext = <boolean>
* Whether or not Splunk Web loads the updated "SAML" page that uses the
  React JavaScript library.
* A value of "true" means that Splunk Web loads the "SAML" page
  implemented with the React library instead of the Backbone library.
* A value of "false" means that Splunk Web loads the page that uses the existing
  Backbone library.
* Default: true

enable_admin_directory_vnext = <boolean>
* Determines whether or not Splunk Web loads the "All configurations" page that
  uses the React JavaScript library.
* A value of "true" means that Splunk Web loads the modernized "All configurations"
  page implemented with the React library instead of with Python and XML.
* A value of "false" means that Splunk Web loads the page that uses the existing
  Python and XML solution.
* Default: true

enable_federation_page_vnext = <boolean>
* Whether or not Splunk Web displays the modernized Federation Page.
* A value of "false" means Splunk Web displays the old federated_search page.
* A value of "true" means Splunk Web displays the modernized Federation Page.
* Default: false

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

enable_search_bar_performance_optimizations = <boolean>
* DEPRECATED.
* Determines whether Splunk Web optimizes search bar load time when it loads
  the search page.
* A value of "false" means that Splunk Web does not optimize search bar load
  time when it loads the search page.
* CAUTION: Do not change this setting.
* Default: true

enable_saved_search_pageload_optimization = <boolean>
* DEPRECATED.
* Determines whether or not Splunk Web optimizes the fetching of details
  for saved searches.
* A value of "true" means that Splunk Web optimizes the fetching of
  details for saved searches.
* A value of "false" means that Splunk Web does not optimize the
  fetching of details for saved searches.
* CAUTION: Do not change this setting.
* Default: true

enable_messages_list_performance_optimizations = <boolean>
* DEPRECATED.
* Determines whether Splunk Web optimizes rendering the messages list when it
  loads some Splunk Web pages.
* A value of "true" means that Splunk Web optimizes rendering the messages
  list when it loads some Splunk Web pages.
* A value of "false" means that Splunk Web does not optimize rendering the
  messages list when it loads some Splunk Web pages.
* Do not change this setting.
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

[feature:authentication_oauth]

enable_authentication_oauth_ui = <boolean>
* Whether or not Splunk Web displays the Open Authorization
  (OAuth) configuration page as part of the Authentication
  Methods configuration workflow.
* A value of "true" means that Splunk Web displays the OAuth page.
* A value of "false" means that Splunk Web does not display the
  OAuth page.
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

python.version = latest|python3.9
* DEPRECATED.
* A value of "latest" means that the app server uses the latest
  version of Python that is available in the release.
* CAUTION: Do not change this setting.
* Default: latest

python.required = <comma-separated list>
* The list of Python versions that Splunk Web supports.
* This setting takes precedence over the 'python.version' setting if both
  settings have values.
* The following values are supported:
  * "3.9": Splunk Web uses Python version 3.9.
  * "3.13": Splunk Web uses Python version 3.13.
  * "latest": Splunk Web uses the latest Python interpreter available.
* CAUTION: Change this setting only when asked to do so by Splunk Support.
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



[feature:knowledge_object_favorites]
enable_dashboards_favorites = <boolean>
* Determines whether users can favorite dashboards.
* A value of "true" means users can favorite or unfavorite dashboards.
* A value of "false" means users cannot favorite or unfavorite dashboards.
* Default: true

enable_reports_favorites = <boolean>
* Determines whether users can favorite reports.
* A value of "true" means users can favorite or unfavorite reports.
* A value of "false" means users cannot favorite or unfavorite reports.
* Default: true


[feature:search_ai_assistant]
* Determines whether Splunk Web displays the Splunk AI Assistant for SPL
  in the Search app.
* A value of "true" means that users can see the Splunk AI Assistant for SPL
  in the Search app.
* A value of "false" means that users can't see the Splunk AI Assistant for SPL
  in the Search app.
enable_search_ai_assistant = true

[feature:splunk_ai_canvas]
check_ai_canvas_eligible = false
* Whether or not the Splunk platform displays AI Canvas.
* A value of "true" means that users can see AI Canvas.
* A value of "false" means that users cannot see AI Canvas.
* This setting applies only to the Splunk Cloud Platform.
* CAUTION: Do not change this setting.
* Default: false



[feature:spl2]
enable_spl2 = <boolean>
* Determines whether Splunk Web enables SPL2.
* A value of "true" means Splunk Web enables SPL2.
* A value of "false" means Splunk Web disables SPL2.
* Default: true

[feature:splunk_oauth_clients]
enable_splunk_oauth_clients_ui = <boolean>
* Whether or not Splunk Web displays pages related to Splunk Open
  Authorization clients.
* A value of "true" means that Splunk OAuth clients are visible in Splunk Web.
* A value of "false" means that Splunk OAuth clients are not visible in Splunk Web.
* Default: false

[feature:appserver_security]
deactivate_custom_mako_templates = <boolean>
* Whether or not Splunk Web blocks custom Mako templates shipped by apps.
* A value of "true" means Splunk Web blocks custom app Mako templates in the
  $SPLUNK_HOME/etc/apps/<app>/appserver/templates and $SPLUNK_HOME/etc/apps/
  <app>/appserver/modules directories.
* A value of "false" means Splunk Web allows custom app Mako templates in those
  directories.
* Regardless of this setting, Splunk Web always allows first-party templates in
  the $SPLUNK_HOME/share/splunk/search_mrsparkle directory.
* Default: false

deactivate_custom_cherrypy_controllers = <boolean>
* Whether or not Splunk Web blocks custom CherryPy controllers shipped by apps.
* A value of "true" means Splunk Web blocks custom app CherryPy controllers.
  Also, app controllers in the $SPLUNK_HOME/etc/apps/<app>/appserver/controllers
  directory are not registered, causing all /custom/<app>/* routes to return
  a 404 error.
* A value of "false" means Splunk Web allows custom app CherryPy controllers in
  those directories.
* This setting only affects the /custom/<app>/* directory. It does not affect
  REST endpoints, views, dashboards, and static assets.
* Default: false
