# -*- coding: utf-8 -*-

import os
import sys
import time

# 获取当前脚本的绝对路径
current_script_path = os.path.abspath(__file__)
# 获取当前脚本的目录路径
current_directory = os.path.dirname(current_script_path)
# 回退到 tts 目录（当前目录的父目录的父目录）
tts_directory = os.path.dirname(current_directory)
# 构建目标目录路径
packages_path = os.path.join(tts_directory, 'packages')
# 添加到 sys.path
sys.path.append(packages_path)
# 打印添加的路径以确认
print("Added to sys.path:", packages_path)

import argparse
from vits.text import text_to_sequence
import vits.commons as commons
import vits.utils as utils
from vits.models import SynthesizerTrn
from torch import no_grad, LongTensor
import torch

import wave
import numpy as np
from datetime import datetime

import redis
import json
from opencc import OpenCC

cc = OpenCC('t2s')  # Traditional Chinese to Simplified Chinese

class VitsService:
    def __init__(self, hparams_file_path = f"{tts_directory}/models/YunzeNeural/config.json",checkpoint_path=f"{tts_directory}/models/YunzeNeural/G_latest.pth"):
        self._hparams_file_path = hparams_file_path 
        self._checkpoint_path = checkpoint_path
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
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
                audio = self.net_g.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=.667, noise_scale_w=0.8,
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

    def create_wav(self, text, filename = None, speaker = "YunzeNeural", language = "中文", speed=0.7):
        """根據文本創建wav檔案"""
        numpy_voice_array, sr = self.process_text_and_generate_voice_array(self.tts_fn, speaker, text, language, speed)
        numpy_voice_array2 = np.int16(np.array(numpy_voice_array) * 32767)
       
        # 構建完整的文件路徑
        file_str = filename if filename else datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')
        full_path = os.path.join(tts_directory,'audio', f"{file_str}.wav")

        # 確保目錄存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # 寫入 WAV 文件
        with wave.open(full_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(numpy_voice_array2.tobytes())
            
        if redis_client :    
            simplified_text = cc.convert(args.text)
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

    def create_voice_array(self, text, speaker = "YunzeNeural", language = "中文", speed=0.7):
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
    parser.add_argument('--hparams_file_path',
                        type=str,
                        default=f"{tts_directory}/models/YunzeNeural/config.json",
                        help="")
    parser.add_argument('--checkpoint_path',
                        type=str,
                        default=f"{tts_directory}/models/YunzeNeural/G_latest.pth",
                        help="")
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
                        default=0.7,
                        help="")
    parser.add_argument('--text', '-t',
                        type=str,
                        required=True,
                        help="The text you want to crate audio file")
    
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
        argparse_handler()
        
        # redis_client = redis.Redis(host=args.redis_host, port=args.redis_port)
        global redis_client
        redis_client = redis.Redis(host=args.redis_host, port=args.redis_port)
        ping = redis_client.ping()
        
        
        tts = VitsService(
            hparams_file_path = args.hparams_file_path,
            checkpoint_path = args.checkpoint_path
        )
        
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
    