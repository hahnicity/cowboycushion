#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = "0.3"


setup(
    name="cowboycushion",
    author="Gregory Rehm",
    version=__version__,
    description="Rate limiting libraries for Python API clients",
    packages=find_packages(),
    package_data={"*": ["*.html"]},
    install_requires=["redis"],
    tests_require=["mock", "mockredispy"]
)
