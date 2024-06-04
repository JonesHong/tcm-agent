# -*- coding: utf-8 -*-
import os
import sys

# from services import redis_service


project_path = os.getcwd()
print("tts_service",project_path)
print(f'tts_service.py {__file__}')

# 获取项目根目录
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 添加项目根目录到 sys.path
sys.path.append(project_root)
import time

import argparse
from packages.vits.text import text_to_sequence
import packages.vits.commons as commons
import packages.vits.utils as utils
from packages.vits.models import SynthesizerTrn
from torch import no_grad, LongTensor
import torch

import wave
import numpy as np
from datetime import datetime

import redis
import json
from opencc import OpenCC
from util.redis_topic import RedisChannel

cc = OpenCC('t2s')  # Traditional Chinese to Simplified Chinese

# If root is main.py
assets_file_path = {
    "hparams_file_path": os.path.join(project_path,'models','YunzeNeural','config.json'),
    "checkpoint_path": os.path.join(project_path,'models','YunzeNeural','G_latest.pth'),
}

class VitsService:
    def __init__(self, 
                 redis_host = 'localhost',
                 redis_port = 6379,
                 hparams_file_path = assets_file_path['hparams_file_path'],
                 checkpoint_path = assets_file_path['checkpoint_path']):
        self._redis_host = redis_host
        self._redis_port = redis_port
        self._hparams_file_path = hparams_file_path
        self._checkpoint_path = checkpoint_path
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
                
        # print(torch.version.cuda)   
        # print('torch.cuda.is_available',torch.cuda.is_available() )
        self.language_marks = {
            "Japanese": "",
            "日本語": "[JA]",
            "中文": "[ZH]",
            "English": "[EN]",
            "Mix": "",
            }
        self.lang = ['日本語', '中文', 'English', 'Mix']
                
        self.tts_fn = self.create_tts_fn()
        self.hps = utils.get_hparams_from_file(self._hparams_file_path)
        self.set_model()

    def set_model(self):
        self.net_g = SynthesizerTrn(
            len(self.hps.symbols),
            self.hps.data.filter_length // 2 + 1,
            self.hps.train.segment_size // self.hps.data.hop_length,
            n_speakers=self.hps.data.n_speakers,
            **self.hps.model).to(self.device)
        _ = self.net_g.eval()

        _ = utils.load_checkpoint(self._checkpoint_path, self.net_g, None)

        self.speaker_ids = self.hps.speakers

    def get_text(self,text, hps, is_symbol):
        text_norm = text_to_sequence(text, hps.symbols, [] if is_symbol else hps.data.text_cleaners)
        if hps.data.add_blank:
            text_norm = commons.intersperse(text_norm, 0)
        text_norm = LongTensor(text_norm)
        return text_norm

    def create_tts_fn(self):
        def tts_fn(text, speaker, language, speed):
            if language is not None:
                text = self.language_marks[language] + text + self.language_marks[language]
            speaker_id = self.speaker_ids[speaker]
            stn_tst = self.get_text(text, self.hps, False)
            with no_grad():
                x_tst = stn_tst.unsqueeze(0).to(self.device)
                x_tst_lengths = LongTensor([stn_tst.size(0)]).to(self.device)
                sid = LongTensor([speaker_id]).to(self.device)
                audio = self.net_g.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=.667, noise_scale_w=0.6,
                                    length_scale=1.0 / speed)[0][0, 0].data.cpu().float().numpy()
            del stn_tst, x_tst, x_tst_lengths, sid
            return "Success", (self.hps.data.sampling_rate, audio)

        return tts_fn

    def process_text_and_generate_voice_array(slef,tts_fn, speaker, text, language, speed):
        """處理文本並生成聲音數據列表"""
        text = text.replace('\\n', '').strip().replace('\n', '')
        symbol_remov = ["，", "、", "。", "：", "）", "（", "？", ":", ")", "(", "「", "」", "！"]
        non_symbol_text = text
        for symbol in symbol_remov:
            non_symbol_text = non_symbol_text.replace(symbol, "@")

        current_index = 0
        max_len = 30
        numpy_voice_array = []
        if max_len >= len(text):
            _, output = tts_fn(text=text, speaker=speaker, language=language, speed=float(speed))
            numpy_voice_array = output[1].tolist()
        else:
            while True:
                temp_text = non_symbol_text[current_index:current_index + max_len]
                split_index = [pos for pos, char in enumerate(temp_text) if char == '@']
                target_index = current_index + max_len + 1 if len(split_index) == 0 else split_index[-1] + current_index + 1
                used_text = text[current_index:target_index]
                _, output = tts_fn(text=used_text, speaker=speaker, language=language, speed=float(speed))
                voice_list = output[1].tolist()
                if len(voice_list) < 20000:
                    numpy_voice_array += voice_list
                else:
                    numpy_voice_array += output[1].tolist()[300:-8500]
                current_index = target_index
                if current_index >= len(text) - 1:
                    break

        return numpy_voice_array, output[0]

    def create_wav(self, text, filename = None, speaker = "YunzeNeural", language = "中文", speed=0.6):
        """根據文本創建wav檔案"""
        numpy_voice_array, sr = self.process_text_and_generate_voice_array(self.tts_fn, speaker, text, language, speed)
        numpy_voice_array2 = np.int16(np.array(numpy_voice_array) * 32767)
       
        # 構建完整的文件路徑
        file_str = filename if filename else datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')
        full_path = os.path.join(project_root,'audio', f"{file_str}.wav")

        # 確保目錄存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # 寫入 WAV 文件
        with wave.open(full_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(numpy_voice_array2.tobytes())
        global redis_client
        if redis_client is None:   
            redis_client = redis.Redis(host=self._redis_host, port=self._redis_port)
        
        if redis_client: 
            simplified_text = cc.convert(text)
            data = {"audio_path": os.path.normpath(full_path),"text": simplified_text}
            tts_done_message = json.dumps(data)
            redis_client.publish(RedisChannel.tts_done_service, tts_done_message)
            print(f"Redis publish {RedisChannel.tts_done_service}: {data}")
            
            time.sleep(1)
            do_tts_message = json.dumps({"text": ""})
            redis_client.publish(RedisChannel.do_tts_service, do_tts_message)
            print(f"Redis publish {RedisChannel.do_tts_service}: {do_tts_message}")
        else:
            print("Redis client is not connected.")
        # 返回完整的文件路徑
        return full_path

    def create_voice_array(self, text, speaker = "YunzeNeural", language = "中文", speed=0.6):
        """根據文本生成聲音數據列表"""
        numpy_voice_array, _ = self.process_text_and_generate_voice_array(self.tts_fn, speaker, text, language, speed)
        return numpy_voice_array
    


def argparse_handler():
    parser = argparse.ArgumentParser()
    parser.add_argument('--redis_port', '-rp',
                        type=int,
                        default=6379,
                        help="Websocket port to run the server on.")
    parser.add_argument('--redis_host','-rh',
                        type=str,
                        default="localhost",
                        help="Websocket host to run the server on.")
    parser.add_argument('--speaker',
                        type=str,
                        default="YunzeNeural",
                        help="TTS  model")
    parser.add_argument('--language', '-l',
                        type=str,
                        default="中文",
                        help="Language for asr.")
    parser.add_argument('--speed',
                        type=int,
                        default=0.6,
                        help="")
    parser.add_argument('--text', '-t',
                        type=str,
                        required=True,
                        help="The text you want to crate audio file")
    
    global args
    args = parser.parse_args()
        
redis_client:redis.Redis =None
# class RedisChannel:
#     do_tts_service = "do-tts-service"
#     tts_done_service = "tts-done-service"
#     do_asr_service = "do-asr-service"
#     asr_done_service = "asr-done-service"
    
def main():
    try:
        argparse_handler()
        # print('main')
        global redis_client
        redis_client = redis.Redis(host=args.redis_host, port=args.redis_port)
        # ping = redis_client.ping()
        
        # global assets_file_path
        # assets_file_path = {
        #     "hparams_file_path": os.path.abspath(os.path.join(project_path,'..','models','YunzeNeural','config.json')),
        #     "checkpoint_path": os.path.abspath(os.path.join(project_path,'..','models','YunzeNeural','G_latest.pth')),
        # }
        tts = VitsService()
        
        tts.create_wav(
            text = args.text,
            speaker = args.speaker,
            language = args.language,
            speed = args.speed
        )
        
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()