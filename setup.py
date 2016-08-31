#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'msgpack-python>=0.4.8,<0.5',
    'toml>=0.9.0,<0.10',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='logdispatchr',
    version='0.1.0',
    description="An attempt at a simple syslog-compatible(?) log dispatcher and filter",
    long_description=readme + '\n\n' + history,
    author="Paul Ollivier",
    author_email='contact@paulollivier.fr',
    url='https://github.com/paulollivier/logdispatchr',
    packages=[
        'logdispatchr',
    ],
    package_dir={'logdispatchr':
                 'logdispatchr'},
    entry_points={
        'console_scripts': [
            'logdispatchrd=logdispatchr.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='logdispatchr',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
