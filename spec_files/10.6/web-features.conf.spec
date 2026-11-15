#   Version 10.6.1.1
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

[feature:c3_base_urls]
waitlist_base_url = <string>
* The base URL for accessing the Cisco Cloud Control application programming
  interface (API) to provide the signup approval status of the current user.
* Possible values: staging.cloud.cisco.com | preview.cloud.cisco.com |
  cloud.cisco.com
* Do not modify this value.
* Default: preview.cloud.cisco.com

tenants_base_url = <string>
* The base URL for accessing the Cisco Cloud Control API to provide the current 
  Terms & Conditions agreement status for the tenant.
* Possible values: api.staging.cloud.cisco.com | api.preview.cloud.cisco.com |
  api.cloud.cisco.com
* Do not modify this value.
* Default: api.preview.cloud.cisco.com

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
* REMOVED. This setting has been removed and has no effect.

[feature:pdfgen]

activate_chromium_legacy_export = <boolean>
* REMOVED. This setting has been removed and has no effect.

activate_scheduled_export_upscaling = <boolean>
* REMOVED. This setting has been removed and has no effect.

[feature:new_search_experience]

enable_new_search_admin = <boolean>
* Allows admins to enable the new Search and Dashboard Experience preview for users on Splunk Cloud Platform.
* A value of "true" means that admins will see a new setting to enable the new Search and Dashboard Experience preview for all users.
* A value of "false" means that admins will not see a new setting to enable the new Search and Dashboard Experience preview for all users.
* Default: true

enable_new_search_user = <boolean>
* Determines whether or not users see the new Search and Dashboard Experience preview on Splunk Cloud Platform.
* A value of "true" means that users will see the new Search and Dashboard Experience preview.
* A value of "false" means that users will not see the new Search and Dashboard Experience preview.
* Default: false

[feature:new_data_management_experience]

enable_new_data_management_link = <boolean>
* Determines whether or not users see the link to the new Data Management Experience on Splunk Cloud Platform.
* A value of "true" means that users will see the link to the new Data Management Experience.
* A value of "false" means that users will not see the link to the new Data Management Experience.
* Default: true

enable_new_data_management_home = <boolean>
* Whether or not the Data Management link navigates to the Data Management
  app home page on the Splunk platform deployment.
* A value of "true" means the link navigates to the Data Management app home
  page on the Splunk platform deployment.
* A value of "false" means that the link does not work for Splunk Enterprise,
  and navigates to the landing page on the Splunk Cloud Services (SCS) tenant
  for Splunk Cloud Platform.
* Default: true

[feature:manager_xml_pages]

enable_element_overlay_usage = <boolean>
* Determines whether the 'element_overlay' query parameter in Splunk Web is
  enabled or disabled.
* A value of "false" means 'element_overlay' is disabled.
* CAUTION: Do not change this setting unless instructed to do so by Splunk
  Support.
* Default: false


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

[feature:c3]
* Settings for Cisco Cloud Control integration entry points in Splunk Web.
* Cisco Cloud Control integration entry points let users cross-launch from
  Splunk Web to Cisco Cloud Control when Cisco Unified Identity is active.

c3_integration_enabled = <boolean>
* Whether or not Splunk Web displays Cisco Cloud Control integration
  entry points, such as cross-launch links to Cisco Cloud Control.
* Splunkd updates this setting when a user with 'cisco_tenant_admin'
  uses the '/services/authentication/cisco_identity' opt-out API to turn
  Cisco Unified Identity circular authentication on or off.
* The configured Cisco Unified Identity value is the local administrator
  request stored in 'authentication.conf:[cui]/enable_circular_auth'.
* If 'authentication.conf:[cui]/enable_circular_auth' is absent or set to an
  empty or invalid Boolean value, Cisco Unified Identity circular
  authentication is not applicable on this stack and the
  '/services/authentication/cisco_identity' API reports 'enabled=null'.
* The effective Cisco Unified Identity state is the runtime result after
  the Splunk platform evaluates the configured value with the required SIS,
  hidden OpenID Connect, automatic registration, and external OAuth
  authorization-code flow prerequisites.
* Splunkd sets this value to match the effective Cisco Unified Identity
  state.
* Operators can set this value directly, but Splunkd can overwrite it after
  the next Cisco Unified Identity API update.
* A value of "true" means Splunk Web displays Cisco Cloud Control integration
  entry points.
* A value of "false" means Splunk Web does not display Cisco Cloud Control
  integration entry points.
