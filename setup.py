import setuptools

# Setup for Frappe app with nested package structure
# Root: __init__.py (for Frappe version detection)
# Package: frappe_puppeteer_pdf/__init__.py (for Python packaging)

setuptools.setup(
    name="frappe_puppeteer_pdf",
    version="1.0.0",  # Frappe will read actual version from root __init__.py
    description="Frappe App to generate PDFs using Puppeteer/Chrome",
    author="Frappe Technologies Pvt Ltd.",
    author_email="hello@frappe.io",
    packages=setuptools.find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "playwright==1.40.0",
        "PyQRCode~=1.2.1",
        "pypng~=0.20220715.0",
        "python-barcode~=0.15.1",
        "distro",
    ],
)
