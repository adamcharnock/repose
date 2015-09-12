#!/usr/bin/env python

from os.path import exists
from setuptools import setup, find_packages


setup(
    name='repose',
    version=open('VERSION').read().strip(),
    # Your name & email here
    author='Adam Charnock',
    author_email='adam@adamcharnock.com',
    # If you had repose.tests, you would also include that in this list
    packages=find_packages(),
    # Any executable scripts, typically in 'bin'. E.g 'bin/do-something.py'
    scripts=[],
    # REQUIRED: Your project's URL
    url='http://github.com/adamcharnock/repose',
    # Put your license here. See LICENSE.txt for more information
    license='',
    # Put a nice one-liner description here
    description='Quickly create restful API clients in Python',
    long_description=open('README.rst').read() if exists("README.rst") else "",
    # Any requirements here, e.g. "Django >= 1.1.1"
    install_requires=[
        'booby==0.7.0',
        'requests==2.7.0',
        'six',
    ],
)