* Default: false

[feature:page_migration]
enable_admin_alert_actions_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Email settings" page.
* A value of "true" means Splunk Web loads the updated "Email settings"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Email settings" page that uses
  the Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_admin_commandsconf_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Search commands" page.
* A value of "true" means Splunk Web loads the updated "Search commands"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Search commands" page that uses
  the Python and Extensible Markup Language (XML) implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_admin_directory_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "All configurations" page.
* A value of "true" means Splunk Web loads the updated "All configurations"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "All configurations" page that
  uses the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_admin_LDAP-groups_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "LDAP groups" page for
  Lightweight Directory Access Protocol (LDAP) group management.
* A value of "true" means Splunk Web loads the updated "LDAP groups"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "LDAP groups" page that uses the
  Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_advancedsearch_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Advanced search" page.
* A value of "true" means Splunk Web loads the updated "Advanced search"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Advanced search" page that uses
  the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_alerts_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Alerts" page.
* A value of "true" means Splunk Web loads the updated "Alerts"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Alerts" page that uses the
  Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_authentication_changepassword_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Change Password" page.
* A value of "true" means Splunk Web loads the updated "Change Password"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the existing Python and XML
  implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_authentication_providers_LDAP_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "LDAP" page.
* A value of "true" means Splunk Web loads the updated "LDAP"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "LDAP" page that uses the Python
  and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_authentication_users_vnext = <boolean>
* REMOVED. This setting has been removed and no longer has any effect.

enable_authorization_fieldfilters_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Field filters" page.
* A value of "true" means Splunk Web loads the updated "Field filters"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Field filters" page that uses
  the Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_authorization_roles_vnext = <boolean>
* REMOVED. This setting has been removed and no longer has any effect.

enable_authorization_tokens_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Tokens" page.
* A value of "true" means Splunk Web loads the updated "Tokens"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Tokens" page that uses the
  Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_authoverview_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Authentication methods" page.
* A value of "true" means Splunk Web loads the updated "Authentication methods"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Authentication methods" page
  that uses the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_bulkreassign_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Reassign knowledge objects"
  page.
* A value of "true" means Splunk Web loads the updated
  "Reassign knowledge objects" page implemented with the React JavaScript
  library.
* A value of "false" means Splunk Web loads the "Reassign knowledge objects"
  page that uses the Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_dashboards_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Dashboards" page.
* A value of "true" means Splunk Web loads the updated "Dashboards"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Dashboards" page that uses the
  Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_data_indexes_cloud_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Indexes cloud" page.
* A value of "true" means Splunk Web loads the updated "Indexes cloud"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Indexes cloud" page that uses
  the Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_data_indexes_vnext = <boolean>
* REMOVED. This setting has been removed and no longer has any effect.

enable_data_lookup-table-files_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Lookup table files" page.
* A value of "true" means Splunk Web loads the updated "Lookup table files"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Lookup table files" page that
  uses the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: false

enable_data_macros_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Search macros" page.
* A value of "true" means Splunk Web loads the updated "Search macros"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Search macros" page that uses
  the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_data_props_calcfields_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Calculated fields" page.
* A value of "true" means Splunk Web loads the updated "Calculated fields"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Calculated fields" page that
  uses the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_data_props_extractions_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Field extractions" page.
* A value of "true" means Splunk Web loads the updated "Field extractions"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Field extractions" page that
  uses the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_data_props_fieldaliases_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Field aliases" page.
* A value of "true" means Splunk Web loads the updated "Field aliases"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Field aliases" page that uses
  the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_data_props_lookups_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Automatic lookups" page.
* A value of "true" means Splunk Web loads the updated "Automatic lookups"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Automatic lookups" page that
  uses the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_data_props_sourcetype-rename_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Sourcetype renaming" page.
* A value of "true" means Splunk Web loads the updated "Sourcetype renaming"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Sourcetype renaming" page that
  uses the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_data_transforms_extractions_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Field transformations" page.
* A value of "true" means Splunk Web loads the updated "Field transformations"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Field transformations" page
  that uses the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_data_transforms_lookups_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Lookup definitions" page.
* A value of "true" means Splunk Web loads the updated "Lookup definitions"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Lookup definitions" page that
  uses the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_data_ui_views_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Views" page.
* A value of "true" means Splunk Web loads the updated "Views"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Views" page that uses the
  Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_data_ui_times_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Time ranges" page.
