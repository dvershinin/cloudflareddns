#!/usr/bin/env python
"""
cloudflareddns
==========
.. code:: shell
  $ cloudflareddns --email <email> --key <api_key> [--hostname <hostname>] --ip <ip_address>
  $ cloudflareddns-syno <email> <api_key> <hostname> <ip_address>
"""

from setuptools import find_packages, setup
import os

install_requires = [
    "requests",
    "tldextract",
    "cloudflare>=2.3.1"
]
tests_requires = ["pytest", "flake8", "faker"]

with open("README.md", "r") as fh:
    long_description = fh.read()

base_dir = os.path.dirname(__file__)

version = {}
with open(os.path.join(base_dir, "cloudflareddns", "__about__.py")) as fp:
    exec(fp.read(), version)

setup(
    name="cloudflareddns",
    version=version["__version__"],
    author="Danila Vershinin",
    author_email="info@getpagespeed.com",
    url="https://github.com/dvershinin/cloudflareddns",
    description="A CLI tool to use Cloudflare as a DDNS provider",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    license="BSD",
    install_requires=install_requires,
    extras_require={
        "tests": install_requires + tests_requires,
    },
    tests_require=tests_requires,
    include_package_data=True,
    entry_points={"console_scripts": ["cloudflareddns = cloudflareddns:main", "cloudflareddns-syno = cloudflareddns:syno"]},
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
    ],
)
