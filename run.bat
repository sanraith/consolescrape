@echo off
cmd /k "venv\Scripts\activate.bat & python consolescrape.py & venv\Scripts\deactivate.bat & echo."