* A value of "true" means Splunk Web loads the updated "Time ranges"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Time ranges" page that uses the
  Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_data_ui_nav_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Navigation menus" page.
* A value of "true" means Splunk Web loads the updated "Navigation menus"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Navigation menus" page that
  uses the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_data_ui_workflow-actions_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Workflow actions" page.
* A value of "true" means Splunk Web loads the updated "Workflow actions"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Workflow actions" page that
  uses the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_datasets_vnext = <boolean>
* REMOVED. This setting has been removed and no longer has any effect.

enable_duo_mfa_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Duo-MFA" page for Duo
  multifactor authentication (MFA).
* A value of "true" means Splunk Web loads the updated "Duo-MFA"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Duo-MFA" page that uses the
  Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_federation_page_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Federation" page.
* A value of "true" means Splunk Web loads the updated "Federation"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Federation" page that uses the
  Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: false

enable_fields_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Fields" page.
* A value of "true" means Splunk Web loads the updated "Fields"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Fields" page that uses the
  Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_global_banner_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Global banner settings" page.
* A value of "true" means Splunk Web loads the updated "Global banner settings"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Global banner settings" page
  that uses the Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_home_vnext = <boolean>
* REMOVED. This setting has been removed and no longer has any effect.

enable_job_manager_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Job manager" page.
* A value of "true" means Splunk Web loads the updated "Job manager"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Job manager" page that uses the
  Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_login_page_settings_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Login page settings" page.
* A value of "true" means Splunk Web loads the updated "Login page settings"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Login page settings" page that
  uses the Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_lookup_geoip_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "GeoIP lookups file" page.
* A value of "true" means Splunk Web loads the updated "GeoIP lookups file"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "GeoIP lookups file" page that
  uses the Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_lookups_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Lookups" page.
* A value of "true" means Splunk Web loads the updated "Lookups"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Lookups" page that uses the
  Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_messages_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Bulletin messages" page.
* A value of "true" means Splunk Web loads the updated "Bulletin messages"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Bulletin messages" page that
  uses the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_permissions_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Permissions" page.
* A value of "true" means Splunk Web loads the updated "Permissions"
   page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Permissions" page that
  uses the Python implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_reports_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Reports" page.
* A value of "true" means Splunk Web loads the updated "Reports"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Reports" page that uses the
  Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_saml_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "SAML" page for Security
  Assertion Markup Language (SAML) configuration.
* A value of "true" means Splunk Web loads the updated "SAML"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "SAML" page that uses the
  Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_saved_eventtypes_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Event types" page.
* A value of "true" means Splunk Web loads the updated "Event types"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Event types" page that uses the
  Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_saved_searches_advancededit_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Saved search advanced edit"
  page.
* A value of "true" means Splunk Web loads the updated
  "Saved search advanced edit" page implemented with the React JavaScript
  library.
* A value of "false" means Splunk Web loads the "Saved search advanced edit"
  page that uses the Backbone implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_server_settings_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "General settings" page.
* A value of "true" means Splunk Web loads the updated "General settings"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "General settings" page that
  uses the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_tags_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "Tags" page.
* A value of "true" means Splunk Web loads the updated "Tags"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "Tags" page that uses the Python
  and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
* Default: true

enable_triggered_alerts_vnext = <boolean>
* REMOVED. This setting has been removed and no longer has any effect.

enable_ui_vnext = <boolean>
* Whether or not Splunk Web loads the React-based "User interface" page.
* A value of "true" means Splunk Web loads the updated "User interface"
  page implemented with the React JavaScript library.
* A value of "false" means Splunk Web loads the "User interface" page that uses
  the Python and XML implementation.
* You must restart the Splunk platform for changes to this setting to
  take effect.
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

[feature:web_access_policy]

enabled = <boolean>
* Whether or not Splunk Web applies the role- and path-based redirect rules
  configured in this stanza to authenticated user interface (UI) requests.
* A value of "true" means Splunk Web applies the policy according to
  'required_roles', 'bypass_roles', 'target_url', and 'denylist_url_patterns'.
* A value of "false" means Splunk Web does not apply the policy.
* If this setting is absent or the value is not a valid Boolean value, Splunk
  Web does not apply the policy.
* NOTE:Do not change this setting unless instructed to do so by Splunk Support.
* Default: false

required_roles = <semicolon-separated list>
* This setting lists role names that let users continue navigating the UI
  without redirection, except for paths that match
  'denylist_url_patterns'.
