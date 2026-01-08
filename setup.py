import setuptools

# Simple setup.py for Frappe app
# Frappe bench handles version detection differently

setuptools.setup(
    name="frappe_puppeteer_pdf",
    version="1.0.0",
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
