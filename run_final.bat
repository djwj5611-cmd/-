@echo off
REM Change directory to the script's location
cd /d "%~dp0"

REM TrendMasterV3 Execution Script
REM This script performs trend analysis using Docker.

ECHO [Step 1/3] Checking if Docker is running...
docker ps > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO [Error] Docker is not running.
    ECHO Please start Docker Desktop and try again.
    pause
    exit /b 1
)
ECHO [Success] Docker is active.
ECHO.

ECHO [Step 2/3] Building the TrendMasterV3 Docker image. (This may take some time on the first run)
docker build -t trendmaster-v3 .
IF %ERRORLEVEL% NEQ 0 (
    ECHO [Error] Failed to build Docker image.
    ECHO Please check the Dockerfile or your network connection.
    pause
    exit /b 1
)
ECHO [Success] Image build complete.
ECHO.

ECHO [Step 3/3] Running the trend analysis container.
ECHO This task may take a few minutes. Please wait...
ECHO.

REM Create the results folder if it doesn't exist
IF NOT EXIST .\results (
    mkdir .\results
)

REM Run the Docker container.
REM --rm : Automatically remove the container when it exits
REM -v "%cd%\results:/app/results" : Mounts the local results folder to the container's results folder
docker run --rm -v "%cd%\results:/app/results" trendmaster-v3

ECHO.
ECHO [Complete] All tasks are finished.
ECHO Please check the report file in the 'results' folder.
pause
