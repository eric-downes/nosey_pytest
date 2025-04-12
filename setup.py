#!/usr/bin/env python

from setuptools import setup, find_packages

description = (
    'Pytest Migration Tools - Utilities to help migrate from nose to pytest'
)

setup(
    name='pytest_migration',
    author="Eric Downes",
    author_email="eric.downes@gmail.com",
    version='0.1.0',
    description=description,
    packages=find_packages(),
    install_requires=[
        'pytest>=7.0.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing',
    ],
    entry_points={
        'console_scripts': [
            'pytest_migration=pytest_migration:main',
        ],
    },
)
