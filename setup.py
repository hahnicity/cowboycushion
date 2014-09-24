#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = "0.1"


setup(
    name="cowboycushion",
    author="Gregory Rehm",
    version=__version__,
    description="Rate limiting libraries for Python API clients",
    packages=find_packages(),
    package_data={"*": ["*.html"]},
)
