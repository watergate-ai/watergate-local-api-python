from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="watergate_local_api", # Replace with your own username
    version="2024.1.11",
    author="Watergate",
    author_email="hi@watergate.ai",
    description="Python package to interact with the Watergate Local API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hero-laboratories/watergate-local-api-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ]
)