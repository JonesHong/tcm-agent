import __init__
import os
import sys
import socketio
import asyncio
import json


from src.utils.config.manager import ConfigManager
from src.utils.log import logger
from src.utils.redis.channel import RedisChannel
from src.utils.redis.core import RedisCore
from src.utils.socket.topic import SocketTopic

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

# # 添加项目根目录到 sys.path
# sys.path.append(project_root)



config = ConfigManager()
redis_core = RedisCore()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

async def async_emit_message(topic, msg):
    await sio.emit(topic, msg)

def emit_message(topic, msg):
    logger.info(f'[Socket] {topic}.emit: {msg}')
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        asyncio.ensure_future(async_emit_message(topic, msg))
    else:
        loop.run_until_complete(async_emit_message(topic, msg))

# 身份驗證中間件
@sio.event
async def connect(sid, environ, auth=None):
    logger.info("Client connect", sid)
    # logger.info("Client connect environ", environ)

    # 從查詢參數中提取 token
    query_string = environ.get('QUERY_STRING', '')
    query_params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
    token = query_params.get('token', None)

    if token == "UNITY":
        await sio.save_session(sid, {"authenticated": True})
        return True  # 允許連接

    await sio.disconnect(sid)
    return False  # 斷開連接

@sio.event
async def disconnect(sid):
    logger.info("Client disconnected", sid)

@sio.on('ttt')
async def ttt(sid, data):
    logger.info('ttt', data)
    await handleASRToggle(sid, False)

# @sio.on("ASR_Toggle")
@sio.on(SocketTopic.asr_toggle)
async def handleASRToggle(sid, data):
    logger.info('handleASRToggle', data)
    # if data: state = 1
    # else: state = 0
    if data: state = 0
    else: state = 1
    
    do_asr_data = {"state":state}
    # do_asr_message = json.dumps(do_asr_data)
    redis_core.publisher(RedisChannel.do_asr_service, do_asr_data)