* A user's effective roles include roles that the user holds directly and
  roles that those roles import.
* If none of the user's effective roles matches a role in this list, Splunk
  Web redirects the user to 'target_url'.
* If this setting is empty, Splunk Web does not apply the policy.
* NOTE: Do not change this setting unless instructed to do so by Splunk Support.
* Default: Not set

bypass_roles = <semicolon-separated list>
* This setting lists role names that let a user bypass the web access policy.
* If a role that the user holds directly matches a role in this list, Splunk
  Web does not apply the policy to that user.
* Imported roles do not let the user bypass the policy.
* If the current user's direct roles intersect this list, Splunk Web skips the
  required_roles and denylist_url_patterns checks.
* NOTE: Do not change this setting unless instructed to do so by Splunk Support.
* Default: Not set

target_url = <string>
* This setting specifies the internal relative URL that Splunk Web uses as the
  redirect destination.
* The value must be a concrete internal relative URL, not a pattern.
* This setting is used for users without a required role and users with a
  required role who request a denylisted path.
* If this setting is empty or the value does not meet these requirements,
  Splunk Web does not apply the policy.
* NOTE: Do not change this setting unless instructed to do so by Splunk Support.
* Default: Not set

denylist_url_patterns = <semicolon-separated list>
* This setting lists internal relative path patterns that trigger redirection
  for users whose effective roles match a role in 'required_roles'.
* The "*" character matches zero or more path characters, including "/".
* NOTE: Do not change this setting unless instructed to do so by Splunk Support.
* Default: Not set

[feature:system_namespace_redirection]

enable_system_namespace_redirection = <boolean>
* Determines whether or not Splunk Web redirects pages with the system app namespace.
* A value of "true" means that Splunk Web redirects pages with the system app
  namespace.
* A value of "false" means that Splunk Web does not redirect pages with the
  system app namespace.
* CAUTION: Do not change this setting.
* Default: true

[feature:ip_allowlist]
enable_ipv6_validations = <boolean>
* Determines whether or not Splunk Web allows IPv6 addresses in address
  input forms for IP allow lists.
* A value of "true" means that Splunk Web allows IPv6 addresses in
  address input forms and both IPv4 and IPv6 addresses will pass frontend
  validation.
* A value of "false" means that Splunk Web allows only IPv4 addresses in
  address input forms and IPv6 addresses will fail frontend validation.
* Default: true

[feature:dynamic_feature_flagging]

enable_dynamic_ui_updates = <boolean>
* Determines whether or not a Splunk Cloud Platform deployment receives dynamic
  user interface updates.
* A value of "true" means the deployment receives the latest user interface
  updates.
* Splunk Cloud Platform deployments pull user interface updates from the
  content delivery network (CDN). Splunk Enterprise deployments pull user
  interface updates from the search head.
* A value of "false" means the deployment does not receive dynamic user
  interface updates.
* Default: true

feature_flag_service_url = <string>
* Specifies the URL from which newly released user interface updates are
  downloaded.
* CAUTION: Do not modify this value without guidance from Splunk personnel.
  Specifying an incorrect URL value can make content updates inaccessible to your
  deployment.
* Default: dff.splunk.com

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

enable_legacy_fss3_ui = <boolean>
* Whether or not Splunk Web keeps the legacy Federated Search for Amazon S3
  functionality available when
  'limits.conf:[federated_analytics]/enable_federated_analytics_service'
  has a value of "true".
* A value of "true" means that Splunk Web makes the legacy Federated Search
  for Amazon S3 workflow available regardless of the value of
  'limits.conf:[federated_analytics]/enable_federated_analytics_service'.
* A value of "false" means that Splunk Web makes the legacy Federated Search
  for Amazon S3 workflow available only when
  'limits.conf:[federated_analytics]/enable_federated_analytics_service'
  has a value of "false".
* This setting does not select the old or modernized Amazon S3 workflow. Use
  'enable_s3_modernization' to select the workflow.
* Default: false

enable_s3_modernization = <boolean>
* Whether or not Splunk Web displays the modernized Federated Search for Amazon
  S3 workflow.
* A value of "false" means Splunk Web displays the old workflow.
* A value of "true" means Splunk Web displays the modernized workflow.
* Default: true

[feature:federated_analytics]
enable_fa_asl = <boolean>
* Whether or not Splunk Web displays workflows associated with setting up
  Federated Analytics.
* A value of "false" means the workflows are not visible in Splunk Web and
  associated configurations, such as federated providers and federated indexes,
  can be viewed but not changed.
