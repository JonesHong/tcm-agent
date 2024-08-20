
import __init__
from fastapi import FastAPI, WebSocket
import uvicorn
# from src.services.WhisperLive.whisper_live import WhisperLive, asr_client_config

from src.services.asr_service.whisper_live import WhisperLive
from src.schemas._enum import AgentMode
from src.utils.redis.channel import RedisChannel
from src.utils.redis.core import RedisCore
from src.utils.config.manager import ConfigManager
__init__.logger_start()
from src.utils.log import uvicorn_init_config, logger

config = ConfigManager()
system_config = config.system
asr_client_config = config.asr_client
# agent = Agent()
channels = [
    RedisChannel.do_asr_service
]
def message_handler(channel, data_parsed):
    if channel == RedisChannel.do_asr_service:
        handle_do_asr_service(data_parsed)

def handle_do_asr_service(data_parsed):    
    try:
        state = data_parsed['state']
        # agent_question_count = int(redis_core.getter(RedisChannel.agent_question_count))
        # if state == 1  and agent_question_count > 0:
        if state == 1:
            agent_mode = redis_core.getter(RedisChannel.agent_mode)
            if agent_mode == AgentMode.DIAGNOSTIC.value or agent_mode == AgentMode.INQUIRY.value or agent_mode == AgentMode.CHITCHAT.value :
                WhisperLive.connect()
            elif agent_mode == AgentMode.TONGUE_DIAGNOSIS.value:
                redis_core.publisher(RedisChannel.do_agent_invoke,'開始舌診')
                # agent.invoke('開始舌診')
        else:
            WhisperLive.disconnect()
    except Exception as e:
        logger.error(f"Error handling ASR service: {e}")
        
redis_core = RedisCore(channels=channels, message_handler=message_handler)

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
        except:
            break

@app.get("/disconnect")
def disconnect_route():
    return WhisperLive.disconnect()

@app.get("/connect")
def connect_route():
    return WhisperLive.connect()


def main():
    # 在主線程中運行 FastAPI 應用程序
    uv_config = uvicorn.Config(app, host=asr_client_config.host, port=asr_client_config.uv_port)
    server = uvicorn.Server(uv_config)

    # # 将uvicorn输出的全部让loguru管理
    uvicorn_init_config()

    server.run()
if __name__ == "__main__":
    WhisperLive.argparse_handler()

    try:
        WhisperLive.run(app)
        main()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Shutting down...")
        if WhisperLive.transcription_client:
            WhisperLive.transcription_client.close_all_clients()
