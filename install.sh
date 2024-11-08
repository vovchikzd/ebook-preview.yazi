#!/usr/bin/env bash

if [ -f ./get-ebook-cover.py ]; then
  ln -s "$PWD/get-ebook-cover.py" /usr/bin/get-ebook-cover
else
  printf "\033[0;31mCan't find get-ebook-cover.py file\033[0m\n"
fi
