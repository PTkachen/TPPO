"#!/usr/bin/python3"

from setuptools import setup, find_packages
import equipmentdiagnostics

setup(
    name='equipmentdiagnostics',
    version='0.0.1',
    packages=find_packages(),
    entry_points={'console_scripts': ['equipmentdiagnostics = equipmentdiagnostics.main:main',]},
    include_package_data=True
)
