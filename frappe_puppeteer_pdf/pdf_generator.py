import os
import tempfile

import frappe
from frappe.utils.pdf import get_pdf as frappe_get_pdf
from playwright.sync_api import sync_playwright

from .chrome_manager import ensure_chrome_running, stop_chrome


def before_request():
    """Set pdf_generator to puppeteer for print designer formats"""
    if (
        frappe.request.path == "/api/method/frappe.utils.print_format.download_pdf"
        or frappe.request.path == "/printview"
    ):
        # Get the print format being requested
        print_format = frappe.request.args.get("format")
        if print_format:
            # Check if this is a print designer format
            is_print_designer = frappe.get_cached_value(
                "Print Format", print_format, "print_designer"
            )
            pdf_generator = frappe.get_cached_value(
                "Print Format", print_format, "pdf_generator"
            )

            # Set pdf_generator in form_dict
            if is_print_designer and pdf_generator == "puppeteer":
                frappe.local.form_dict.pdf_generator = "puppeteer"
            else:
                frappe.local.form_dict.pdf_generator = frappe.request.args.get(
                    "pdf_generator", pdf_generator or "wkhtmltopdf"
                )

        # Initialize Chrome if puppeteer is being used
        if frappe.local.form_dict.get("pdf_generator") == "puppeteer":
            try:
                ensure_chrome_running()
            except Exception as e:
                frappe.log_error(f"Failed to start Chrome for puppeteer: {e}")
                # Fallback to wkhtmltopdf
                frappe.local.form_dict.pdf_generator = "wkhtmltopdf"


def after_request():
    """Cleanup after request"""
    # We keep Chrome running for performance, but could stop it here
    # stop_chrome()  # Uncomment if you want to stop Chrome after each request


def get_pdf(print_format, html, options=None, output=None, pdf_generator=None):
    """Main PDF generation function called by Frappe"""
    if pdf_generator != "puppeteer":
        # Let Frappe use default PDF generator
        return None

    try:
        frappe.logger().info(
            f"Generating PDF with puppeteer for format: {print_format}"
        )

        # Ensure Chrome is running
        chrome_manager = ensure_chrome_running()

        # Generate PDF using Playwright
        pdf_data = generate_with_playwright(html, options, chrome_manager)

        if output:
            with open(output, "wb") as f:
                f.write(pdf_data)
            return output

        return pdf_data

    except Exception as e:
        frappe.log_error(f"Puppeteer PDF generation failed for {print_format}: {e}")
        frappe.logger().error(f"Falling back to wkhtmltopdf: {e}")

        # Fallback to Frappe's default PDF generator
        return fallback_to_wkhtmltopdf(html, options, output)


def generate_with_playwright(html, options, chrome_manager):
    """Generate PDF using Playwright connected to Chrome"""
    with sync_playwright() as p:
        try:
            # Connect to running Chrome instance
            browser = p.chromium.connect_over_cdp(chrome_manager.get_connection_url())

            # Create new page
            page = browser.new_page()

            # Set HTML content
            page.set_content(html, wait_until="networkidle")

            # Configure PDF options
            pdf_options = map_frappe_to_playwright(options)

            # Generate PDF
            pdf_data = page.pdf(**pdf_options)

            # Cleanup
            page.close()
            browser.close()

            return pdf_data

        except Exception as e:
            frappe.log_error(f"Playwright PDF generation error: {e}")
            raise


def map_frappe_to_playwright(options):
    """Map Frappe PDF options to Playwright PDF options"""
    if not options:
        options = {}

    playwright_options = {
        "format": options.get("page_size", "A4"),
        "print_background": True,
        "scale": 1,
        "display_header_footer": False,
        "header_template": "",
        "footer_template": "",
        "landscape": options.get("orientation", "Portrait") == "Landscape",
        "page_ranges": options.get("page_ranges", ""),
        "margin": {
            "top": f"{options.get('margin_top', 0)}mm",
            "right": f"{options.get('margin_right', 0)}mm",
            "bottom": f"{options.get('margin_bottom', 0)}mm",
            "left": f"{options.get('margin_left', 0)}mm",
        },
        "prefer_css_page_size": False,
    }

    # Handle custom page sizes
    if options.get("page_size") == "Custom":
        playwright_options["width"] = f"{options.get('page_width', 210)}mm"
        playwright_options["height"] = f"{options.get('page_height', 297)}mm"
        # Remove format when using custom dimensions
        playwright_options.pop("format", None)

    # Clean up None values
    playwright_options = {k: v for k, v in playwright_options.items() if v is not None}

    return playwright_options


def fallback_to_wkhtmltopdf(html, options, output):
    """Fallback to Frappe's wkhtmltopdf generator"""
    frappe.logger().warning("Using wkhtmltopdf fallback for PDF generation")

    try:
        return frappe_get_pdf(html, options, output)
    except Exception as e:
        frappe.log_error(f"wkhtmltopdf fallback also failed: {e}")
        raise


def check_chrome_status():
    """Check if Chrome is running and return status"""
    from .chrome_manager import get_chrome_manager

    try:
        manager = get_chrome_manager()
        if manager.is_running():
            return {"status": "running", "port": manager.port}
        else:
            return {"status": "stopped"}
    except Exception:
        return {"status": "error"}
