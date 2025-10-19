#!/bin/bash

set -e

# Use python3.9 to be specific
python3.9 manage.py collectstatic --noinput --clear