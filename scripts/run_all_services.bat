cd "c:\work\tcm-agent"
start  "tcm-agent_service" scripts\agent_service.bat
start  "tcm-asr_service" scripts\asr_service.bat
start  "tcm-multi_comm_service" scripts\multi_comm_service.bat
start  "tcm-ollama_keeper_service" scripts\ollama_keeper_service.bat
start  "tcm-tts_service" scripts\tts_service.bat
