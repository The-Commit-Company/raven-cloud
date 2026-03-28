app_name = "raven_cloud"
app_title = "Raven Cloud"
app_publisher = "The Commit Company (Algocode Technologies Private Limited)"
app_description = "Cloud platform for Raven for notifications and marketplace"
app_email = "support@thecommit.company"
app_license = "agpl-3.0"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "raven_cloud",
		"logo": "/assets/raven_cloud/logo.png",
		"title": "Raven Cloud",
		"route": "/dashboard",
		# "has_permission": "raven_cloud.api.permission.has_app_permission"
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/raven_cloud/css/raven_cloud.css"
# app_include_js = "/assets/raven_cloud/js/raven_cloud.js"

# include js, css files in header of web template
# web_include_css = "/assets/raven_cloud/css/raven_cloud.css"
# web_include_js = "/assets/raven_cloud/js/raven_cloud.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "raven_cloud/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "raven_cloud/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "raven_cloud.utils.jinja_methods",
# 	"filters": "raven_cloud.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "raven_cloud.install.before_install"
# after_install = "raven_cloud.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "raven_cloud.uninstall.before_uninstall"
# after_uninstall = "raven_cloud.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "raven_cloud.utils.before_app_install"
# after_app_install = "raven_cloud.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "raven_cloud.utils.before_app_uninstall"
# after_app_uninstall = "raven_cloud.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "raven_cloud.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
    # "all": ["raven_cloud.tasks.all"],
    "daily": [
        "raven_cloud.doctype.rc_push_notification_log.rc_push_notification_log.cleanup_old_logs"
    ],
    # "hourly": ["raven_cloud.tasks.hourly"],
    "weekly": [
        "raven_cloud.doctype.rc_push_notification_weekly_summary.rc_push_notification_weekly_summary.aggregate_weekly_logs"
    ],
    # "monthly": ["raven_cloud.tasks.monthly"],
    # "cron": {
    #     # custom cron to run every sunday at 12:00 AM
    #     "0 0 * * 0": [
    #         "raven_cloud.doctype.rc_push_notification_weekly_summary.rc_push_notification_weekly_summary.aggregate_weekly_logs"
    #     ],
    # },
}

# Testing
# -------

# before_tests = "raven_cloud.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "raven_cloud.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "raven_cloud.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["raven_cloud.utils.before_request"]
# after_request = ["raven_cloud.utils.after_request"]

# Job Events
# ----------
# before_job = ["raven_cloud.utils.before_job"]
# after_job = ["raven_cloud.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"raven_cloud.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


fixtures = [
    {
        "doctype": "Role",
        "filters": {
            "name": "Raven Cloud User"
        },
    }
]

website_route_rules = [{'from_route': '/dashboard/<path:app_path>', 'to_route': 'dashboard'},]
