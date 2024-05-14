# -*- coding: utf-8 -*-

import os
import sys


project_path = os.getcwd()
print("asr_service",project_path)
print(f'asr_service.py {__file__}')
# 获取项目根目录
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 添加项目根目录到 sys.path
sys.path.append(project_root)
import signal
import sys

import argparse

import redis
from packages.WhisperLive.whisper_live.client import TranscriptionClient
import time
import threading
import json

from util.redis_topic import RedisChannel
from reactivex import operators as ops
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
    def __init__(self, 
                host = "localhost",
                port = 9090, 
                lang = "zh", 
                model = "small", 
                use_vad = True,
                translate = False):
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
        
        self.start()

    def start(self):
        print(f"Starting client: {self._host}:{self._port}")
        self._last_segment_subscription = self.last_segment_stream.subscribe(self.last_segment_handler)
        self._segment_subscription = self.segment_stream.subscribe(self.segment_handler)
        self.transcription_client()

    def stop(self):
        print("Stopping client...")
        self.resettable_timer.stop()
        
        if self._last_segment_subscription is not None:
            self._last_segment_subscription.dispose()
        if self._segment_subscription is not None:
            self._segment_subscription.dispose() 
        
        if redis_client:
            asr_done_data = {"text": self.format_sentence(self.transcription_client.client.segment_behavior_subject.value)}
            asr_done_message = json.dumps(asr_done_data)
            print(f"Redis publish {RedisChannel.asr_done_service}: {asr_done_data}")
            redis_client.publish(RedisChannel.asr_done_service, asr_done_message)
            
            do_asr_message = json.dumps({"state": 0})
            print(f"Redis publish {RedisChannel.do_asr_service}: {do_asr_message}")
            redis_client.publish(RedisChannel.do_asr_service, do_asr_message)
        else:
            print("Redis client is not connected.") 
        
        time.sleep(1)
        self.transcription_client.close_all_clients()

    def timeout_event(self):
        print("\n= = = = END = = =\n")
        print(f"Timeout event triggered after {self.resettable_timer_seconds} seconds with no events!")
        print(f'optimize_segments(history_segments): {self.optimize_segments(history_segments)}')
        print(f'format_sentence(segment_behavior_subject.value): {self.format_sentence(self.transcription_client.client.segment_behavior_subject.value)}')
        self.stop()
        
    def last_segment_handler(self, last_segment):
        simplified_text = cc.convert(last_segment['text'])
        last_segment['text'] = simplified_text
        print(f"[Received] last_segment_subject : {last_segment['text']}")
        history_segments.append(last_segment)

    def segment_handler(self, segment):
        print(f"[Received] segment_subject : {segment}")
        self.resettable_timer.reset()

    def optimize_segments(self, history_segments):
        max_segments = {}
        for segment in history_segments:
            start = segment['start']
            end = float(segment['end'])
            text = segment['text']
            if start in max_segments:
                if end > float(max_segments[start]['end']):
                    max_segments[start] = {'end': str(end), 'text': text}
            else:
                max_segments[start] = {'end': str(end), 'text': text}
        optimized_segments = [{'start': start, 'end': info['end'], 'text': info['text']} for start, info in max_segments.items()]
        return optimized_segments

    def format_sentence(self, input_string):
        formatted_string = input_string.replace(" ", "，").replace(",", "，")
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
    parser.add_argument('--port', '-p', type=int, default=9090, help="Websocket port to run the server on.")
    parser.add_argument('--host', type=str, default="localhost", help="Websocket host to run the server on.")
    parser.add_argument('--redis_port', '-rp', type=int, default=51201, help="Websocket port to run the server on.")
    parser.add_argument('--redis_host','-rh', type=str, default="localhost", help="Websocket host to run the server on.")
    parser.add_argument('--lang', '-l', type=str, default="zh", help="Language for asr.")
    parser.add_argument('--model', '-m', type=str, default="small", help="Model for Whisper")
    parser.add_argument('--use_vad', type=str_to_bool, nargs='?', const=True, default=True, help="Enable or disable VAD (Voice Activity Detection). Use y/n or yes/no.")
    parser.add_argument('--translate', type=str_to_bool, nargs='?', const=True, default=False, help="Enable or disable translate. Use y/n or yes/no.")
    global args
    args = parser.parse_args()

redis_client = None

def main():
    def signal_handler(signum, frame):
        print(f"Received signal: {signum}")
        print("Performing cleanup...")
        raise KeyboardInterrupt()

    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        argparse_handler()
        global redis_client
        redis_client = redis.Redis(host=args.redis_host, port=args.redis_port)
        ping = redis_client.ping()
        print(ping)
        
        asr_service = AsrService(
            host=args.host,
            port=args.port,
            lang=args.lang,
            model=args.model,
            use_vad=args.use_vad,
            translate=args.translate
        )

    except KeyboardInterrupt:
        print("KeyboardInterrupt caught in main, performing cleanup...")
        if 'asr_service' in locals():
            asr_service.stop()
        sys.exit(0)
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
    