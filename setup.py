import os
import re

from setuptools import find_packages, setup


def get_version():
    """Read version from __init__.py without importing the module"""
    init_path = os.path.join(
        os.path.dirname(__file__), "frappe_puppeteer_pdf", "__init__.py"
    )

    with open(init_path, "r") as f:
        content = f.read()

    version_match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.M)

    if version_match:
        return version_match.group(1)
    else:
        return "1.0.0"


with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="frappe_puppeteer_pdf",
    version=get_version(),
    description="Frappe App to generate PDFs using Puppeteer/Chrome",
    author="Frappe Technologies Pvt Ltd.",
    author_email="hello@frappe.io",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
