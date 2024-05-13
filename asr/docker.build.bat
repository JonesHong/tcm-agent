@echo off
echo Building Docker image...
docker build -t whisper_live -f .packages\WhisperLive\docker\Dockerfile.gpu .

if %ERRORLEVEL% equ 0 (
  echo Docker image 'whisper_live' built successfully.
) else (
  echo Docker image build failed.
)
