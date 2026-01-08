import re
from typing import Literal

import frappe
from frappe.model.document import BaseDocument
from frappe.utils.jinja import get_jenv


@frappe.whitelist(allow_guest=False)
def render_user_text(string, doc, row=None, send_to_jinja=None):
    """Render user-provided Jinja template text"""
    if not row:
        row = {}
    if not send_to_jinja:
        send_to_jinja = {}

    jinja_vars = {}
    if isinstance(send_to_jinja, dict):
        jinja_vars = send_to_jinja
    elif send_to_jinja != "" and isinstance(send_to_jinja, str):
        try:
            jinja_vars = frappe.parse_json(send_to_jinja)
        except Exception:
            pass

    if not (isinstance(row, dict) or issubclass(row.__class__, BaseDocument)):
        if isinstance(row, str):
            try:
                row = frappe.parse_json(row)
            except Exception:
                raise TypeError("row must be a dict")
        else:
            raise TypeError("row must be a dict")

    if not issubclass(doc.__class__, BaseDocument):
        # This is when we send doc from client side as a json string
        if isinstance(doc, str):
            try:
                doc = frappe.parse_json(doc)
            except Exception:
                raise TypeError("doc must be a dict or subclass of BaseDocument")

    jenv = get_jenv()
    result = {}
    try:
        result["success"] = 1
        result["message"] = jenv.from_string(string).render(
            {"doc": doc, "row": row, **jinja_vars}
        )
    except Exception as e:
        """
        string is provided by user and there is no way to know if it is correct or not so log the error from client side
        """
        result["success"] = 0
        result["error"] = e
    return result


@frappe.whitelist(allow_guest=False)
def render_user_text_withdoc(
    string, doctype, docname=None, row=None, send_to_jinja=None
):
    """Render Jinja template text with document fetched from database"""
    if not row:
        row = {}
    if not send_to_jinja:
        send_to_jinja = {}

    if not docname or docname == "":
        return render_user_text(
            string=string, doc={}, row=row, send_to_jinja=send_to_jinja
        )

    doc = frappe.get_cached_doc(doctype, docname)
    doc.check_permission()
    return render_user_text(
        string=string, doc=doc, row=row, send_to_jinja=send_to_jinja
    )


@frappe.whitelist()
def convert_css(css_obj):
    """Convert CSS object to string for inline styles"""
    string_css = ""
    if css_obj:
        for item in css_obj.items():
            string_css += (
                "".join(
                    ["-" + i.lower() if i.isupper() else i for i in item[0]]
                ).lstrip("-")
                + ":"
                + str(
                    item[1]
                    if item[1] != "" or item[0] != "backgroundColor"
                    else "transparent"
                )
                + "!important;"
            )
    string_css += "user-select: all;"
    return string_css


@frappe.whitelist()
def convert_uom(
    number: float,
    from_uom: Literal["px", "mm", "cm", "in"] = "px",
    to_uom: Literal["px", "mm", "cm", "in"] = "px",
    only_number: bool = False,
) -> float:
    """Convert between different units of measurement"""
    unit_values = {
        "px": 1,
        "mm": 3.7795275591,
        "cm": 37.795275591,
        "in": 96,
    }

    if from_uom == to_uom:
        return number

    # Convert to pixels first
    if from_uom != "px":
        number = number * unit_values[from_uom]

    # Convert from pixels to target unit
    if to_uom != "px":
        number = number / unit_values[to_uom]

    if only_number:
        return round(number, 3)
    return f"{round(number, 3)}{to_uom}"


