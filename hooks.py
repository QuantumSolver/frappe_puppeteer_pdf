from . import __version__ as app_version

app_name = "frappe_puppeteer_pdf"
app_title = "Puppeteer PDF Generator"
app_publisher = "Frappe Technologies Pvt Ltd."
app_description = "Frappe App to generate PDFs using Puppeteer/Chrome"
app_email = "hello@frappe.io"
app_license = "AGPLv3"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_js = ""

# include js, css files in header of web template
# web_include_css = "/assets/frappe_puppeteer_pdf/css/frappe_puppeteer_pdf.css"
# web_include_js = "/assets/frappe_puppeteer_pdf/js/frappe_puppeteer_pdf.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "frappe_puppeteer_pdf/public/scss/website"

# include js in page
# Keep minimal client scripts if needed for PDF
page_js = {
    "print": "frappe_puppeteer_pdf/client_scripts/print.js",
}

# include js in doctype views
doctype_js = {"Print Format": "frappe_puppeteer_pdf/client_scripts/print_format.js"}

# Jinja
# ----------

# Keep essential Jinja methods for PDF rendering
jinja = {
    "methods": [
        "frappe_puppeteer_pdf.pdf_utils.render_user_text",
        "frappe_puppeteer_pdf.pdf_utils.convert_css",
        "frappe_puppeteer_pdf.pdf_utils.convert_uom",
        "frappe_puppeteer_pdf.pdf_utils.get_barcode",
    ]
}

# Installation
# ------------

before_install = "frappe_puppeteer_pdf.install.before_install"
after_install = "frappe_puppeteer_pdf.install.after_install"

# Uninstallation
# ------------

before_uninstall = "frappe_puppeteer_pdf.uninstall.before_uninstall"

# PDF Generation Hooks
# ------------

pdf_header_html = "frappe_puppeteer_pdf.pdf_utils.pdf_header_footer_html"
pdf_body_html = "frappe_puppeteer_pdf.pdf_utils.pdf_body_html"
pdf_footer_html = "frappe_puppeteer_pdf.pdf_utils.pdf_header_footer_html"

get_print_format_template = "frappe_puppeteer_pdf.pdf_utils.get_print_format_template"

# Request Hooks
before_request = ["frappe_puppeteer_pdf.pdf_generator.before_request"]
after_request = ["frappe_puppeteer_pdf.pdf_generator.after_request"]

# Main PDF Generator Hook
pdf_generator = "frappe_puppeteer_pdf.pdf_generator.get_pdf"

# Desk Notifications
# ------------------

# DocType Class Override
# ---------------

override_doctype_class = {
    "Print Format": "frappe_puppeteer_pdf.overrides.PuppeteerPrintFormat",
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "all": [
        "frappe_puppeteer_pdf.install.setup_chromium",
    ],
}

# Document Events
# ---------------

# Testing
# -------

# before_tests = "frappe_puppeteer_pdf.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#     "frappe.desk.doctype.event.event.get_events": "frappe_puppeteer_pdf.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#     "Task": "frappe_puppeteer_pdf.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["frappe_puppeteer_pdf.utils.before_request"]
# after_request = ["frappe_puppeteer_pdf.utils.after_request"]

# Job Events
# ----------
# before_job = ["frappe_puppeteer_pdf.utils.before_job"]
# after_job = ["frappe_puppeteer_pdf.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#     {
#         "doctype": "{doctype_1}",
#         "filter_by": "{filter_by}",
#         "redact_fields": ["{field_1}", "{field_2}"],
#         "partial": 1,
#     },
#     {
#         "doctype": "{doctype_2}",
#         "filter_by": "{filter_by}",
#         "partial": 1,
#     },
#     {
#         "doctype": "{doctype_3}",
#         "strict": False,
#     },
#     {
#         "doctype": "{doctype_4}"
#     }
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#     "frappe_puppeteer_pdf.auth.validate"
# ]
