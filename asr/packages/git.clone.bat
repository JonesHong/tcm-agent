@echo off
set "repo_path=asr\packages\WhisperLive"

if exist "%repo_path%" (
    echo The folder %repo_path% already exists. Skipping clone.
) else (
    echo The folder %repo_path% does not exist. Cloning WhisperLive...
    git clone https://github.com/collabora/WhisperLive.git "%repo_path%"
    echo Clone complete.
)
@REM pause
