@echo off
:: Gradle wrapper script for Windows (copied from MyApp)
:: This script downloads and runs Gradle

set GRADLE_VERSION=8.1.1
set GRADLE_DIST_URL=https://services.gradle.org/distributions/gradle-%GRADLE_VERSION%-bin.zip
set GRADLE_USER_HOME=%USERPROFILE%\.gradle
set WRAPPER_DIR=%~dp0
set GRADLE_HOME=%GRADLE_USER_HOME%\wrapper\dists\gradle-%GRADLE_VERSION%-bin

:: Download and extract Gradle if not present
if not exist "%GRADLE_HOME%\gradle-%GRADLE_VERSION%\bin\gradle.bat" (
    echo Downloading Gradle %GRADLE_VERSION%...
    mkdir "%GRADLE_HOME%" 2>nul
    cd /d "%GRADLE_HOME%"
    curl -L -o gradle.zip "%GRADLE_DIST_URL%"
    powershell -command "Expand-Archive -Force gradle.zip"
    del gradle.zip
)

:: Run Gradle
"%GRADLE_HOME%\gradle-%GRADLE_VERSION%\bin\gradle.bat" %*
