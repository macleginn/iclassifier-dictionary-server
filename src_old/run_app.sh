#! /bin/bash

/home/macleginn/.local/bin/gunicorn -b 127.0.0.1:15000 --reload --chdir /home/macleginn/iclf/iclassifier-dictionary-server/src app:app
