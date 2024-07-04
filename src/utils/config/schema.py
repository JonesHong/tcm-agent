import __init__
from configparser import SectionProxy
import os

class ConfigSchema:
    def __init__(self, config_section: SectionProxy) -> None:
        self._config_section = config_section

class SystemSchema(ConfigSchema):
    """
    [System]
    """
    def __init__(self, config_section: SectionProxy) -> None:
        super().__init__(config_section)
    @property
    def mode(self):
        return self._config_section.get('mode')
    @property
    def opencc_convert(self):
        return self._config_section.get('opencc_convert')
    @property
    def minimized_bat(self):
        return self._config_section.getboolean('minimized_bat')

class LogSchema(ConfigSchema):
    """
    [Log]
    """
    def __init__(self, config_section: SectionProxy) -> None:
        super().__init__(config_section)
    @property
    def level(self):
        return self._config_section.get('level')
    @property
    def rotation(self):
        return self._config_section.getint('rotation')

class RedisSchema(ConfigSchema):
    """
    [Redis]
    """
    def __init__(self, config_section: SectionProxy) -> None:
        super().__init__(config_section)
    @property
    def host(self):
        return self._config_section.get('host')
    @property
    def port(self):
        return self._config_section.getint('port')

class MultiCommSchema(ConfigSchema):
    """
    [MultiComm]
    """
    def __init__(self, config_section: SectionProxy) -> None:
        super().__init__(config_section)
    @property
    def host(self):
        return self._config_section.get('host')
    @property
    def port(self):
        return self._config_section.getint('port')
    @property
    def uploads_dir(self):
        return self._config_section.get('uploads_dir')

class AIKanSheSchema(ConfigSchema):
    """
    [AIKanShe]
    """
    def __init__(self, config_section: SectionProxy) -> None:
        super().__init__(config_section)
    @property
    def appid(self):
        return self._config_section.get('appid')
    @property
    def password(self):
        return self._config_section.getint('password')
    @property
    def token_path(self):
        return self._config_section.get('token_path')
    @property
    def base_url(self):
        return self._config_section.get('base_url')

class RAGFlowSchema(ConfigSchema):
    """
    [RAGFlow]
    """
    def __init__(self, config_section: SectionProxy) -> None:
        super().__init__(config_section)
    @property
    def api_token(self):
        return self._config_section.get('api_token')
    @property
    def base_url(self):
        return self._config_section.get('base_url')

class ASR_ClientSchema(ConfigSchema):
    """
    [ASR_Client]
    """
    def __init__(self, config_section: SectionProxy) -> None:
        super().__init__(config_section)
    @property
    def uv_port(self):
        return self._config_section.getint('uv_port')
    @property
    def host(self):
        return self._config_section.get('host')
    @property
    def port(self):
        return self._config_section.getint('port')
    @property
    def lang(self):
        return self._config_section.get('lang')
    @property
    def translate(self):
        return self._config_section.getboolean('translate')
    @property
    def model(self):
        return self._config_section.get('model')
    @property
    def use_vad(self):
        return self._config_section.getboolean('use_vad')
    @property
    def save_output_recording(self):
        return self._config_section.getboolean('save_output_recording')
    @property
    def output_recording_filename(self):
        return self._config_section.get('output_recording_filename')
    @property
    def output_transcription_path(self):
        return self._config_section.get('output_transcription_path')
    @property
    def resettable_timer_seconds(self):
        return self._config_section.getint('resettable_timer_seconds')

class TTSSchema(ConfigSchema):
    """
    [TTS]
    """
    def __init__(self, config_section: SectionProxy) -> None:
        super().__init__(config_section)
    @property
    def speaker(self):
        return self._config_section.get('speaker')
    @property
    def language(self):
        return self._config_section.get('language')
    @property
    def speed(self):
        return self._config_section.getfloat('speed')
    @property
    def hparams_file_path(self):
        return self._config_section.get('hparams_file_path')
    @property
    def checkpoint_path(self):
        return self._config_section.get('checkpoint_path')
    @property
    def create_wav_dir(self):
        return self._config_section.get('create_wav_dir')

class AgentSchema(ConfigSchema):
    """
    [Agent]
    """
    def __init__(self, config_section: SectionProxy) -> None:
        super().__init__(config_section)
    @property
    def mode(self):
        return self._config_section.get('mode')
    @property
    def model_name(self):
        return self._config_section.get('model_name')
