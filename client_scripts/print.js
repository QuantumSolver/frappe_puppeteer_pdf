// Minimal client script for puppeteer PDF generator
frappe.pages["print"].on_page_load = function (wrapper) {
    // Load PDF viewer CSS
    frappe.require(["pdfjs.bundle.css"]);
    frappe.ui.make_app_page({
        parent: wrapper,
    });

    let print_view = new frappe.ui.form.PrintView(wrapper);

    $(wrapper).bind("show", () => {
        const route = frappe.get_route();
        const doctype = route[1];
        const docname = route.slice(2).join("/");

        if (!frappe.route_options || !frappe.route_options.frm) {
            frappe.model.with_doc(doctype, docname, () => {
                let frm = { doctype: doctype, docname: docname };
                frm.doc = frappe.get_doc(doctype, docname);
                frappe.model.with_doctype(doctype, () => {
                    frm.meta = frappe.get_meta(route[1]);
                    print_view.show(frm);
                });
            });
        } else {
            print_view.frm = frappe.route_options.frm.doctype
                ? frappe.route_options.frm
                : frappe.route_options.frm.frm;
            frappe.route_options.frm = null;
            print_view.show(print_view.frm);
        }
    });
};

// Override print view to ensure puppeteer is used when available
frappe.ui.form.PrintView = class PrintView extends frappe.ui.form.PrintView {
    show(frm) {
        super.show(frm);

        // Check if current print format uses puppeteer
        const print_format = this.print_format_select.val();
        if (print_format) {
            frappe.db.get_value('Print Format', print_format, 'pdf_generator').then(r => {
                if (r.message && r.message.pdf_generator === 'puppeteer') {
                    // Add indicator that puppeteer is being used
                    this.page.set_title(__('Print (Puppeteer)'));
                }
            });
        }
    }

    print_doc() {
        // Ensure puppeteer is selected for print designer formats
        const print_format = this.print_format_select.val();
        if (print_format) {
            frappe.db.get_value('Print Format', print_format, ['print_designer', 'pdf_generator']).then(r => {
                if (r.message && r.message.print_designer && r.message.pdf_generator !== 'puppeteer') {
                    // Suggest switching to puppeteer
                    frappe.show_alert({
                        message: __('This print format may work better with Puppeteer PDF generator'),
                        indicator: 'blue'
                    }, 5);
                }
            });
        }

        // Call original print method
        return super.print_doc();
    }
};
