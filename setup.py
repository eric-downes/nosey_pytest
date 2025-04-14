#!/usr/bin/env python

from setuptools import setup, find_packages

description = (
    'Nosey-pytest - Tools to help migrate from nose to pytest'
)

setup(
    name='nosey_pytest',
    author="eric-downes",
    author_email="eric@triskew.com",
    version='0.1.0',
    description=description,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/eric-downes/nosey_pytest',
    license='MIT',
    packages=find_packages(include=['src', 'src.*']),
    py_modules=['migrate', 'pytest_migration'],
    install_requires=[
        'pytest>=7.0.0',
        'gitpython>=3.1.0',
        'fissix>=21.11.13',  # Required for nose2pytest
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Testing',
    ],
    entry_points={
        'console_scripts': [
            'pytest-migration=pytest_migration:main',
            'nose-to-pytest=migrate:main',
        ],
    },
    python_requires='>=3.8',
)
