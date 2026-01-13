import frappe
from frappe.utils.pdf import get_pdf as frappe_get_pdf
from playwright.sync_api import sync_playwright

from .chrome_manager import ensure_chrome_running


def before_request():
    """Set pdf_generator to chrome for print designer formats"""
    if (
        frappe.request.path == "/api/method/frappe.utils.print_format.download_pdf"
        or frappe.request.path == "/printview"
    ):
        # Get the print format being requested
        print_format = frappe.request.args.get("format")
        if print_format:
            pdf_generator = frappe.get_cached_value(
                "Print Format", print_format, "pdf_generator"
            )

            # Set pdf_generator in form_dict
            if pdf_generator == "chrome":
                frappe.local.form_dict.pdf_generator = "chrome"
            else:
                frappe.local.form_dict.pdf_generator = frappe.request.args.get(
                    "pdf_generator", pdf_generator or "wkhtmltopdf"
                )

        # Initialize Chrome if chrome is being used
        if frappe.local.form_dict.get("pdf_generator") == "chrome":
            try:
                ensure_chrome_running()
            except Exception as e:
                frappe.log_error(f"Failed to start Chrome: {e}")
                # Fallback to wkhtmltopdf
                frappe.local.form_dict.pdf_generator = "wkhtmltopdf"


def after_request():
    """Cleanup after request"""
    # We keep Chrome running for performance, but could stop it here
    # stop_chrome()  # Uncomment if you want to stop Chrome after each request


def get_pdf(print_format, html, options=None, output=None, pdf_generator=None):
    """Main PDF generation function called by Frappe"""
    if pdf_generator != "chrome":
        # Let Frappe use default PDF generator
        return None

    try:
        frappe.logger().info(
            f"Generating PDF with chrome/playwright for format: {print_format}"
        )

        # Get orientation from Print Format
        if not options:
            options = {}
        if print_format:
            orientation = frappe.get_cached_value("Print Format", print_format, "pdf_page_orientation")
            if orientation:
                options["orientation"] = orientation

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
        frappe.log_error(f"Chrome PDF generation failed for {print_format}: {e}")
        frappe.logger().error(f"Falling back to wkhtmltopdf: {e}")

        # Fallback to Frappe's default PDF generator
        return fallback_to_wkhtmltopdf(html, options, output)


def generate_with_playwright(html, options, chrome_manager):
    """Generate PDF using Playwright connected to Chrome"""
    # Strip print-hide elements (Print/Get PDF buttons)
    import re
    html = re.sub(r'<div class="action-banner print-hide">.*?</div>', '', html, flags=re.DOTALL)

    with sync_playwright() as p:
        try:
            # Connect to running Chrome instance
            browser = p.chromium.connect_over_cdp(chrome_manager.get_connection_url())

            # Create new page
            page = browser.new_page()

            # Set HTML content
            page.set_content(html, wait_until="networkidle")

            # Emulate print media to apply @media print styles
            page.emulate_media(media="print")

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
