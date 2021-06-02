#!/bin/bash

sudo apt install python3-pip debmake debhelper-compat dh-python python3-all mysql-server
sudo pip3 install setuptools numpy matplotlib tensorflow scipy mysql-connector-python detect_delimiter

python3 setup.py sdist

cd dist && mv equipmentdiagnostics*.tar.gz ../
cd ..

#mv equipmentdiagnostics*.tar.gz deb

mkdir deb
tar -C "deb" -xzmf equipmentdiagnostics*.tar.gz
cd deb
cd ..

rm -r ~/.edconf > /dev/null
mkdir -p ~/.edconf/
sudo cp -r equipmentdiagnostics/model ~/.edconf/

cd deb
cd equipmentdiagnostics*

sudo debmake -n -b':python3'

sudo debuild
