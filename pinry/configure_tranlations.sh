#!/bin/bash

#configure_tranlations.sh
echo "Generate the translation files"
django-admin.py makemessages -l en
django-admin.py makemessages -l d
django-admin.py makemessages -a -d djangojs
echo "Compiling the translation files"
django-admin.py compilemessages
