# -*- coding: utf-8 -*
import __init__
import argparse
import sys
import os

from src.packages.vits.text import text_to_sequence
import src.packages.vits.commons as commons
import src.packages.vits.utils as utils
from src.packages.vits.models import SynthesizerTrn
from torch import no_grad, LongTensor
import torch

import cmd
import wave
import numpy as np
from datetime import datetime

from opencc import OpenCC
from src.utils.config.manager import ConfigManager
from src.utils.log import logger
from src.utils.redis.channel import RedisChannel
from src.utils.decorators.singleton import singleton
from src.utils.redis.core import RedisCore

config = ConfigManager()
system_config = config.system
tts_config = config.tts

redis_core = RedisCore()
cc = OpenCC(system_config.opencc_convert)  # Traditional Chinese to Simplified Chinese

# If root is main.py
assets_file_path = {
    "hparams_file_path": __init__.trim_path(os.path.join(__init__.SRC_DIR, tts_config.hparams_file_path)),
    "checkpoint_path":  __init__.trim_path(os.path.join(__init__.SRC_DIR, tts_config.checkpoint_path)),
}

@singleton
class VitsClass(cmd.Cmd):
    intro = 'Welcome to the generator wav. Type help or ? to list commands.\n'
    prompt = 'Text: '
    def __init__(self):
        super().__init__()
        self.args = None
        self.speaker= None
        self.language= None
        self.speed= None
        # print(args.speaker,args)
        self._stop = False
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
                
        # logger.info(torch.version.cuda)   
        # logger.info('torch.cuda.is_available',torch.cuda.is_available() )
        self.language_marks = {
            "Japanese": "",
            "日本語": "[JA]",
            "中文": "[ZH]",
            "English": "[EN]",
            "Mix": "",
            }
        self.lang = ['日本語', '中文', 'English', 'Mix']
                
        self.tts_fn = self.create_tts_fn()
        self.hps = utils.get_hparams_from_file(assets_file_path['hparams_file_path'])
        self.set_model()
        
    def argparse_handler(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--speaker',
                            type=str,
                            default= tts_config.speaker,
                            help="TTS  model")
        parser.add_argument('--language', '-l',
                            type=str,
                            default= tts_config.language,
                            help="Language for asr.")
        parser.add_argument('--speed',
                            type=int,
                            default= tts_config.speed,
                            help="")
        parser.add_argument('--text', '-t',
                            type=str,
                            # required=True,
                            help="The text you want to crate audio file")
        
        self.args = parser.parse_args()
        
        self.speaker= self.args.speaker
        self.language= self.args.language
        self.speed= self.args.speed
    
    def default(self, line):
        logger.success(f"(text) {line}")  # 记录用户输入
        response = self.create_wav(text=line)
        logger.info(f"(tts) {response}")
        # response = agent.invoke(line)
        # logger.info(f"(agent) {response}")

    def do_exit(self, line):
        """Exit the interactive agent."""
        logger.info('Exiting the interactive agent.')
        self._stop = True
        return True

    def sigint_handler(self, signum, frame):
        try:
            print("Received SIGINT, shutting down...")
            # logger.info("Received SIGINT, shutting down...")
            self._stop = True
            self.onecmd('exit')
        except Exception as e:
            logger.error(f"Exception in signal handler: {e}")
        finally:
            sys.exit(0)
            
    def cmdloop(self, intro=None):
        while not self._stop:
            try:
                super().cmdloop(intro=intro)
                self._stop = True  # Exit loop if cmdloop() completes
            except KeyboardInterrupt:
                self._stop = True

    def set_model(self):
        self.net_g = SynthesizerTrn(
            len(self.hps.symbols),
            self.hps.data.filter_length // 2 + 1,
            self.hps.train.segment_size // self.hps.data.hop_length,
            n_speakers=self.hps.data.n_speakers,
            **self.hps.model).to(self.device)
        _ = self.net_g.eval()

        _ = utils.load_checkpoint(assets_file_path['checkpoint_path'], self.net_g, None)

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

    def create_wav(self, text, speaker = None , language = None, speed = None, filename = None):
        speaker = speaker if speaker else self.args.speaker
        language = language if language else self.args.language
        speed = speed if speed else self.args.speed
        """根據文本創建wav檔案"""
        numpy_voice_array, sr = self.process_text_and_generate_voice_array(self.tts_fn, speaker, text, language, speed)
        numpy_voice_array2 = np.int16(np.array(numpy_voice_array) * 32767)
       
        # 構建完整的文件路徑
        file_str = filename if filename else datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')
        full_path = os.path.join(__init__.SRC_DIR, 'audio', f"{file_str}.wav")

        # 確保目錄存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # 寫入 WAV 文件
        with wave.open(full_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(numpy_voice_array2.tobytes())
            
        simplified_text = cc.convert(text)
        tts_done_data = {"audio_path": os.path.normpath(full_path),"text": simplified_text}
        # tts_done_message = json.dumps(data)
        redis_core.publisher(RedisChannel.tts_service_done, tts_done_data)
        # logger.info(f"Redis publish {RedisChannel.tts_service_done}: {tts_done_data}")
            
            # time.sleep(1)
            # do_tts_message = json.dumps({"text": ""})
            # redis_client.publish(RedisChannel.do_tts_service, do_tts_message)
            # logger.info(f"Redis publish {RedisChannel.do_tts_service}: {do_tts_message}")
        # 返回完整的文件路徑
        return tts_done_data

    def create_voice_array(self, text, speaker, language, speed):
        """根據文本生成聲音數據列表"""
        numpy_voice_array, _ = self.process_text_and_generate_voice_array(self.tts_fn, speaker, text, language, speed)
        return numpy_voice_array
    
Vits = VitsClass()