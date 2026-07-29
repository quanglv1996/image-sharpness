@echo off
REM Docker build and run helper script for Image Sharpness Analyzer
REM Usage: docker-run.bat [command]
REM Commands: build, up, down, logs, shell, clean

setlocal enabledelayedexpansion

set CONTAINER_NAME=image-sharpness-app
set IMAGE_NAME=image-sharpness:latest

if "%1"=="" (
    set COMMAND=up
) else (
    set COMMAND=%1
)

REM Check if docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed
    exit /b 1
)

REM Check if docker-compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed
    exit /b 1
)

if "%COMMAND%"=="build" (
    echo [INFO] Building Docker image...
    docker-compose build
    echo [INFO] Build complete!
) else if "%COMMAND%"=="up" (
    echo [INFO] Starting container...
    docker-compose up -d
    echo [INFO] Container started!
    echo [INFO] Access application at: http://localhost:5000
) else if "%COMMAND%"=="down" (
    echo [INFO] Stopping container...
    docker-compose down
    echo [INFO] Container stopped!
) else if "%COMMAND%"=="restart" (
    echo [INFO] Restarting container...
    docker-compose restart
    echo [INFO] Container restarted!
) else if "%COMMAND%"=="logs" (
    echo [INFO] Showing logs (Ctrl+C to exit)...
    docker-compose logs -f
) else if "%COMMAND%"=="shell" (
    echo [INFO] Opening shell in container...
    docker exec -it %CONTAINER_NAME% cmd
) else if "%COMMAND%"=="status" (
    echo [INFO] Checking container status...
    docker-compose ps
) else if "%COMMAND%"=="clean" (
    echo [WARN] Removing container and image...
    docker-compose down
    docker rmi %IMAGE_NAME% 2>nul
    echo [INFO] Cleaned up!
) else if "%COMMAND%"=="rebuild" (
    echo [INFO] Rebuilding everything...
    docker-compose down
    docker-compose up --build -d
    echo [INFO] Rebuild complete!
    echo [INFO] Access application at: http://localhost:5000
) else (
    echo Usage: %0 [command]
    echo.
    echo Commands:
    echo   build     - Build Docker image
    echo   up        - Start container (default)
    echo   down      - Stop container
    echo   restart   - Restart container
    echo   logs      - View container logs
    echo   shell     - Open shell in container
    echo   status    - Show container status
    echo   clean     - Remove container and image
    echo   rebuild   - Clean, rebuild and start
    exit /b 1
)
