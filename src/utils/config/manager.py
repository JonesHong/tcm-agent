import __init__
import configparser
import os
from .schema import (
    SystemSchema,
    LogSchema,
    RedisSchema,
    MultiCommSchema,
    AIKanSheSchema,
    ASR_ClientSchema,
    TTSSchema,
    AgentSchema,
    RAGFlowSchema,
)


class ConfigManager(object):
    _instance = None
    
    def __new__(cls, *args, **kwargs): 
        if cls._instance is None: 
            cls._instance = super().__new__(cls) 
        return cls._instance
    
    def __init__(self, config_path: str= os.path.join(__init__.ROOT_DIR, 'config', 'config.ini')):
        self._config = configparser.ConfigParser()
        self._config.read(config_path ,encoding='utf-8')

        self.system = SystemSchema(self._config['System'])
        self.log = LogSchema(self._config['Log'])
        self.redis = RedisSchema(self._config['Redis'])
        self.multicomm = MultiCommSchema(self._config['MultiComm'])
        self.aikanshe = AIKanSheSchema(self._config['AIKanShe'])
        self.asr_client = ASR_ClientSchema(self._config['ASR_Client'])
        self.tts = TTSSchema(self._config['TTS'])
        self.agent = AgentSchema(self._config['Agent'])
        self.ragflow = RAGFlowSchema(self._config['RAGFlow'])
