#!/bin/bash

# A shell script wrapper for the CMD from the Dockerfile that can accept arguments
python3 -m gunicorn -b 0.0.0.0:30000 app:app