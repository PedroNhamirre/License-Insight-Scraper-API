@echo off
setlocal

set "APP_MODULE=main:app"
if not defined HOST set "HOST=0.0.0.0"
if not defined PORT set "PORT=8000"
if not defined VENV_DIR set "VENV_DIR=.venv"

if not exist "%VENV_DIR%\Scripts\python.exe" (
    python -m venv "%VENV_DIR%"
)

call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if not exist ".env" (
    copy ".env.example" ".env" >nul
)

uvicorn "%APP_MODULE%" --host "%HOST%" --port "%PORT%"

endlocal
