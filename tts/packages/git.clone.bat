@echo off
set "repo_path=tts\packages\vits"

if exist "%repo_path%" (
    echo The folder %repo_path% already exists. Skipping clone.
) else (
    echo The folder %repo_path% does not exist. Cloning VITS...
    git clone https://github.com/jaywalnut310/vits.git "%repo_path%"
    echo Clone complete.
)
@REM pause
