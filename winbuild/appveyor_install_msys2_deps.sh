#!/bin/sh

mkdir /var/cache/pacman/pkg
pacman -S --noconfirm mingw32/mingw-w64-i686-python3-pip \
     mingw32/mingw-w64-i686-python3-setuptools \
     mingw32/mingw-w64-i686-python3-pytest \
     mingw32/mingw-w64-i686-python3-pytest-cov \
     mingw-w64-i686-libjpeg-turbo \
     mingw-w64-i686-libimagequant

python3 -m pip install --upgrade pip

pip install olefile
pip3 install olefile
