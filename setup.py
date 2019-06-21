#! /usr/bin/env python
from setuptools import find_packages, setup

tests_require = [
    "pytest-cov",
    "pytest-mock",
    "responses",
    "pytest-server-fixtures[s3]",
]

setup(
    name="piedpiper",
    use_scm_version=True,
    description="Libraries and CLI tools to interact with piedpiper",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    author="Nick Shobe",
    author_email="nickshobe@gmail.com",
    license="MIT License",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "attrdict",
        "pyyaml",
        "marshmallow",
        "requests",
        "minio",
        "subresource-integrity",
    ],
    setup_requires=["setuptools-scm"],
    extras_require={"test": tests_require},
    tests_require=tests_require,
    entry_points={"console_scripts": ["sritool=piedpiper.cli.sri:main"]},
)
