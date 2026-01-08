# Frappe Puppeteer PDF Generator

A Frappe Framework app that generates PDFs using Puppeteer/Chrome instead of wkhtmltopdf. This app provides better CSS support, improved rendering, and modern PDF generation capabilities for Frappe print formats.

## Features

- **Puppeteer/Chrome PDF Generation**: Uses headless Chrome via Playwright for superior PDF rendering
- **Frappe Integration**: Works seamlessly with existing Frappe print formats
- **Print Designer Compatibility**: Compatible with Print Designer formats (`print_designer=1`)
- **Automatic Chrome Installation**: Downloads and sets up Chrome binaries automatically
- **Fallback Support**: Gracefully falls back to wkhtmltopdf if Chrome fails
- **Simple Configuration**: Just set `pdf_generator="puppeteer"` on your Print Format

## Installation

### Prerequisites
- Frappe Framework version 15 or higher
- Python 3.10+
- Internet connection (for Chrome download)

### Install from GitHub
```bash
bench get-app https://github.com/yourusername/frappe_puppeteer_pdf.git
bench install-app frappe_puppeteer_pdf
```

### Manual Installation
```bash
# Clone the app
git clone https://github.com/yourusername/frappe_puppeteer_pdf.git
cd frappe_puppeteer_pdf

# Install in your Frappe bench
bench get-app frappe_puppeteer_pdf $(pwd)
bench install-app frappe_puppeteer_pdf
```

## Usage

### 1. Configure Print Format
1. Open any Print Format in Frappe
2. Enable "Print Designer" checkbox
3. Set "PDF Generator" to "puppeteer"
4. Save the Print Format

### 2. Test PDF Generation
1. Open any document (e.g., Sales Invoice)
2. Click Print → Print Preview
3. Select your Print Format with `pdf_generator="puppeteer"`
4. Generate PDF - it will use Puppeteer/Chrome

## How It Works

### Chrome Management
- Automatically downloads Chrome binaries to `<bench>/chromium/`
- Starts Chrome with remote debugging enabled (port 9222)
- Manages Chrome process lifecycle
- Reuses Chrome instance for performance

### PDF Generation Flow
1. User requests PDF from Frappe
2. App checks if format uses `pdf_generator="puppeteer"`
3. Ensures Chrome is running (starts if needed)
4. Connects Playwright to Chrome via CDP
5. Renders HTML and generates PDF using Playwright
6. Returns PDF to user

### Fallback Mechanism
If Puppeteer/Chrome fails:
1. Logs the error
2. Falls back to Frappe's wkhtmltopdf
3. Continues working without interruption

## Configuration

### Common Site Config
Add to `common_site_config.json`:

```json
{
    "chromium_download_url": "optional_custom_url",
    "chromium_version": "133.0.6943.35",
    "playwright_chromium_version": "1157",
    "use_persistent_chromium": false
}
```

### Environment Variables
- `CHROMIUM_DOWNLOAD_URL`: Custom Chrome download URL
- `USE_SYSTEM_CHROME`: Use system Chrome if available

## Troubleshooting

### Chrome Won't Start
1. Check Chrome binary exists: `<bench>/chromium/chrome-linux/headless_shell`
2. Verify permissions: `chmod +x headless_shell`
3. Check port 9222 is available
4. Review logs: `bench --site your-site logs`

### PDF Generation Fails
1. Check Print Format has `print_designer=1`
2. Verify `pdf_generator="puppeteer"`
3. Test Chrome manually: `./chromium/chrome-linux/headless_shell --version`
4. Check network connectivity for Chrome download

### Performance Issues
1. Chrome uses ~100MB RAM per instance
2. Consider disabling persistent Chrome in config
3. Monitor Chrome processes: `ps aux | grep chrome`

## Development

### Setup Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run tests
python -m pytest tests/
```

### Project Structure
```
frappe_puppeteer_pdf/
├── hooks.py              # Frappe hooks
├── install.py            # Installation & Chrome setup
├── pdf_generator.py      # Main PDF generation logic
├── chrome_manager.py     # Chrome process management
├── pdf_utils.py          # Jinja helpers & utilities
├── overrides.py          # PrintFormat overrides
├── custom_fields.py      # Custom fields (from Print Designer)
├── uninstall.py          # Uninstallation cleanup
├── patches/              # Database patches
├── client_scripts/       # Client-side JavaScript
└── requirements.txt      # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit pull request

## License

AGPLv3

## Support

- GitHub Issues: https://github.com/yourusername/frappe_puppeteer_pdf/issues
- Documentation: See `docs/` folder
- Frappe Forum: https://discuss.frappe.io

## Acknowledgments

- Based on Frappe Print Designer's Chrome integration
- Uses Playwright for Chrome automation
- Compatible with existing Print Designer formats

## Changelog

### v1.0.0
- Initial release
- Puppeteer/Chrome PDF generation
- Chrome auto-download
- Frappe Print Format integration
- Fallback to wkhtmltopdf
```
Now let me create a quick validation script to check our implementation:

<｜DSML｜function_calls>
<｜DSML｜invoke name="terminal">
<｜DSML｜parameter name="command" string="true">find /home/ubuntu/print_designer/frappe_puppeteer_pdf -type f -name "*.py" | wc -l</｜DSML｜parameter>
<｜DSML｜parameter name="cd" string="true">/home/ubuntu/print_designer</｜DSML｜parameter>
</｜DSML｜invoke>
</｜DSML｜function_calls>