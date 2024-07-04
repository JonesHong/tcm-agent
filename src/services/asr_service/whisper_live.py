import __init__
import argparse

import threading
from opencc import OpenCC
from src.packages.WhisperLive.whisper_live.client import TranscriptionClient
from reactivex import Observable, operators as ops
from src.utils.config.manager import ConfigManager
from src.utils.redis.channel import RedisChannel
from src.utils.redis.core import RedisCore
from src.services.asr_service.timer import ResettableTimer
from src.utils.log import logger
from src.utils.decorators.singleton import singleton

config = ConfigManager()
system_config = config.system
asr_client_config = config.asr_client


cc = OpenCC(system_config.opencc_convert)
redis_core = RedisCore()

@singleton
class WhisperLiveClass:
    def __init__(self):
        self.args = None
        # self.cc = OpenCC(system_config.opencc_convert)
        self.transcription_client: TranscriptionClient = None
        self.last_segment_subscription = None
        self.segment_subscription = None
        self.history_segments = []
        self.resettable_timer = ResettableTimer(asr_client_config.resettable_timer_seconds, self.timeout_event)

    def timeout_event(self):
        logger.info("= = = = END = = =\nTimeout event triggered after {asr_client_config.resettable_timer_seconds} seconds with no sound events!\n")
        
        optimize_segments_history_segments = self.optimize_segments(self.history_segments)
        format_sentence_segment_value = self.format_sentence(self.transcription_client.client.segment_behavior_subject.value)
        logger.info(f'optimize_segments(history_segments): {optimize_segments_history_segments}')
        logger.info(f'format_sentence(segment_behavior_subject.value): {format_sentence_segment_value}')

        asr_done_data = {"text": format_sentence_segment_value}
        redis_core.publisher(RedisChannel.asr_service_done, asr_done_data)
        self.disconnect()

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

    def start_transcription_client(self):
        # 使用多執行緒啟動 TranscriptionClient
        transcription_thread = threading.Thread(target=self.transcription_client)
        transcription_thread.start()

    def connect(self):
        if self.transcription_client and self.transcription_client.client:
            logger.info("= = = = START = = =\nConnect trigger!")
            self.transcription_client.client.connect_websocket()
            self.start_transcription_client()
            return {"status": "connected"}
        return {"error": "No transcription client available"}
    
    def disconnect(self):
        if self.transcription_client and self.transcription_client.client:
            logger.info("Disconnect trigger!")
            self.resettable_timer.stop()
            self.history_segments = []  # 清空 history_segments
            self.transcription_client.close_all_clients()
            return {"status": "disconnected"}
        return {"error": "No transcription client available"}
    
    def last_segment_handler(self, last_segment):
        simplified_text = cc.convert(last_segment['text'])
        last_segment['text'] = simplified_text
        if system_config.mode == "test":
            logger.info(f"last_segment_subject: {last_segment['text']}")
        self.history_segments.append(last_segment)

    def segment_handler(self, segment):
        logger.info(f"segment_subject: {segment}")
        self.resettable_timer.reset()

    def argparse_handler(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--host', '-H',
                            type=str,
                            default=asr_client_config.host,
                            help='Host for the server')
        parser.add_argument('--port', '-p',
                            type=int,
                            default=asr_client_config.port,
                            help='Websocket port to run the server on.')
        parser.add_argument('--lang', '-l',
                            type=str,
                            default=asr_client_config.lang,
                            help='The primary language for transcription. Default is None, which defaults to English ("en").')
        parser.add_argument('--translate', '-t',
                            action='store_true',
                            default=asr_client_config.translate,
                            help='Indicates whether translation tasks are required (default is False).')
        parser.add_argument('--model', '-m',
                            type=str,
                            default=asr_client_config.model,
                            help='')
        parser.add_argument('--use_vad', '-uv',
                            action='store_true',
                            default=asr_client_config.use_vad,
                            help='(default is False).')
        parser.add_argument('--save-output-recording', '-s',
                            action='store_true',
                            default=asr_client_config.save_output_recording,
                            help='Indicates whether to save recording from microphone (default is False).')
        parser.add_argument('--output-recording-filename', '-f',
                            type=str,
                            default=asr_client_config.output_recording_filename,
                            help='File to save the output recording.')
        parser.add_argument('--output-transcription-path', '-o',
                            type=str,
                            default=asr_client_config.output_transcription_path,
                            help='File to save the output transcription.')
        self.args = parser.parse_args()

    def run(self,app):
        # 初始化 TranscriptionClient
        self.transcription_client = TranscriptionClient(
            host=self.args.host,
            port=self.args.port,
            lang=self.args.lang,
            translate=self.args.translate,
            model=self.args.model,
            use_vad=self.args.use_vad
        )

        # 订阅流
        self.last_segment_subscription = self.transcription_client.client.last_segment_behavior_subject.pipe(
            ops.filter(lambda last_segment: last_segment['text'] != '' and last_segment['text'] != '字幕by索兰娅'),
            ops.distinct_until_changed()
        ).subscribe(self.last_segment_handler)

        self.segment_subscription = self.transcription_client.client.segment_behavior_subject.pipe(
            ops.filter(lambda segment: segment != '' and segment != '字幕by索兰娅'),
            ops.distinct_until_changed()
        ).subscribe(self.segment_handler)

WhisperLive = WhisperLiveClass()