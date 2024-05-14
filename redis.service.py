# -*- coding: utf-8 -*-
import os
import signal
import subprocess
import argparse
import time
import threading
import json

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

class RedisChannel:
    do_tts_service = "do-tts-service"
    tts_done_service = "tts-done-service"
    do_asr_service = "do-asr-service"
    asr_done_service = "asr-done-service"
    

def redis_handler():
    import redis
    
    def publisher(channel, message):
        redis_client_pub.publish(channel, message)
        print(f"Published: {message}")

    def subscriber(redis_client_sub):
        pubsub = redis_client_sub.pubsub()
        pubsub.subscribe(
            RedisChannel.do_tts_service, 
            RedisChannel.do_asr_service,
            RedisChannel.tts_done_service
        )
        print(f"Listening for messages on '{RedisChannel.do_tts_service}', '{RedisChannel.do_asr_service}', '{RedisChannel.tts_done_service}'.")
        for message in pubsub.listen():
            message_type = message['type']
            pattern = message['pattern']
            channel = message['channel'].decode()
            data_print = message['data']
            if isinstance(data_print, bytes):
                # 對二進制數據解碼
                decoded_data = data_print.decode('utf-8')
                try:
                    # 嘗試解析 JSON
                    data_json = json.loads(decoded_data)
                    data_print = data_json
                    # print(f"Received JSON data: {data_json}")
                except json.JSONDecodeError:
                    # 解析 JSON 失敗，打印解碼後的數據
                    data_print = decoded_data
                    # print(f"Received text data: {decoded_data}")
                    
            print(f"Receive: {{'type': {message_type}, 'pattern': {pattern}, 'channel': {channel}, 'data': {data_print} }}")
            if message['type'] == 'message':
                
                def shutdown_handler(process, threads):
                    print(f'process terminate {process}')
                    if process:
                        process.send_signal(signal.SIGINT)
                        # process.terminate()
                        process.wait()
                    for thread in threads:
                        if thread and thread.is_alive():
                            thread.join()
                        
                def read_output(process, process_name):
                     while True: 
                         # 讀取標準輸出
                        output = process.stdout.readline()
                        if output:
                            print(f'[Output] {process_name}: {output.strip()}')
                        else:
                            break  # 當沒有輸出時結束循環
                def read_error(process, process_name):
                     while True: 
                          # 讀取標準錯誤
                        error = process.stderr.readline()
                        if error:
                            print(f'[Error] {process_name}: {error.strip()}')
                        else:
                            break  # 當沒有輸出時結束循環
                
                if(channel == RedisChannel.do_asr_service):
                            
                    state = data_print['state']
                    asr_process = None
                    asr_thread_output = None
                    asr_thread_error = None
                    if state == 1:
                        # 啟動 subprocess
                        asr_process = subprocess.Popen([
                            'python', '-X', 'utf8', '-u', 
                            './asr/services/asr.service.py',
                            '--redis_port', str(args.port)], 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
                        # 創建並啟動一個線程來讀取輸出
                        asr_thread_output = threading.Thread(target=read_output, args=(asr_process, 'asr_process'))
                        asr_thread_output.start()
                        asr_thread_error = threading.Thread(target=read_error, args=(asr_process, 'asr_process'))
                        asr_thread_error.start()
                    else:
                        shutdown_handler(asr_process, [asr_thread_output, asr_thread_error])
                    # print(asr_process)
                elif(channel == RedisChannel.do_tts_service ):
                    
                    tts_process = None
                    tts_thread_output = None
                    tts_thread_error = None
                    text = data_print['text']
                    if text != '' :
                        # 啟動 subprocess
                        # print("text >>> ", text)
                        tts_process = subprocess.Popen([
                            'python', '-X', 'utf8', '-u', 
                            './tts/services/tts.service.py',
                            '--text', text,'--redis_port', str(args.port)], 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

                        # 創建並啟動一個線程來讀取輸出
                        tts_thread_output = threading.Thread(target=read_output, args=(tts_process, 'tts_process'))
                        tts_thread_output.start()
                        tts_thread_error = threading.Thread(target=read_error, args=(tts_process, 'tts_process'))
                        tts_thread_error.start()
                    else:
                        print(f'tts_process terminate {tts_process}')
                        shutdown_handler(tts_process, [tts_thread_output, tts_thread_error],)
                    # print(tts_process)

    redis_client_pub = redis.Redis(host=args.host, port=args.port)
    redis_client_sub = redis.Redis(host=args.host, port=args.port)
   
    # 订阅者在独立线程中运行
    sub_thread = threading.Thread(target=subscriber, args=(redis_client_sub,))
    sub_thread.start()

    # 发布者稍后运行，以确保订阅者已准备好接收消息
    # time.sleep(1)
    # publisher(RedisChannel.asr_done_service, '3333')
    
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Detected Ctrl+C, shutting down...")
        sub_thread.join()
    
    
def main():
    try:
        argparse_handler()
        redis_handler()
        
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
    