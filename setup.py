#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = "0.1"


setup(
    name="discourse",
    author="Gregory Rehm, David Rodriguez",
    version=__version__,
    description="Data analysis for the Disqus API",
    packages=find_packages(),
    package_data={"*": ["*.html"]},
    entry_points={
        "console_scripts": [
        ],
    },
    install_requires=[
	"disqus-python"
    ],
)