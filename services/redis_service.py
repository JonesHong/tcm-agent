# -*- coding: utf-8 -*-
import random
import __init__
import time
import argparse
import math
import os
import subprocess
import sys
import threading
import json
import signal

from util.agent.core import Agent
from util.config.manager import ConfigManager


# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# # 添加项目根目录到 sys.path
# sys.path.append(project_root)
# from services.redis.core import RedisService
from models.schemas.fastapi import aikenshe_result_dict
from util.agent.mode import AgentMode
# from services.agent_service import AgentService
from services.tts_service import VitsService
# from util.agent.rag_chain import SongBieYu
from util.redis.channel import RedisChannel
from util.redis.core import RedisCore

project_path = os.getcwd()
assets_file_path = {
    "tts_service": os.path.join(__init__.ROOT_DIR, 'services', 'tts_service.py'),
    "asr_service": os.path.join(__init__.ROOT_DIR, 'services', 'asr_service.py')
}
# C:\Users\User\Documents\work\tcm-agent\services\asr_service.py
# tts_service: VitsService = None
# agent_service: AgentService = None


class RedisService:
    def __init__(self):
        try:
            config = ConfigManager()
            global tts_service
            tts_service = VitsService(redis_host=config.redis.host, redis_port=config.redis.port)
            # global agent_service
            # agent_service = AgentService()
            
            self.__agent = Agent()
            
            channels = [
                RedisChannel.vip_event, 
                RedisChannel.do_tts_service, 
                RedisChannel.do_asr_service,
                # RedisChannel.tts_done_service,
                RedisChannel.asr_done_service,
                RedisChannel.aikanshe_done_service
            ]
            global redis_core
            redis_core = RedisCore(config=config.redis,channel=channels,message_handler=self.message_handler)

            # self.__agent = agent_service.agent
            
            self.asr_process = None
            self.asr_thread_output = None
            self.asr_thread_error = None
            
            def agent_mode_observer(value):
                try:
                    # 確保將 AgentMode 值轉換為字符串
                    redis_value = value.value if isinstance(value, AgentMode) else value
                    redis_core._redis_client.set(RedisChannel.agent_mode, redis_value)
                except Exception as e:
                    print(f"Error setting agent mode: {e}")
                    
            # 確保將 AgentMode 值轉換為字符串
            redis_value =  self.__agent.mode.value if isinstance(self.__agent.mode, AgentMode) else self.__agent.mode
            redis_core._redis_client.set(RedisChannel.agent_mode, redis_value)
            # print( redis_core.redis_client.get(RedisChannel.agent_mode), redis_value)
            self.__agent.modeSub.subscribe(agent_mode_observer)

        except Exception as e:
            print(f"Error initializing RedisService: {e}")

    def message_handler(self, channel, data_parsed):
        try:
            if channel == RedisChannel.vip_event:
                self.handle_vip_event(data_parsed)
            elif channel == RedisChannel.do_asr_service:
                self.handle_do_asr_service(data_parsed)
            elif channel == RedisChannel.asr_done_service:
                self.handle_asr_done_service(data_parsed)
            elif channel == RedisChannel.do_tts_service:
                self.handle_do_tts_service(data_parsed)
            elif channel == RedisChannel.aikanshe_done_service:
                self.handle_aikanshe_done_service(data_parsed)
        except Exception as e:
            print(f"Error handling message from {channel}: {e}")

    def handle_vip_event(self, data_parsed):
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
            if data_parsed['type'] == 0  and (self.__agent.mode == AgentMode.DIAGNOSTIC or self.__agent.mode == AgentMode.SILENT): 
                """ 打招呼  """
                self.__agent.initial()
                self.__agent.user_info_from_yolo = data_parsed['data']
                age_range = self.__agent.user_info_from_yolo['age']
                min_age, max_age = map(int, age_range.strip('()').split('-'))
                median_age = math.floor((min_age + max_age) / 2)
                gender = self.__agent.user_info_from_yolo['gender']
                male = 0 if gender == 'Female' else 1
                self.__agent.transformed_data = {
                    'age': median_age,
                    'male': male
                }
                self.__agent.sex = data_parsed['data']['gender'].lower()
                response = self.__agent.invoke('開始問診。')
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
                self.__agent.initial()
                # self.__agent.question_count = None
                redis_core.publisher(RedisChannel.do_tts_service, message)
                # redis_core.publisher(RedisChannel.do_asr_service, {"state": 0})
                # emit_message
        except Exception as e:
            print(f"Error handling VIP event: {e}")
    
    def handle_do_asr_service(self, data_parsed):
        try:
            print(data_parsed, self.__agent.question_count,self.__agent.mode,self.asr_process is  None)
            state = data_parsed['state']
            if state == 1 and self.__agent.question_count > 0:
                if self.__agent.mode == AgentMode.DIAGNOSTIC or self.__agent.mode == AgentMode.INQUIRY or self.__agent.mode == AgentMode.CHITCHAT :
                    if self.asr_process is  None:
                        self.asr_process = subprocess.Popen([
                            'python', '-X', 'utf8', '-u', 
                            assets_file_path['asr_service'],
                            '--redis_port', str(redis_core._port)], 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                        
                        self.asr_thread_output = threading.Thread(target=self.read_output, args=(self.asr_process, 'asr_process'))
                        self.asr_thread_output.daemon = True
                        self.asr_thread_output.start()
                        self.asr_thread_error = threading.Thread(target=self.read_error, args=(self.asr_process, 'asr_process'))
                        self.asr_thread_error.daemon = True
                        self.asr_thread_error.start()
                elif self.__agent.mode == AgentMode.TONGUE_DIAGNOSIS:
                    self.__agent.invoke('開始舌診')
                    pass
                
            else:
                self.shutdown_handler(process_name="asr_process", process=self.asr_process, threads=[self.asr_thread_output, self.asr_thread_error])
        except Exception as e:
            print(f"Error handling ASR service: {e}")

    def handle_asr_done_service(self, data_parsed):
        try:
            if self.__agent.question_count != 0 :
                asr_result = data_parsed['text']
                response = self.__agent.invoke(asr_result)
                redis_core.publisher(RedisChannel.do_asr_service, {"state":0})
                
                if response != '' and response is not None:
                    redis_core.publisher(RedisChannel.do_tts_service, {"text": response})
        except Exception as e:
            print(f"Error handling ASR done service: {e}")
            
    def handle_do_tts_service(self, data_parsed):
        try:
            text = data_parsed['text']
            if text != '' and text is not None:
                global tts_service
                tts_service.create_wav(text,speed=1.2)
            else:
                print('text is empty')
        except Exception as e:
            print(f"Error handling TTS service: {e}")
            
    def handle_aikanshe_done_service(self, data_parsed):
        try:
            if self.__agent.mode != AgentMode.EVALUATION_ADVICE:
                self.__agent.mode = AgentMode.EVALUATION_ADVICE
                # self.__agent.invoke(f'開始評估和診斷')
                if data_parsed != '':
                    self.__agent.invoke(f'舌診結果如下：{data_parsed}')
                else:
                    self.__agent.invoke('')
            # pass    
        except Exception as e:
            print(f"Error handling Aikanshe done service: {e}")

    def shutdown_handler(self, process_name, process, threads):
        try:
            if process:
                print(f'process terminate {process_name}')
                if os.name == 'nt':
                    process.send_signal(signal.CTRL_C_EVENT)
                    print('process.send_signal(signal.CTRL_C_EVENT)')
                else:
                    process.send_signal(signal.SIGINT)
                    print('process.send_signal(signal.SIGINT)')
                
                try:
                    process.terminate()
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                for thread in threads:
                    if thread and thread.is_alive():
                        thread.join(timeout=2)
            self.asr_process = None
        except Exception as e:
            print(f"Error shutting down handler: {e}")

    def read_output(self, process, process_name):
        try:
            while True:
                output = process.stdout.readline()
                if output:
                    print(f'[Output] {process_name}: {output.strip()}')
                else:
                    break
        except Exception as e:
            print(f"Error reading output from {process_name}: {e}")

    def read_error(self, process, process_name):
        try:
            while True:
                error = process.stderr.readline()
                if error:
                    print(f'[Error] {process_name}: {error.strip()}')
                else:
                    break
        except Exception as e:
            print(f"Error reading error from {process_name}: {e}")
            
# 在 RedisService 類之外定義一個新的函數來處理信號
def handle_exit(signum, frame):
    print("Received exit signal, shutting down gracefully...")
    sys.exit(0)

# 在 main 函數中設置信號處理
def main():
    try:
        main_service = RedisService()
        signal.signal(signal.SIGINT, handle_exit)
        signal.signal(signal.SIGTERM, handle_exit)
    except Exception as e:
        print(f"Error during execution: {e}")


if __name__ == "__main__":
    main()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program interrupted by user.")