import os

from setuptools import find_packages, setup


# Get version from __init__.py
def get_version():
    with open(os.path.join("frappe_puppeteer_pdf", "__init__.py"), "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return eval(line.split("=")[1].strip())
    return "1.0.0"


# Read requirements from requirements.txt
def get_requirements():
    with open("requirements.txt", "r") as f:
        return f.read().strip().split("\n")


setup(
    name="frappe_puppeteer_pdf",
    version=get_version(),
    description="Frappe App to generate PDFs using Puppeteer/Chrome",
    author="Frappe Technologies Pvt Ltd.",
    author_email="hello@frappe.io",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=get_requirements(),
)