* A value of "true" means the workflows are visible in Splunk Web and
  configurations associated with Federated Analytics can be updated.
* Default: false

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
enable_search_ai_assistant = <boolean>
* Whether or not Splunk Web displays the Splunk AI Assistant in the Search app.
* A value of "true" means that:
  * Users can see the Splunk AI Assistant in the Search app.
  * The 'admin_search_ai_assistant_allowed' setting is available
    through Splunk Web Server Settings for admins to further restrict
    the Splunk AI Assistant.
* A value of "false" means that users can't see the Splunk AI Assistant
  in the Search app.

admin_search_ai_assistant_allowed = <boolean>
* Whether or not the Splunk AI Assistant in the Search app is available
  to users on this Splunk platform instance.
* A value of "true" means the Splunk AI Assistant in the Search app is
  available to users in Splunk Web.
* A value of "false" means the Splunk AI Assistant in the Search app is
  not available to any user in Splunk Web.
* Administrators can use this setting to independently control the availability
  of the Splunk AI Assistant using a toggle on their Splunk platform instance,
  which is displayed in Splunk Web on the Search preferences page, in Server 
  settings.
* Change the value of this setting using the toggle in Splunk Web in the Search
  preferences page instead of using this setting. If you change the value of
  'admin_search_ai_assistant_allowed', you must manually reload this file. 
* This setting only takes effect when 'enable_search_ai_assistant'
  has a value of "true". 
* If 'enable_search_ai_assistant' has a value of "false", this setting has no
  effect and the Splunk AI Assistant toggle is not displayed in the Search 
  preferences page in Splunk Web for this Splunk platform instance.
* Default: true

[feature:pendo]
enable_pendo = <boolean>
* This setting turns on or off Pendo telemetry integration in Splunk Web.
* A value of "true" means Pendo telemetry is on.
* A value of "false" means Pendo telemetry is off.
* Default: true

[feature:scoped_capabilities]
enable_scoped_capabilities_ui = <boolean>
* Determines whether Splunk Web displays UI related to scoped capabilities,
  which are authorization policies that add fine-grained scopes to capabilities
  and are necessary for implementing complex access policies.
* A value of "true" means that policies management pages accessed through
  Settings and on the roles page are visible in Splunk Web.
* A value of "false" means that policies management pages accessed through
  Settings and on the roles page are not visible in Splunk Web.
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
  directories, with a WARN message on each custom app Mako template load
  indicating that the template is deprecated and is scheduled for removal in an
  upcoming release.
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
  those directories, with a WARN message at controller registration and on each
  request indicating that the controller is deprecated and is scheduled for
  removal in an upcoming release.
* This setting only affects the /custom/<app>/* directory. It does not affect
  REST endpoints, views, dashboards, and static assets.
* Default: false

[feature:splunk_service_credentials]
enable_splunk_service_credentials_ui = <boolean>
* Whether or not Splunk Web displays pages related to service credentials.
* Apps and data inputs use service credentials to authenticate with external systems.
* A value of "true" means that service credentials pages are visible in Splunk Web.
* A value of "false" means that service credentials pages are not visible in Splunk Web.
* Default: true

[feature:cron_schedule_restrictions]
enable_cron_schedule_restrictions_ui = <boolean>
* Whether or not to turn on role-based cron schedule restrictions in Splunk Web,
  on the Resources tab of the "Roles" page. 
* When turned on, roles in Splunk Web can define minimum schedule intervals
  and restrict custom cron expressions. 
* A value of "true" means settings for cron schedule restrictions are visible
  in Splunk Web.
* A value of "false" means settings for cron schedule restrictions are not
  visible in Splunk Web.
* Default: false

[feature:hec_mdl_raw_datasets]
enable_hec_mdl_raw_datasets_ui = <boolean>
* Whether or not Splunk Web displays Machine Data Lake (MDL) raw
  datasets as available indexes when configuring data inputs
  for the HTTP Event Collector (HEC).
* A value of "true" means that MDL raw datasets display as available
  indexes when configuring a HEC token on the "Add Data" pages.
* A value of "false" means that MDL raw datasets are not visible as available
  indexes when configuring a HEC token on the "Add Data" pages.
* Default: true

[feature:guided_data_inputs]
gdi_web_service_home = <string>
* The home address of the Guided Data Inputs (GDI) web service.
* Default: https://guides.splunk.com/v1
