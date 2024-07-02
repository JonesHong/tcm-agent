import __init__
import configparser
import os
from .schema import (
    LogSchema,
    RedisSchema,
    AIKanSheSchema,
    ASRSchema,
    TTSSchema,
    AgentSchema,
)


class ConfigManager(object):
    _instance = None
    
    def __new__(cls, *args, **kwargs): 
        if cls._instance is None: 
            cls._instance = super().__new__(cls) 
        return cls._instance
    
    def __init__(self, config_path: str= os.path.join(__init__.ROOT_DIR, 'config.ini')):
        self._config = configparser.ConfigParser()
        self._config.read(config_path ,encoding='utf-8')

        self.log = LogSchema(self._config['Log'])
        self.redis = RedisSchema(self._config['Redis'])
        self.aikanshe = AIKanSheSchema(self._config['AIKanShe'])
        self.asr = ASRSchema(self._config['ASR'])
        self.tts = TTSSchema(self._config['TTS'])
        self.agent = AgentSchema(self._config['Agent'])
