# -*- coding: utf-8 -*-

import os
import signal
import sys

# 获取当前脚本的绝对路径
current_script_path = os.path.abspath(__file__)
# 获取当前脚本的目录路径
current_directory = os.path.dirname(current_script_path)
# 回退到 asr 目录（当前目录的父目录的父目录）
asr_directory = os.path.dirname(current_directory)
# 构建目标目录路径
packages_path = os.path.join(asr_directory, 'packages')
# 添加到 sys.path
sys.path.append(packages_path)

# 打印添加的路径以确认
print("Added to sys.path:", packages_path)
import argparse
from typing import Optional
from WhisperLive.whisper_live.client import TranscriptionClient
import time
import threading
import redis
import json

from rx import operators as ops
from rx.core.typing import Disposable
from opencc import OpenCC

cc = OpenCC('t2s')  # Traditional Chinese to Simplified Chinese

stop_event = threading.Event()
history_segments = []

class ResettableTimer:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.timer = None
        self.lock = threading.Lock()

    def reset(self):
        with self.lock:
            if self.timer is not None:
                self.timer.cancel()
            self.timer = threading.Timer(self.interval, self.action)
            self.timer.start()

    def stop(self):
        with self.lock:
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None

class AsrService:
    def __init__(self, host, port, lang, model, use_vad,translate):
        self._host = host
        self._port = port
        self.transcription_client = TranscriptionClient(
            host,
            port=port,
            lang=lang,
            model=model,
            use_vad=use_vad,
            translate=translate
        )
        
        self.resettable_timer_seconds = 3
        self.resettable_timer = ResettableTimer(self.resettable_timer_seconds, self.timeout_event)  # Set 3-second timeout
        
        self.last_segment_stream = self.transcription_client.client.last_segment_behavior_subject.pipe(
            ops.filter(lambda last_segment: last_segment['text'] != '' and last_segment['text'] != '字幕by索兰娅'),
            ops.distinct_until_changed()
        )
        self.segment_stream = self.transcription_client.client.segment_behavior_subject.pipe(
            ops.filter(lambda segment: segment != '' and segment != '字幕by索兰娅'),
            ops.distinct_until_changed()
        )
        
        # self.client_thread = threading.Thread(target=self.transcription_client)
        self.start()



    def start(self):
        print(f"Starting client: {self._host}:{self._port}")
        
        self._last_segment_subscription = self.last_segment_stream.subscribe(self.last_segment_handler)
        self._segment_subscription = self.segment_stream.subscribe(self.segment_handler)
        self.transcription_client()
        # self.client_thread.start()

    def stop(self):
        print("Stopping client...")
        # self.transcription_client.client.close_websocket()
        self.resettable_timer.stop()  # Ensure timer is stopped
        # self.client_thread.join()
        
        if self._last_segment_subscription is not None:
            self._last_segment_subscription.dispose()
        if self._segment_subscription is not None:
            self._segment_subscription.dispose() 
        
        print(redis_client.ping())
        if redis_client :
            asr_done_data = {"text": self.format_sentence(self.transcription_client.client.segment_behavior_subject.value)}
            asr_done_message = json.dumps(asr_done_data)
            redis_client.publish(RedisChannel.asr_done_service, asr_done_message)
            print(f"Redis publish {RedisChannel.asr_done_service}: {asr_done_data}")
            
            time.sleep(3)
            do_asr_message = json.dumps({"state": 0})
            redis_client.publish(RedisChannel.do_asr_service, do_asr_message)
            print(f"Redis publish {RedisChannel.do_asr_service}: {do_asr_message}")
            
        else:
            print("Redis client is not connected.") 
        
        # time.sleep(3)
        # self.transcription_client.close_all_clients()
        
            
    
    def timeout_event(self):
        """
        Define the event to execute on timeout
        定義超時時執行的事件
        """
        print("= = = = END = = =\n\n")
        print(f"Timeout event triggered after {self.resettable_timer_seconds} seconds with no events!")
        print(f'format_sentence(segment_behavior_subject.value): {self.format_sentence(self.transcription_client.client.segment_behavior_subject.value)}')
        print(f'optimize_segments(history_segments): {self.optimize_segments(history_segments)}')
        
        self.stop()
        
    def last_segment_handler(self,last_segment):
        simplified_text = cc.convert(last_segment['text'])
        last_segment['text'] = simplified_text
        print(f"[Received] last_segment_subject : {last_segment['text']}")
        history_segments.append(last_segment)

    def segment_handler(self,segment):
        # simplified_text = cc.convert(segment)
        print(f"[Received] segment_subject : {segment}")
        self.resettable_timer.reset()  # Reset the timer on event reception
        # 接收到事件時重設計時器
        
    def optimize_segments(self,history_segments):
        """
        Optimize the list of segments by keeping only the segment with the maximum 'end' value for each 'start' time.
        優化片段列表，為每個起始時間只保留最大結束值的片段。

        :param history_segments: List of dictionaries, each containing 'start', 'end', and 'text' keys.
        :return: A list of optimized segments.
        """
        max_segments = {}

        for segment in history_segments:
            start = segment['start']
            end = float(segment['end'])
            text = segment['text']

            if start in max_segments:
                # Compare and keep the entry with the maximum 'end'
                # 比較並保留擁有最大結束時間的條目
                if end > float(max_segments[start]['end']):
                    max_segments[start] = {'end': str(end), 'text': text}
            else:
                # Add new entry
                # 添加新條目
                max_segments[start] = {'end': str(end), 'text': text}

        # Convert the dictionary back to a list for the output
        # 將字典轉換回列表以輸出
        optimized_segments = [{'start': start, 'end': info['end'], 'text': info['text']} for start, info in max_segments.items()]
        return optimized_segments

    def format_sentence(self,input_string):
        """

        Args:
            input_string (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Replace spaces and commas with Chinese commas
        # 將空格和逗號替換為中文逗號
        formatted_string = input_string.replace(" ", "，").replace(",", "，")
        
        # Check if the sentence ends with a period, add one if not
        # 檢查句子是否以句號結尾，如果沒有則添加
        if not formatted_string.endswith("。"):
            formatted_string += "。"
        
        return formatted_string


def argparse_handler():
        def str_to_bool(v):
            if isinstance(v, bool):
                return v
            if v.lower() in ('yes', 'y'):
                return True
            elif v.lower() in ('no', 'n'):
                return False
            else:
                raise argparse.ArgumentTypeError('Boolean value expected.')
            
        parser = argparse.ArgumentParser()
        parser.add_argument('--port', '-p',
                            type=int,
                            default=9090,
                            help="Websocket port to run the server on.")
        parser.add_argument('--host',
                            type=str,
                            default="localhost",
                            help="Websocket host to run the server on.")
        parser.add_argument('--redis_port', '-rp',
                            type=int,
                            default=6379,
                            help="Websocket port to run the server on.")
        parser.add_argument('--redis_host','-rh',
                            type=str,
                            default="localhost",
                            help="Websocket host to run the server on.")
        parser.add_argument('--lang', '-l',
                            type=str,
                            default="zh",
                            help="Language for asr.")
        parser.add_argument('--model', '-m',
                            type=str,
                            default="small",
                            help="Model for Whisper")
        parser.add_argument('--use_vad',
                            type=str_to_bool,
                            nargs='?',
                            const=True,  # If --use_vad is used without value, it defaults to True
                            default=True,
                            help="Enable or disable VAD (Voice Activity Detection). Use y/n or yes/no.")
        parser.add_argument('--translate',
                            type=str_to_bool,
                            nargs='?',
                            const=True,  # If --use_vad is used without value, it defaults to False
                            default=False,
                            help="Enable or disable translate. Use y/n or yes/no.")
        
        global args
        args = parser.parse_args()

redis_client = None
class RedisChannel:
    do_tts_service = "do-tts-service"
    tts_done_service = "tts-done-service"
    do_asr_service = "do-asr-service"
    asr_done_service = "asr-done-service"
def main():
    try:
        
        def signal_handler(signum, frame):
            print(f"Received signal: {signum}")
            # 清理工作
            print("Performing cleanup...")
            # 拋出 KeyboardInterrupt 異常，以便它可以在 main 函數中被捕捉
            raise KeyboardInterrupt()

        # 註冊信號處理器
        signal.signal(signal.SIGINT, signal_handler)
        
        argparse_handler()
        
        # redis_client = redis.Redis(host=args.redis_host, port=args.redis_port)
        global redis_client
        redis_client = redis.Redis(host=args.redis_host, port=args.redis_port)
        ping = redis_client.ping()
        print(ping)
        
        # 務必讓它在最後一行，會阻塞進程
        asr_service = AsrService(
            host=args.host,
            port=args.port,
            lang=args.lang,
            model= args.model,
            use_vad= args.use_vad,
            translate=args.translate
            )
        
    except Exception as e:
        print(f"Error during execution: {e}")
        
    except KeyboardInterrupt:
        # 這裡現在可以捕捉到 KeyboardInterrupt
        print("KeyboardInterrupt caught in main, performing cleanup...")
        # 執行清理工作
        sys.exit(0)  # 確保正確退出

if __name__ == "__main__":
    main()
    