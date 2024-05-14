# -*- coding: utf-8 -*-

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

from services.tts_service import VitsService
from util.redis_topic import RedisChannel

# If root is main.py
project_path = os.getcwd()
assets_file_path = {
    "tts_service": os.path.join(project_path, 'services', 'tts_service.py'),
    "asr_service": os.path.join(project_path, 'services', 'asr_service.py')
}

tts_service:VitsService =  None
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

    def subscriber(self, redis_client_sub):
        while self.run_subscriber:
            pubsub = redis_client_sub.pubsub()
            pubsub.subscribe(
                RedisChannel.do_tts_service, 
                RedisChannel.do_asr_service,
                RedisChannel.tts_done_service
            )
            print(f"Listening for messages on '{RedisChannel.do_tts_service}', '{RedisChannel.do_asr_service}', '{RedisChannel.tts_done_service}'.")
            for message in pubsub.listen():
                if not self.run_subscriber:
                    break
                message_type = message['type']
                channel = message['channel'].decode()
                data_print = message['data']
                if isinstance(data_print, bytes):
                    decoded_data = data_print.decode('utf-8')
                    try:
                        data_json = json.loads(decoded_data)
                        data_print = data_json
                    except json.JSONDecodeError:
                        data_print = decoded_data
                print(f"Receive: {{'type': {message_type}, 'channel': {channel}, 'data': {data_print} }}")
                if message['type'] == 'message':
                    if channel == RedisChannel.do_asr_service:
                        self.handle_asr_service(data_print)
                    elif channel == RedisChannel.do_tts_service:
                        self.handle_tts_service(data_print)
            pubsub.close()

    def handle_asr_service(self, data_print):
        state = data_print['state']
        if state == 1:
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

    def shutdown_handler(self, process_name, process, threads):
        print(f'process terminate {process_name}')
        if process:
            if os.name == 'nt':
                process.send_signal(signal.CTRL_C_EVENT)
                print('process.send_signal(signal.CTRL_C_EVENT)')
            else:
                process.send_signal(signal.SIGINT)
                print('process.send_signal(signal.SIGINT)')
            
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        for thread in threads:
            if thread and thread.is_alive():
                thread.join(timeout=5)

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

    def handle_tts_service(self, data_print):
        text = data_print['text']
        if text != '':
            global tts_service
            tts_service.create_wav(text)
        else:
            print('text is empty')

    def signal_handler(self, signum, frame):
        print('Received SIGINT, shutting down...')
        self.run_subscriber = False
        self.shutdown_handler(process_name="asr_process", process=self.asr_process, threads=[self.asr_thread_output, self.asr_thread_error])
        if self.sub_thread.is_alive():
            self.sub_thread.join(timeout=5)
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
    