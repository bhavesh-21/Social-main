@echo off
REM Check if Python is installed
python --version
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

REM Check if the venv module is available
python -c "import venv" 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo The venv module is not available. Attempting to install...
    python -m pip install --user virtualenv
    IF %ERRORLEVEL% NEQ 0 (
        echo Failed to install virtualenv. Please install the venv module or virtualenv package manually and try again.
        exit /b 1
    )
)

REM Create a virtual environment named 'venv'
echo Creating virtual environment...
python -m venv venv

REM Check if the virtual environment was created successfully
IF NOT EXIST venv (
    echo Failed to create virtual environment.
    exit /b 1
)

REM Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Check if the requirements.txt file exists
IF NOT EXIST requirements.txt (
    echo requirements.txt file not found.
    exit /b 1
)

REM Install the dependencies from requirements.txt
echo Installing dependencies...
pip install -r requirements.txt

REM Check if the installation was successful
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies.
    exit /b 1
)

echo Setup complete. The virtual environment is ready and dependencies are installed.