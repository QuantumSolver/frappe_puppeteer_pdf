from setuptools import find_packages, setup

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in frappe_puppeteer_pdf/__init__.py
from frappe_puppeteer_pdf import __version__ as version

setup(
    name="frappe_puppeteer_pdf",
    version=version,
    description="Frappe App to generate PDFs using Puppeteer/Chrome",
    author="Frappe Technologies Pvt Ltd.",
    author_email="hello@frappe.io",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
