@echo off
REM Auto-delivery script for food ordering system (Windows)
REM This script should be run every hour via Windows Task Scheduler

cd /d "C:\path\to\your\django\project"
call venv\Scripts\activate.bat
python manage.py auto_deliver_orders
