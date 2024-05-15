from setuptools import setup, find_packages

import certbot_dns_mydnsjp

with open("Readme.md") as f:
    long_description = f.read()

setup(
    name="certbot_dns_mydnsjp",
    author="usk-johnny-s",
    url="https://github.com/usk-johnny-s/certbot_dns_mydnsjp/",
    description="Authenticator plugin for certbot to handle dns-01 challenge with MyDNS.JP.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    use_scm_version=True,
    include_package_data=True,
    setup_requires=[
        "setuptools>=64",
        "setuptools_scm>=8"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
        "Topic :: System :: Systems Administration"
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "certbot>=1.18.0,<3.0",
        "requests>=2.20.0,<3.0"
    ],
    entry_points={
        "certbot.plugins": [
            "dns-mydnsjp = certbot_dns_mydnsjp.cert.client:Authenticator",
        ]
    }
)