@frappe.whitelist()
def get_barcode(
    barcode_format,
    barcode_value,
    options=None,
    width=None,
    height=None,
    png_base64=False,
):
    """Generate barcode or QR code"""
    if not options:
        options = {}

    options = frappe.parse_json(options)

    if isinstance(barcode_value, str) and barcode_value.startswith("<svg"):
        import re

        barcode_value = re.search(r'data-barcode-value="(.*?)">', barcode_value).group(
            1
        )

    if barcode_value == "":
        fallback_html_string = """
            <div class="fallback-barcode">
                <div class="content">
                    <span>No Value was Provided to Barcode</span>
                </div>
            </div>
        """
        return {"type": "svg", "value": fallback_html_string}

    if barcode_format == "qrcode":
        return get_qrcode(barcode_value, options, png_base64)

    import base64
    from io import BytesIO

    import barcode
    from barcode.writer import ImageWriter, SVGWriter

    class PDSVGWriter(SVGWriter):
        def __init__(self):
            SVGWriter.__init__(self)

        def calculate_viewbox(self, code):
            vw, vh = self.calculate_size(len(code[0]), len(code))
            return vw, vh

        def _init(self, code):
            SVGWriter._init(self, code)
            vw, vh = self.calculate_viewbox(code)
            if not width:
                self._root.removeAttribute("width")
            else:
                self._root.setAttribute("width", f"{width * 3.7795275591}")
            if not height:
                self._root.removeAttribute("height")
            else:
                self._root.setAttribute("height", height)

            self._root.setAttribute(
                "viewBox", f"0 0 {vw * 3.7795275591} {vh * 3.7795275591}"
            )

    if barcode_format not in barcode.PROVIDED_BARCODES:
        return f"Barcode format {barcode_format} not supported. Valid formats are: {barcode.PROVIDED_BARCODES}"

    writer = ImageWriter() if png_base64 else PDSVGWriter()
    barcode_class = barcode.get_barcode_class(barcode_format)

    try:
        barcode_obj = barcode_class(barcode_value, writer)
    except Exception:
        frappe.msgprint(
            f"Invalid barcode value <b>{barcode_value}</b> for format <b>{barcode_format}</b>",
            raise_exception=True,
            alert=True,
            indicator="red",
        )

    stream = BytesIO()
    barcode_obj.write(stream, options)
    barcode_value = stream.getvalue().decode("utf-8")
    stream.close()

    if png_base64:
        barcode_value = base64.b64encode(barcode_value.encode()).decode()

    return {"type": "png_base64" if png_base64 else "svg", "value": barcode_value}


def get_qrcode(barcode_value, options=None, png_base64=False):
    """Generate QR code"""
    import base64
    from io import BytesIO

    import pyqrcode

    if not options:
        options = {}

    options = frappe.parse_json(options)
    options = {
        "scale": options.get("scale", 5),
        "module_color": options.get("module_color", "#000000"),
        "background": options.get("background", "#ffffff"),
        "quiet_zone": options.get("quiet_zone", 1),
    }

    qr = pyqrcode.create(barcode_value)
    stream = BytesIO()

    if png_base64:
        qrcode_svg = qr.png_as_base64_str(**options)
    else:
        options.update(
            {
                "svgclass": "print-qrcode",
                "lineclass": "print-qrcode-path",
                "omithw": True,
                "xmldecl": False,
            }
        )
        qr.svg(stream, **options)
        qrcode_svg = stream.getvalue().decode("utf-8")
        stream.close()

    return {"type": "png_base64" if png_base64 else "svg", "value": qrcode_svg}


def pdf_header_footer_html(soup, head, content, styles, html_id, css):
    """Generate HTML for PDF header/footer"""
    from frappe.utils.pdf import pdf_footer_html, pdf_header_html

    if html_id == "header-html":
        return pdf_header_html(
            soup=soup,
            head=head,
            content=content,
            styles=styles,
            html_id=html_id,
            css=css,
        )
    else:
        return pdf_footer_html(
            soup=soup,
            head=head,
            content=content,
            styles=styles,
            html_id=html_id,
            css=css,
        )


def pdf_body_html(print_format, for_preview=False, debug=False, **kwargs):
    """Generate HTML for PDF body"""
    # Use Frappe's default implementation
    from frappe.utils.pdf import pdf_body_html as frappe_pdf_body_html

    return frappe_pdf_body_html(print_format, for_preview, debug, **kwargs)


def get_print_format_template():
    """Get print format template"""
    # Default implementation - can be overridden if needed
    return None
