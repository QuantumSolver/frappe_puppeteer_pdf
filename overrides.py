import frappe
from frappe.printing.doctype.print_format.print_format import PrintFormat


class PuppeteerPrintFormat(PrintFormat):
    """Override PrintFormat to handle puppeteer-specific logic"""

    def get_html(self, doc=None, print_settings=None):
        """Get HTML for the document, ensuring puppeteer compatibility"""
        html = super().get_html(doc, print_settings)

        # If this is a print designer format using puppeteer, ensure proper HTML structure
        if self.print_designer:
            # Add puppeteer marker for identification
            if '<div id="__print_designer"' not in html:
                # Insert marker at the beginning of body
                html = html.replace("<body", '<body data-puppeteer-pdf="true"')

        return html

    def get_print_settings(self, print_settings=None):
        """Override print settings to ensure puppeteer is used for print designer formats"""
        settings = super().get_print_settings(print_settings)

        # Force puppeteer for print designer formats if not specified
        if self.print_designer and not settings.get("pdf_generator"):
            settings["pdf_generator"] = "puppeteer"

        return settings

    def before_print(self, settings, print_format):
        """Hook called before printing"""
        # Ensure puppeteer is set for print designer formats
        if self.print_designer:
            settings["pdf_generator"] = "puppeteer"

        return settings
