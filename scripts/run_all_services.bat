cd "c:\Users\User\Documents\work\tcm-agent"
start /min "agent_service" scripts\agent_service.bat
start /min "asr_service" scripts\asr_service.bat
start /min "multi_comm_service" scripts\multi_comm_service.bat
start /min "ollama_keeper_service" scripts\ollama_keeper_service.bat
start /min "tts_service" scripts\tts_service.bat
