# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from odata import version


requires = (
    'requests>=2.0',
)

setup(
    name='odata',
    version=version,
    description='A simple library for read/write access to OData services.',
    author='Tuomas Mursu',
    author_email='tuomas.mursu@kapsi.fi',
    install_requires=requires,
    packages=find_packages(),
)
