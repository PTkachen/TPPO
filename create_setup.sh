#!/bin/bash

python3 setup.py sdist

cd dist && mv equipmentdiagnostics*.tar.gz ../
cd ..

#mv equipmentdiagnostics*.tar.gz deb

mkdir deb
tar -C "deb" -xzmf equipmentdiagnostics*.tar.gz
cd deb

cd equipmentdiagnostics*

sudo debmake -n -b':python3'

sudo debuild
