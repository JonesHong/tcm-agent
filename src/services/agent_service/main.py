# -*- coding: utf-8 -*-
import __init__
import math
import random
import signal
import sys
import cmd

from src.schemas._enum import AgentMode
from src.services.agent_service.agent import Agent
from src.services.agent_service.rag_chain import llm
from src.utils.config.manager import ConfigManager
from src.utils.log import logger, uvicorn_init_config
from src.utils.redis.channel import RedisChannel
from src.utils.redis.core import RedisCore

config = ConfigManager()
__init__.logger_start()
# Initialize logger configuration
uvicorn_init_config()

# agent = Agent
# llm = llm
# InteractiveAgent
class AgentService(cmd.Cmd):
    intro = 'Welcome to the interactive Agent. Type help or ? to list commands.\n'
    prompt = 'Question: '
    def __init__(self):
        super().__init__()
        self._stop = False
        if(config.agent.mode == AgentMode.CHITCHAT):
            logger.info(f"AgentMode: {config.agent.mode }，使用通用模型進行回答")
        else:
            logger.info(f"AgentMode: {config.agent.mode }，使用RAGFlow進行回答")

    def default(self, line):
        logger.success(f"(user) {line}")  # 记录用户输入
        if(config.agent.mode== AgentMode.CHITCHAT):
            response = llm.invoke(line)
            logger.info(f"(llm) {response}")
        else:
            response = Agent.invoke(line)
            logger.info(f"(agent) {response}")

    def do_exit(self, line):
        """Exit the interactive Agent."""
        logger.info('Exiting the interactive Agent.')
        self._stop = True
        return True

    def sigint_handler(self, signum, frame):
        try:
            logger.info("Received SIGINT, shutting down...")
            # logger.info("Received SIGINT, shutting down...")
            self._stop = True
            self.onecmd('exit')
        except Exception as e:
            logger.error(f"Exception in signal handler: {e}")
        finally:
            sys.exit(0)
            
    def cmdloop(self, intro=None):
        while not self._stop:
            try:
                super().cmdloop(intro=intro)
                self._stop = True  # Exit loop if cmdloop() completes
            except KeyboardInterrupt:
                self._stop = True

    

agent_service:AgentService = None

channels = [
    RedisChannel.vip_event, 
    RedisChannel.asr_service_done,
    RedisChannel.aikanshe_service_done,
    RedisChannel.do_agent_invoke,
    # RedisChannel.agent_invoke_done
]
def message_handler(channel, data_parsed):
    if channel == RedisChannel.vip_event:
        handle_vip_event(data_parsed)
    elif channel == RedisChannel.asr_service_done:
        handle_asr_servicer_done(data_parsed)
    elif channel == RedisChannel.aikanshe_service_done:
        handle_aikanshe_service_done(data_parsed)
    elif channel == RedisChannel.do_agent_invoke:
        handle_do_agent_invoke(data_parsed)
        
        
    pass
def handle_vip_event(data_parsed):
    """_summary_

    Args:
        face_meta (_type_):  
        {'type': 1, 'text': ['other 再見，祝你有美好的一天～'], 
        'data': {'gender': 'Female', 'age': '(38-43)', 'emotion': 'Happy', 'area': 9.456380208333332, 'name': 'undersecretary', 'face_xyxy': [29, 49, 204, 215]}}
        {'type': 0, 'text': 'other 您好，很高興為您服務！', 
        'data': {'gender': None, 'age': None, 'emotion': None, 'area': None, 'name': None, 'face_xyxy': []}}
    """
    try:
        if data_parsed is None: return
        if data_parsed['type'] == 0  and (Agent.mode == AgentMode.DIAGNOSTIC or Agent.mode == AgentMode.SILENT): 
            """ 打招呼  """
            Agent.initial()
            Agent.user_info_from_yolo = data_parsed['data']
            age_range = Agent.user_info_from_yolo['age']
            min_age, max_age = map(int, age_range.strip('()').split('-'))
            median_age = math.floor((min_age + max_age) / 2)
            gender = Agent.user_info_from_yolo['gender']
            male = 0 if gender == 'Female' else 1
            Agent.transformed_data = {
                'age': median_age,
                'male': male
            }
            Agent.sex = data_parsed['data']['gender'].lower()
            
            response = Agent.invoke('你好')
            message = {"text": response}
            redis_core.publisher(RedisChannel.do_tts_service, message)
        elif data_parsed['type'] == 1:
            """ 再見  """
            # response = SongBieYu({"input": "根據知識庫。參考文件內容說再見，要完整一點的版本"})
            # message = {"text": response['answer']}
            simple_response = "很高興為您服務，祝平安喜樂，再見。"
            detailed_response = "很高興為您服務，中醫提倡“治標治本”，除了使用藥物治療，更重要的是通過調整生活方式來達到長期的健康目標。中醫強調“治未病”的理念，預防勝於治療，通過健康的生活方式來防止疾病的發生。需要注意的是，中藥治療可能會有一些副作用，如果感到非常不適，請立即就醫或尋求專業幫助。\n祝平安喜樂，再見。"
            response_list = [simple_response, detailed_response]

            message = {"text": random.choice(response_list)}
            Agent.initial()
            # self.Agent.question_count = None
            redis_core.publisher(RedisChannel.do_tts_service, message)
            # redis_core.publisher(RedisChannel.do_asr_service, {"state": 0})
            # emit_message
    except Exception as e:
        logger.info(f"Error handling VIP event: {e}")
    pass

def handle_asr_servicer_done(data_parsed):
    try:
        # if Agent.question_count != 0 or True :
            asr_result = data_parsed['text']
            response = Agent.invoke(asr_result)
            redis_core.publisher(RedisChannel.do_asr_service, {"state":0})
            
            if response != '' and response is not None:
                redis_core.publisher(RedisChannel.do_tts_service, {"text": response})
    except Exception as e:
        logger.error(f"Error handling ASR done service: {e}")
        

def handle_aikanshe_service_done(data_parsed):
    try:
        if Agent.mode != AgentMode.EVALUATION_ADVICE:
            Agent.mode = AgentMode.EVALUATION_ADVICE
            # Agent.invoke(f'開始評估和診斷')
            if data_parsed != '':
                Agent.invoke(f'舌診結果如下：{data_parsed}')
            else:
                Agent.invoke('')
        # pass    
    except Exception as e:
        logger.error(f"Error handling Aikanshe done service: {e}")
def handle_do_agent_invoke(data_parsed):
    response = Agent.invoke(data_parsed)
    redis_core.publisher(RedisChannel.agent_invoke_done,response)
    pass

redis_core = RedisCore(channels=channels,message_handler=message_handler)
# 在 main 函數中設置信號處理
def main():
    global agent_service
    agent_service = AgentService()
    signal.signal(signal.SIGINT, agent_service.sigint_handler)
    try:
        agent_service.cmdloop()
    except Exception as e:
        logger.info(f"Error during execution: {e}")
    finally:
        logger.info("Cleanup complete.")
        # Perform any necessary cleanup here



if __name__ == "__main__":
    main()
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     logger.info("Program interrupted by user.")