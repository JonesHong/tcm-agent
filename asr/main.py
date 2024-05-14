import os
import sys

project_path = os.getcwd()
print(project_path)
sys.path.append(f'{project_path}/packages')

import argparse
from typing import Optional
from WhisperLive.whisper_live.client import TranscriptionClient
import time
import threading

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
        # self._last_segment_subscription:Optional[Disposable] = None
        self.segment_stream = self.transcription_client.client.segment_behavior_subject.pipe(
            ops.filter(lambda segment: segment != ''and segment != '字幕by索兰娅'),
            ops.distinct_until_changed()
        )
        # self._segment_subscription:Optional[Disposable] = None
        
        # self.client_thread = threading.Thread(target=self.transcription_client)
        self.start()
        # self._client_thread = None



    def start(self):
        print(f"Starting client: {self._host}:{self._port}")
        
        self._last_segment_subscription = self.last_segment_stream.subscribe(self.last_segment_handler)
        self._segment_subscription = self.segment_stream.subscribe(self.segment_handler)
        self.transcription_client()
        # self.client_thread.start()
        # self.client_thread.join()  # Wait up to 60 seconds
        # time.sleep(60)
        # if self.transcription_client.stream.is_active():
        # if self.client_thread.is_alive():
            # self.stop()

    def stop(self):
        print("Stopping client...")
        self.transcription_client.close_all_clients()
        # self.transcription_client.client.close_websocket()
        self.resettable_timer.stop()  # Ensure timer is stopped
        self.client_thread.join()
        
        if self._last_segment_subscription is not None:
            self._last_segment_subscription.dispose()
        if self._segment_subscription is not None:
            self._segment_subscription.dispose() 
        
            
    
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
        pubsub.subscribe(RedisChannel.do_tts_service, RedisChannel.do_asr_service)
        print(f"Listening for messages on '{RedisChannel.do_tts_service}', '{RedisChannel.do_asr_service}'.")
        for message in pubsub.listen():
            print(message)
            if message['type'] == 'message':
                channel = message['channel'].decode()
                data = message['data'].decode()
                match channel:
                    case RedisChannel.do_asr_service:
                        asr_handler()
                        break
                    case _:
                        return "Unknown command"

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
    
    
def asr_handler():
    asr_service = AsrService(
        host=args.host,
        port=args.port,
        lang=args.lang,
        model= args.model,
        use_vad= args.use_vad,
        translate=args.translate
        )
    # asr_service.start()
    
    # last_segment_stream = asr_service.last_segment_stream
    # last_segment_handler = asr_service.last_segment_handler
    # segment_stream = asr_service.segment_stream
    # segment_handler = asr_service.segment_handler
    
    # asr_service.last_segment_subscription = last_segment_stream.subscribe(last_segment_handler)
    # asr_service.segment_subscription = segment_stream.subscribe(segment_handler)
    
def main():
    try:
        argparse_handler()
        # asr_handler()
        redis_handler()
        
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
    
# asr_service = AsrService(
#   "localhost",
#   9090,
#   lang="zh",
#   translate=False,
#   model="small",
#   use_vad=True,
#     )
# asr_service.transcription_client()

# client = TranscriptionClient(
#   "localhost",
#   9090,
#   lang="zh",
#   translate=False,
#   model="small",
#   use_vad=True,
# )
# print('sajiosajoia')
# client()