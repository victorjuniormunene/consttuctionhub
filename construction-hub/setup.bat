@echo off
REM Batch script for Construction Hub Django Project setup on Windows

REM Variables
set VENV=venv
set PYTHON=%VENV%\Scripts\python.exe
set PIP=%VENV%\Scripts\pip.exe
set MANAGE=%PYTHON% manage.py

REM Default target
if "%1"=="help" goto help
if "%1"=="install" goto install
if "%1"=="migrate" goto migrate
if "%1"=="superuser" goto superuser
if "%1"=="run" goto run
if "%1"=="setup" goto setup
if "%1"=="clean" goto clean
goto help

:help
echo Available targets:
echo   install    - Create virtual environment and install dependencies
echo   migrate    - Run database migrations
echo   superuser  - Create a superuser
echo   run        - Start the development server
echo   setup      - Full setup: install, migrate, superuser
echo   clean      - Remove virtual environment and cache files
goto end

:install
python -m venv %VENV%
%PIP% install --upgrade pip
%PIP% install -r requirements.txt
goto end

:migrate
%MANAGE% migrate
goto end

:superuser
%MANAGE% createsuperuser
goto end

:run
%MANAGE% runserver
goto end

:setup
call :install
call :migrate
call :superuser
goto end

:clean
rmdir /s /q %VENV%
for /d %%i in (__pycache__) do rmdir /s /q "%%i"
del /q *.pyc
del /q db.sqlite3
goto end

:end
