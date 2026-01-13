CUSTOM_FIELDS = {
	"Print Format": [
		{
			"fieldname": "pdf_page_orientation",
			"fieldtype": "Select",
			"label": "Page Orientation",
			"options": "Portrait\nLandscape",
			"default": "Portrait",
			"depends_on": "eval:doc.pdf_generator=='chrome'",
			"insert_after": "pdf_generator",
		},
	]
}
