
// Minimal client script for Print Format doctype to support puppeteer
frappe.ui.form.on('Print Format', {
    refresh: function(frm) {
        // Add puppeteer info when print_designer is enabled
        if (frm.doc.print_designer) {
            // Ensure pdf_generator is set to puppeteer by default
            if (!frm.doc.pdf_generator || frm.doc.pdf_generator !== 'puppeteer') {
                frm.set_value('pdf_generator', 'puppeteer');
            }

            // Add info message about puppeteer
            frm.dashboard.add_comment(
                __('This print format will use Puppeteer/Chrome for PDF generation.'),
                'blue',
                true
            );
        }
    },

    print_designer: function(frm) {
        // When print_designer is enabled/disabled, update pdf_generator
        if (frm.doc.print_designer) {
            frm.set_value('pdf_generator', 'puppeteer');
        } else if (frm.doc.pdf_generator === 'puppeteer') {
            // If disabling print_designer but pdf_generator is still puppeteer, reset to default
            frm.set_value('pdf_generator', 'wkhtmltopdf');
        }
    },

    pdf_generator: function(frm) {
        // Validate pdf_generator selection for print_designer formats
        if (frm.doc.print_designer && frm.doc.pdf_generator !== 'puppeteer') {
            frappe.msgprint({
                title: __('Warning'),
                message: __('Print Designer formats work best with Puppeteer PDF generator.'),
                indicator: 'orange'
            });
        }
    }
});

// Add custom button for testing puppeteer PDF generation
frappe.ui.form.on('Print Format', {
    onload: function(frm) {
        if (frm.doc.print_designer) {
            frm.add_custom_button(__('Test Puppeteer PDF'), function() {
                frappe.call({
                    method: 'frappe.utils.print_format.download_pdf',
                    args: {
                        doctype: 'Print Format',
                        name: frm.doc.name,
                        format: frm.doc.name,
                        no_letterhead: 0,
                        letterhead: null,
                        settings: null
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint({
                                title: __('Success'),
                                message: __('PDF generated successfully with Puppeteer'),
                                indicator: 'green'
                            });
                        }
                    }
                });
            }, __('Test'));
        }
    }
});
