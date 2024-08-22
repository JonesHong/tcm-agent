import __init__
import re
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from src.services.multi_comm_service.ragflow_utils import post_completion
from src.schemas._enum import AgentMode,AikensheResultDict
from src.utils.config.manager import ConfigManager
from src.utils.log import logger
from src.utils.redis.core import RedisCore
from src.utils.redis.channel import RedisChannel
from src.utils.socket.topic import SocketTopic
from src.services.multi_comm_service.api import api_router, quanxi_analysis_local_file
from services.multi_comm_service.sio import emit_message, sio

# from util.redis.core import RedisCore

is_photo_taken =False
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 將 Socket.IO 服務器掛載到 FastAPI 應用上
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# FastAPI 路由
app.include_router(api_router)


config = ConfigManager()
channels = [
    RedisChannel.vip_event,
    RedisChannel.tts_service_done,
    RedisChannel.do_aikanshe_service,
    RedisChannel.photo_taken,
    RedisChannel.do_ragflow_invoke,
]
def message_handler(channel, data_parsed):
    if channel == RedisChannel.vip_event:
        handle_vip_event(data_parsed)
    if channel == RedisChannel.tts_service_done:
        handle_tts_service_done(data_parsed)
    elif channel == RedisChannel.do_aikanshe_service:
        handle_do_aikanshe_service(data_parsed)
    elif channel == RedisChannel.photo_taken:
        handle_photo_taken(data_parsed)
    elif channel == RedisChannel.do_ragflow_invoke:
        handle_do_ragflow_invoke(data_parsed)

redis_core = RedisCore(channels=channels,message_handler=message_handler)

# def handle_do_ragflow_invoke(data_parsed): 
#     response = post_completion(data_parsed)
#     print(response)
#     data = {"text":response['data']['answer'].replace(' ','').replace('\n', ' ')}
    
#     redis_core.publisher(RedisChannel.do_tts_service, data)
#     # pass

def handle_do_ragflow_invoke(data_parsed): 
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(post_completion(data_parsed))
        print(4564645,response)
        data = {"text": response['data']['answer'].replace(' ', '').replace('\n', ' ')}
        
        redis_core.publisher(RedisChannel.do_tts_service, data)
    finally:
        print("finally")
        # loop.close()
    # pass
def handle_vip_event(data_parsed): 
    """_summary_
    Args:
        face_meta (_type_):  
        {'type': 1, 'text': ['other 再見，祝你有美好的一天～'], 
        'data': {'gender': 'Female', 'age': '(38-43)', 'emotion': 'Happy', 'area': 9.456380208333332, 'name': 'undersecretary', 'face_xyxy': [29, 49, 204, 215]}}
        {'type': 0, 'text': 'other 您好，很高興為您服務！', 
        'data': {'gender': None, 'age': None, 'emotion': None, 'area': None, 'name': None, 'face_xyxy': []}}
    """
    # sleep(1)
    global redis_core
    agent_mode = redis_core.getter(RedisChannel.agent_mode)
    if data_parsed is None: return
    if data_parsed['type'] == 1  and (agent_mode == AgentMode.DIAGNOSTIC or agent_mode == AgentMode.EVALUATION_ADVICE or agent_mode == AgentMode.SILENT):
        """ 再見  """
        emit_message(SocketTopic.report_toggle, False)
        
    # emit_message(SocketTopic.report_toggle, False)
    
    global is_photo_taken  
    is_photo_taken = False
        
    logger.info(f'is_photo_taken: {is_photo_taken}')
    # pass

def handle_tts_service_done(data_parsed):
    emit_message(SocketTopic.doctor_message, {'audioPath' : data_parsed['audio_path'], "text" : data_parsed['text']})
    # pass

transformed_data = {"age": None, "male": None}

def handle_do_aikanshe_service(data_parsed):
    global transformed_data
    transformed_data = {**data_parsed}
    emit_message(SocketTopic.camera_toggle, True)
    # pass
def handle_photo_taken(data_parsed):
    global is_photo_taken
    logger.info(f'is_photo_taken: {is_photo_taken}')
    if is_photo_taken == False:
        file_path = data_parsed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            asyncio.ensure_future(process_local_file(transformed_data['age'], transformed_data['male'], file_path))
        else:
            loop.run_until_complete(process_local_file(transformed_data['age'], transformed_data['male'], file_path))
        
        emit_message(SocketTopic.camera_toggle, False)
        is_photo_taken = True

async def process_local_file(age, male, file_path):
    # 使用本地檔案進行全息舌像分析
    result = await quanxi_analysis_local_file(
        file_path=file_path,
        age=age,
        male=male
    )
    payload = None
    # 檢查 result 中是否存在 previous_result 以及 analysis_result 鍵
    if 'previous_result' in result and 'analysis_result' in result['previous_result'] and result['previous_result']['analysis_result']['data'] is not None:
        payload = result['previous_result']['analysis_result']['data']
        # pass
    elif 'data' in result and result['data'] is not None:
        payload = result['data']
        # pass
    if payload is not None:
        
        def remove_html_tags(text):
            # 使用正則表達式去除 HTML 標籤
            clean_text = re.sub(r'<.*?>', '', text)
            # 移除多餘的換行符號和空格
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            return clean_text
        # 關注的 key
        keys_of_interest = ["food", "life"]
        # 抽取並轉換 key
        extracted_info = []
        for key in keys_of_interest:
            if key in payload:
                chinese_key = AikensheResultDict.get(key, key)
                extracted_info.append(f"{chinese_key}建議: {remove_html_tags(payload[key])}")
        # 以句號隔開並合併為一個字串
        result_string = "。".join(extracted_info)
        # 發佈消息到 Redis 頻道
        redis_core.publisher(RedisChannel.aikanshe_service_done, result_string)
    else:
        # 發佈消息到 Redis 頻道
        redis_core.publisher(RedisChannel.aikanshe_service_done, '')
    
    emit_message(SocketTopic.report_toggle, True)
    # logger.info(result)
    return result



# transformed_data = {"age": 30, "male": 1}    
# file_path = 'C:\\Users\\User\\Downloads\\S__18104362.jpg'
# loop = asyncio.get_event_loop()
# loop.run_until_complete(process_local_file(transformed_data['age'], transformed_data['male'], file_path))

# async def async_quanxi_analysis_local_file(age,male,file_path): 
#     await  quanxi_analysis_local_file( age=age, male=male, file_path=file_path,appkey= "v1eaevl3dum3i9g46ar5c8cghd8cle7t")
# loop = asyncio.get_event_loop()
# loop.run_until_complete(async_quanxi_analysis_local_file(transformed_data['age'], transformed_data['male'], file_path))