#!/usr/bin/env python

from setuptools import setup, find_packages

description = (
    'Nosey-pytest - Tools to help migrate from nose to pytest'
)

setup(
    name='nosey_pytest',
    author="Eric Downes",
    author_email="eric.downes@gmail.com",
    version='0.1.0',
    description=description,
    packages=find_packages(include=['src', 'src.*']),
    py_modules=['migrate', 'pytest_migration'],
    install_requires=[
        'pytest>=7.0.0',
        'gitpython>=3.1.0',
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
            'pytest-migration=pytest_migration:main',
            'nose-to-pytest=migrate:main',
        ],
    },
)
