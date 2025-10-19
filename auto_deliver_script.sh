#!/bin/bash
# Auto-delivery script for food ordering system
# This script should be run every hour via cron job
# Add this line to crontab: 0 * * * * /path/to/this/script.sh

cd /path/to/your/django/project
source venv/bin/activate  # if using virtual environment
python manage.py auto_deliver_orders
