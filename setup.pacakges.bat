@echo off
echo Checking and executing asr's git.clone.bat...
call asr\packages\git.clone.bat

echo Checking and executing tts's git.clone.bat...
call tts\packages\git.clone.bat

echo All clone operations checks completed.
pause
