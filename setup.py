# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from odata import version


requires = (
    'requests>=2.0',
    'dateutil',
    'lxml',
)

tests_require = (
    'responses',
)

setup(
    name='odata',
    version=version,
    description='A simple library for read/write access to OData services.',
    license='MIT',
    author='Tuomas Mursu',
    author_email='tuomas.mursu@kapsi.fi',
    install_requires=requires,
    tests_require=tests_require,
    packages=find_packages(),
)
