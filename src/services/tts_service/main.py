# -*- coding: utf-8 -*
import __init__
import signal

from opencc import OpenCC
from src.services.tts_service.vits import Vits
from src.utils.config.manager import ConfigManager
from src.utils.log import logger
from src.utils.redis.channel import RedisChannel
from src.utils.redis.core import RedisCore

__init__.logger_start()
config = ConfigManager()
system_config = config.system
redis_config = config.redis
tts_config = config.tts

cc = OpenCC(system_config.opencc_convert)  # Traditional Chinese to Simplified Chinese

channels = [
    RedisChannel.do_tts_service
]
def message_handler(channel, data_parsed):
    if channel == RedisChannel.do_tts_service:
        handle_do_tts_service(data_parsed)
        
    pass
redis_core = RedisCore(channels=channels,message_handler=message_handler)

def handle_do_tts_service( data_parsed):
    try:
        text = data_parsed['text']
        if text != '' and text is not None:
            #  tts_service
            Vits.create_wav(text)
        else:
            logger.info('text is empty')
    except Exception as e:
        logger.info(f"Error handling TTS service: {e}")
        

        
def main():
    Vits.argparse_handler()
    # global tts_service
    # tts_service = VitsService()
    
    signal.signal(signal.SIGINT, Vits.sigint_handler)
    try:
        Vits.cmdloop()
        # tts_service.create_wav(
        #     text = args.text,
        #     speaker = args.speaker,
        #     language = args.language,
        #     speed = args.speed
        # )
    except Exception as e:
        logger.info(f"Error during execution: {e}")
    finally:
        logger.info("Cleanup complete.")

if __name__ == "__main__":
    main()