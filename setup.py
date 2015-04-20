#!/usr/bin/env python

from setuptools import setup, find_packages


requirements = [
    'eventbrite',
    'premo',
    'sume',
]


setup(
    name='bookie',
    version='0.0.1',
    url='https://www.github.com/eb-ninja/bookie',
    author='cieplak@eventbrite.com',
    description='sell stuff',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=requirements,
    tests_require=['nosetests', 'mock>=0.8'],
    scripts=['bin/bookie'],
)
