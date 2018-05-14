#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
import sys

from setuptools import setup, find_packages

on_rtd = os.environ.get('READTHEDOCS') == 'True'

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


# requirements

# Basic requirements that contain no C extensions.
# This is necessary for building on RTD
requirements = []

if on_rtd:
    requirements += []
else:
    requirements += [
        'numpy >= 1.14.0',
        'numba >= 0.38.0',
        'scipy >= 1.0.1']

setup_requirements = ['pytest-runner', ]

if sys.version_info[0] == 3:
    astropy_req = "astropy >= 3.0.0"
else:
    astropy_req = "astropy >= 2.0.0, < 3.0.0"

test_requirements = [
        astropy_req,
        'python-casacore >= 2.2.1',
        'pytest',
        'dask[array] >= 0.17.4']

setup(
    author="Simon Perkins",
    author_email='sperkins@ska.ac.za',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Radio Astronomy Building Blocks",
    install_requires=requirements,
    license="GNU General Public License v2",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='codex-africanus',
    name='codex-africanus',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ska-sa/codex-africanus',
    version='0.1.2',
    zip_safe=False,
)
