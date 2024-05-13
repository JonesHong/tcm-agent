# -*- coding: utf-8 -*-
import subprocess
import argparse
import time
import threading
import json

def argparse_handler():
            
        parser = argparse.ArgumentParser()
        parser.add_argument('--port', '-p',
                            type=int,
                            default=6379,
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
        pubsub.subscribe(RedisChannel.do_tts_service, RedisChannel.do_asr_service,RedisChannel.tts_done_service)
        print(f"Listening for messages on '{RedisChannel.do_tts_service}', '{RedisChannel.do_asr_service}', '{RedisChannel.tts_done_service}'.")
        for message in pubsub.listen():
            print(f"Receive: {message}")
            if message['type'] == 'message':
                channel = message['channel'].decode()
                data = message['data'].decode()
                
                def shutdown_handler(process, thread):
                    if process:
                        process.terminate()
                        process.wait()
                    if thread and thread.is_alive():
                        thread.join()
                        
                def read_output(process,process_name):
                    while True:
                        output = process.stdout.readline()
                        if output:
                            print(f'{process_name} Output: {output.strip()}')
                        else:
                            break  # 當沒有輸出時結束循環
                
                if(channel == RedisChannel.do_asr_service):
                            
                    state = json.loads(data)['state']
                    asr_process = None
                    asr_thread = None
                    if state == 1:
                        # 啟動 subprocess
                        asr_process = subprocess.Popen(['python', '-X', 'utf8', '-u', './asr/services/asr.service.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

                        # 創建並啟動一個線程來讀取輸出
                        asr_thread = threading.Thread(target=read_output, args=(asr_process, 'asr_process'))
                        asr_thread.start()
                    else:
                        print(f'asr_process terminate {asr_process}')
                        shutdown_handler(asr_process, asr_thread)
                    # print(asr_process)
                elif(channel == RedisChannel.do_tts_service or channel == RedisChannel.tts_done_service ):
                    
                    tts_process = None
                    tts_thread = None
                    if  channel == RedisChannel.do_tts_service:
                        text = json.loads(data)['text']
                        if text != '' :
                            # 啟動 subprocess
                            tts_process = subprocess.Popen(['python', '-X', 'utf8', '-u', './tts/services/tts.service.py','--text', text], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

                            # 創建並啟動一個線程來讀取輸出
                            tts_thread = threading.Thread(target=read_output, args=(tts_process, 'tts_process'))
                            tts_thread.start()
                    else:
                        print(f'tts_process terminate {tts_process}')
                        shutdown_handler(tts_process, tts_thread)
                    # print(tts_process)

    redis_client_pub = redis.Redis(host='localhost', port=6379)
    redis_client_sub = redis.Redis(host='localhost', port=6379)
    
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
    