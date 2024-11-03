#!/usr/bin/env bash

if [ -f ./ebook-preview.py ]; then
  ln -s "$PWD/ebook-preview.py" /usr/bin/ebook-preview
else
  printf "\033[0;31mCan't fing ebook-preview.py file\033[0m\n"
fi
