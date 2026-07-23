from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    # Version is provided by setuptools-scm (see pyproject.toml [tool.setuptools_scm]);
    # it is derived from the git tag, so there is no version string to maintain here.
    name="watergate_local_api",
    author="Watergate",
    author_email="hi@watergate.ai",
    description="Python package to interact with the Watergate Local API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/watergate-ai/watergate-local-api-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ]
)