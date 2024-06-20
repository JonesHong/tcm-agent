# -*- coding: utf-8 -*-

import argparse
import math
import os
import subprocess
import sys
import threading
import json
import signal

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 添加项目根目录到 sys.path
sys.path.append(project_root)
# from services.redis_core import RedisService
from services.agent_service import AgentService
from services.tts_service import VitsService
from util.rag_chain import SongBieYu
from util.redis_channel import RedisChannel
from util.redis_core import RedisCore

project_path = os.getcwd()
assets_file_path = {
    "tts_service": os.path.join(project_path, 'services', 'tts_service.py'),
    "asr_service": os.path.join(project_path, 'services', 'asr_service.py')
}

tts_service: VitsService = None
agent_service: AgentService = None

class RedisService:
    def __init__(self, host='localhost', port=51201):
        global tts_service
        tts_service = VitsService()
        global agent_service
        agent_service = AgentService()
        self.__agent = agent_service.agent
        self.asr_process = None
        self.asr_thread_output = None
        self.asr_thread_error = None
        
        channels = [
            RedisChannel.vip_event, 
            RedisChannel.do_tts_service, 
            RedisChannel.do_asr_service,
            RedisChannel.tts_done_service,
            RedisChannel.asr_done_service
        ]
        global redis_core
        redis_core = RedisCore(host=host, port=port, channels=channels, message_handler=self.handle_message)

    def handle_message(self, channel, data_parsed):
        if channel == RedisChannel.vip_event:
            self.handle_vip_event(data_parsed)
        elif channel == RedisChannel.do_asr_service:
            self.handle_do_asr_service(data_parsed)
        elif channel == RedisChannel.do_tts_service:
            self.handle_do_tts_service(data_parsed)
        elif channel == RedisChannel.asr_done_service:
            self.handle_asr_done_service(data_parsed)

    def handle_vip_event(self, data_parsed):
        if data_parsed is None: return
        if data_parsed['type'] == 0: 
            self.__agent.initial()
            self.__agent.user_info_from_yolo = data_parsed['data']
            age_range = self.__agent.user_info_from_yolo['data']['age']
            min_age, max_age = map(int, age_range.strip('()').split('-'))
            median_age = math.floor((min_age + max_age) / 2)
            gender = self.__agent.user_info_from_yolo['data']['gender']
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
            response = SongBieYu({"input": "根據知識庫。參考文件內容說再見，要完整一點的版本"})
            message = {"text": response['answer']}
            self.__agent.initial()
            self.__agent.question_count = None
            redis_core.publisher(RedisChannel.do_tts_service, message)
            redis_core.publisher(RedisChannel.do_asr_service, {"state": 0})

    def handle_asr_done_service(self, data_parsed):
        if self.__agent.question_count != 0:
            asr_result = data_parsed['text']
            response = self.__agent.invoke(asr_result)
            message = {"text": response}
            redis_core.publisher(RedisChannel.do_tts_service, message)
    
    def handle_do_asr_service(self, data_parsed):
        print(data_parsed)
        state = data_parsed['state']
        if state == 1 and self.__agent.question_count is not None:
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
                process.terminate()
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
            for thread in threads:
                if thread and thread.is_alive():
                    thread.join(timeout=2)
        self.asr_process = None

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

def argparse_handler():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', type=int, default=51201, help="Websocket port to run the server on.")
    parser.add_argument('--host', type=str, default="localhost", help="Websocket host to run the server on.")
    global args
    args = parser.parse_args()

def main():
    try:
        argparse_handler()
        global assets_file_path
        assets_file_path = {
            "tts_service": os.path.abspath(os.path.join(project_path, '..', 'services', 'tts_service.py')),
            "asr_service": os.path.abspath(os.path.join(project_path, '..', 'services', 'asr_service.py'))
        }
        main_service = RedisService(port=args.port,host=args.host)
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()