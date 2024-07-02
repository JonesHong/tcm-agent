import __init__
from configparser import SectionProxy
import os

class ConfigSchema:
    def __init__(self, config_section: SectionProxy) -> None:
        self._config_section = config_section

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
    def log_path(self):
        # 使用默认值，如果没有值，则返回默认路径
        log_path = self._config_section.get('log_path')
        return log_path if log_path else os.path.join(__init__.ROOT_DIR, "logs")
    @property
    def process_id(self):
        return self._config_section.get('process_id')
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

class AIKanSheSchema(ConfigSchema):
    """
    [AIKanShe]
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
    def appid(self):
        return self._config_section.get('appid')
    @property
    def password(self):
        return self._config_section.get('password')

class ASRSchema(ConfigSchema):
    """
    [ASR]
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
    def lang(self):
        return self._config_section.get('lang')
    @property
    def model(self):
        return self._config_section.get('model')
    @property
    def use_vad(self):
        return self._config_section.getboolean('use_vad')
    @property
    def translate(self):
        return self._config_section.getboolean('translate')
    @property
    def chinese_convert(self):
        return self._config_section.get('chinese_convert')

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

class AgentSchema(ConfigSchema):
    """
    [Agent]
    """
    def __init__(self, config_section: SectionProxy) -> None:
        super().__init__(config_section)
    @property
    def mode(self):
        return self._config_section.get('mode')
