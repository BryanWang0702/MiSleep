# -*- coding: UTF-8 -*-
# Copyright (C) 2024 Xueqiang Wang

DESCRIPTION = "MiSleep: Mice Sleep EEG/EMG visualization, scoring and analysis."
with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

DISTNAME = "MiSleep"
MAINTAINER = "Xueqiang Wang"
MAINTAINER_EMAIL = "swang@gmail.com"
URL = "https://github.com/BryanWang0702/MiSleep/"
LICENSE = "BSD (3-clause)"
DOWNLOAD_URL = "https://github.com/BryanWang0702/MiSleep/"
VERSION = "0.1.0"

INSTALL_REQUIRES = [
    "numpy>=1.18.1",
    "matplotlib",
    "scipy",
    "pyedflib",
    "hdf5storage",
]

PACKAGES = [
    "MiSleep",
]

CLASSIFIERS = [
    "Intended Audience :: Science/Research",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "License :: OSI Approved :: BSD License",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Operating System :: MacOS",
]

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if __name__ == "__main__":
    setup(
        name=DISTNAME,
        author=MAINTAINER,
        author_email=MAINTAINER_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license=LICENSE,
        url=URL,
        version=VERSION,
        download_url=DOWNLOAD_URL,
        install_requires=INSTALL_REQUIRES,
        include_package_data=True,
        packages=PACKAGES,
        classifiers=CLASSIFIERS,
    )