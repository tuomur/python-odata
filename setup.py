# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages

requires = [
    'requests>=2.22.0',
    'python-dateutil',
]

# support for enums from pypi when on older python
if sys.version_info < (3, 4):
    requires.append('enum34')

tests_require = (
    'responses',
)

setup(
    name='odata',
    version='0.3',
    description='A simple library for read/write access to OData services.',
    license='MIT',
    author='Tuomas Mursu',
    author_email='tuomas.mursu@kapsi.fi',
    install_requires=requires,
    tests_require=tests_require,
    packages=find_packages(),
)
