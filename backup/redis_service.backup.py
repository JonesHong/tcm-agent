# -*- coding: utf-8 -*-

import math
import os
import sys
import signal
import subprocess
import argparse
import time
import threading
import json
import redis
from redis import Redis

from services.agent_service import AgentService
from services.tts_service import VitsService
from util.agent.rag_chain import SongBieYu
from util.redis.channel import RedisChannel

# If root is main.py
project_path = os.getcwd()
assets_file_path = {
    "tts_service": os.path.join(project_path, 'services', 'tts_service.py'),
    "asr_service": os.path.join(project_path, 'services', 'asr_service.py')
}

tts_service:VitsService =  None
agent_service:AgentService =  None
class RedisService:
    def __init__(self, host='localhost', port=6379):
        self.run_subscriber = True
        self.sub_thread = None
        self.asr_process = None
        self.asr_thread_output = None
        self.asr_thread_error = None

        self._host = host
        self._port = port
        self.redis_client_pub = redis.Redis(host=host, port=port)
        self.redis_client_sub = redis.Redis(host=host, port=port)

        signal.signal(signal.SIGINT, self.signal_handler)
        self.sub_thread = threading.Thread(target=self.subscriber, args=(self.redis_client_sub,))
        self.sub_thread.daemon = True  # 设置为守护线程
        self.sub_thread.start()
        global tts_service
        tts_service = VitsService(redis_host=host,redis_port=port)
        global agent_service
        agent_service = AgentService()
        self.__agent = agent_service.agent

    def publisher(self, channel, data):
        message = json.dumps(data)
        self.redis_client_pub.publish(channel, message)
        
    def subscriber(self, redis_client_sub):
        while self.run_subscriber:
            pubsub = redis_client_sub.pubsub()
            channel_need_sub = [
                RedisChannel.vip_event, 
                RedisChannel.do_tts_service, 
                RedisChannel.do_asr_service,
                RedisChannel.tts_done_service,
                RedisChannel.asr_done_service
            ]
            # 訂閱頻道
            pubsub.subscribe(*channel_need_sub)
            # 格式化頻道名稱為字符串
            channel_names = ', '.join(channel_need_sub)
            # 打印訂閱信息
            print(f"Listening for messages on '{channel_names}'.")
            for message in pubsub.listen():
                if not self.run_subscriber:
                    break
                message_type = message['type']
                channel = message['channel'].decode()
                data_parsed = message['data']
                if isinstance(data_parsed, bytes):
                    decoded_data = data_parsed.decode('utf-8')
                    try:
                        data_json = json.loads(decoded_data)
                        data_parsed = data_json
                    except json.JSONDecodeError:
                        data_parsed = decoded_data
                        
                print(f"Receive: {{'type': {message_type}, 'channel': {channel}, 'data': {data_parsed} }}")
                if message['type'] == 'message':
                    if channel == RedisChannel.vip_event:
                        self.handle_vip_event(data_parsed)
                    elif channel == RedisChannel.do_asr_service:
                        self.handle_do_asr_service(data_parsed)
                    elif channel == RedisChannel.do_tts_service:
                        self.handle_do_tts_service(data_parsed)
                    elif channel == RedisChannel.asr_done_service:
                        self.handle_asr_done_service(data_parsed)
            pubsub.close()
    
    def handle_vip_event(self, data_parsed):
        """_summary_
        Args:
            face_meta (_type_):  
            {'type': 1, 'text': ['other 再見，祝你有美好的一天～'], 
            'data': {'gender': 'Female', 'age': '(38-43)', 'emotion': 'Happy', 'area': 9.456380208333332, 'name': 'undersecretary', 'face_xyxy': [29, 49, 204, 215]}}
            {'type': 0, 'text': 'other 您好，很高興為您服務！', 
            'data': {'gender': None, 'age': None, 'emotion': None, 'area': None, 'name': None, 'face_xyxy': []}}
        """
        if data_parsed is None: return
        if data_parsed['type'] == 0 : 
            """ 打招呼 """
            self.__agent.initial()
            self.__agent.user_info_from_yolo = data_parsed['data']
            # 提取年齡範圍並計算中位數
            age_range = self.__agent.user_info_from_yolo['data']['age']
            min_age, max_age = map(int, age_range.strip('()').split('-'))
            median_age = math.floor((min_age + max_age) / 2)

            # 提取性別並轉換
            gender = self.__agent.user_info_from_yolo['data']['gender']
            male = 0 if gender == 'Female' else 1

            # 轉換後的資料
            self.__agent.transformed_data = {
                'age': median_age,
                'male': male
            }

            self.__agent.sex = data_parsed['data']['gender'].lower()
            response = self.__agent.invoke('開始問診。')
            
            message = {"text": response}
            self.publisher(RedisChannel.do_tts_service, message)
        elif data_parsed['type'] == 1 :
            """ 說再見 """
            # prompt = "很高興為您服務，中醫提倡“治標治本”，除了使用藥物治療，更重要的是通過調整生活方式來達到長期的健康目標。這也是中醫強調“治未病”的理念，即預防勝於治療，通過健康的生活方式來防止疾病的發生。需要注意的是，中藥治療可能會有一些副作用，如果感到非常不適，請立即就醫或尋求專業幫助。"
            response = SongBieYu({"input": "根據知識庫。參考文件內容說再見，要完整一點的版本"})
            message = {"text": response['answer']}
            self.__agent.initial()
            self.__agent.question_count = None
            self.publisher(RedisChannel.do_tts_service, message)
            
            self.publisher(RedisChannel.do_asr_service, {"state": 0})
            
    def handle_asr_done_service(self, data_parsed):
        if self.__agent.question_count != 0:
            asr_result = data_parsed['text']
            response = self.__agent.invoke(asr_result)
            message = {"text": response}
            self.publisher(RedisChannel.do_tts_service, message)
        
    
    def handle_do_asr_service(self, data_parsed):
        state = data_parsed['state']
        if state == 1 and self.__agent.question_count != None:
            self.asr_process = subprocess.Popen([
                'python', '-X', 'utf8', '-u', 
                assets_file_path['asr_service'],
                '--redis_port', str(self._port)], 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            
            self.asr_thread_output = threading.Thread(target=self.read_output, args=(self.asr_process, 'asr_process'))
            self.asr_thread_output.daemon = True  # 设置为守护线程
            self.asr_thread_output.start()
            self.asr_thread_error = threading.Thread(target=self.read_error, args=(self.asr_process, 'asr_process'))
            self.asr_thread_error.daemon = True  # 设置为守护线程
            self.asr_thread_error.start()
        else:
            self.shutdown_handler(process_name="asr_process", process=self.asr_process, threads=[self.asr_thread_output, self.asr_thread_error])

    def handle_do_tts_service(self, data_parsed):
        text = data_parsed['text']
        if text != '':
            global tts_service
            tts_service.create_wav(text)
        else:
            print('text is empty')
            
    def shutdown_handler(self, process_name, process, threads):
        if process:
            print(f'process terminate {process_name}')
            if os.name == 'nt':
                process.send_signal(signal.CTRL_C_EVENT)
                print('process.send_signal(signal.CTRL_C_EVENT)')
            else:
                process.send_signal(signal.SIGINT)
                print('process.send_signal(signal.SIGINT)')
            
            try:
                # process.wait(timeout=2)
                pass
            except subprocess.TimeoutExpired:
                process.kill()
            for thread in threads:
                if thread and thread.is_alive():
                    thread.join(timeout=2)

    def read_output(self, process, process_name):
        while True:
            output = process.stdout.readline()
            if output:
                print(f'[Output] {process_name}: {output.strip()}')
            else:
                break
            
    def read_error(self, process, process_name):
        while True: 
            error = process.stderr.readline()
            if error:
                print(f'[Error] {process_name}: {error.strip()}')
            else:
                break


    def signal_handler(self, signum, frame):
        print('Received SIGINT, shutting down...')
        self.run_subscriber = False
        self.shutdown_handler(process_name="asr_process", process=self.asr_process, threads=[self.asr_thread_output, self.asr_thread_error])
        if self.sub_thread.is_alive():
            self.sub_thread.join(timeout=2)
        print('Shutdown complete.')
        sys.exit(0)
    
def argparse_handler():
            
        parser = argparse.ArgumentParser()
        parser.add_argument('--port', '-p',
                            type=int,
                            default=51201,
                            help="Websocket port to run the server on.")
        parser.add_argument('--host',
                            type=str,
                            default="localhost",
                            help="Websocket host to run the server on.")
        
        global args
        args = parser.parse_args()

def main():
    try:
        argparse_handler()
        # If root is redis_service.py
        global assets_file_path
        assets_file_path = {
            "tts_service": os.path.abspath(os.path.join(project_path,'..','services','tts_service.py')),
            "asr_service": os.path.abspath(os.path.join(project_path,'..','services','asr_service.py'))
        }

        redis_service = RedisService(host=args.host,port=args.port)
        
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
    