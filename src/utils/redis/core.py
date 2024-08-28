# -*- coding: utf-8 -*-
import asyncio
import atexit
import __init__
import json
import signal
import sys
import threading
import redis
from redis import Redis

from src.utils.config.manager import ConfigManager
from src.utils.config.schema import RedisSchema
from src.utils.decorators.singleton import singleton
from src.utils.log import logger

config = ConfigManager()
redis_config = config.redis

# 給 singleton就不能設定 channels, message_handler
# @singleton
# class RedisCoreClass:
class RedisCore:
    def __init__(self,config: RedisSchema = redis_config,channels=None,message_handler=None):
    # def __init__(self, host='localhost', port=51201, channels=None, message_handler=None):
        self._config = config
        self.run_subscriber = True
        self.sub_thread = None

        self._host = config.host
        self._port = config.port
        self._redis_client = redis.Redis(host=config.host, port=config.port)
        self._redis_client_sub = redis.Redis(host=config.host, port=config.port)

        self._channels = channels 
        self._message_handler = message_handler
        signal.signal(signal.SIGINT, self.signal_handler)
        atexit.register(self.cleanup)
        if channels is not None and message_handler is not None:
            self.sub_thread = threading.Thread(target=self.subscriber, args=(self._redis_client_sub,))
            self.sub_thread.daemon = True  # 設置為守護線程
            self.sub_thread.start()
        
    def setter(self, name, value):
        original_value = value  # 存储原始的值

        # 如果 value 不是 Redis 可以接受的类型，将其转换为字符串
        if not isinstance(value, (str, bytes, int, float)):
            try:
                # 尝试将 value 转换为 JSON 字符串
                value = json.dumps(value, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                logger.error(f'Failed to convert value to JSON: {e}')
                raise ValueError("Provided value is not serializable and cannot be stored in Redis.")
        
        self._redis_client.set(name, value)
        logger.info(f'RedisCore set {name}: {original_value}')  # 使用原始的值进行日志记录

    def getter(self, name):
        value = self._redis_client.get(name)
        
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        # 尝试将字符串解析为字典
        try:
            # 如果 value 是 JSON 字符串，解析为字典
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # 如果解析失败，保持原始值
            pass
        
        if value is not None:
            logger.info(f'RedisCore get {name}: {value}')
        return value
    
    def deleter(self, name):
        self._redis_client.delete(name)
        logger.info(f'RedisCore delete {name}')
    
    def publisher(self, channel, data):
        if not isinstance(data, str):
            try:
                message = json.dumps(data)
            except (TypeError, ValueError) as e:
                logger.error(f"Error converting data to JSON: {e}")
                return
        else:
            message = data

        logger.info(f'RedisCore publish {channel}: {data}')
        self._redis_client.publish(channel, message)


    def subscriber(self, redis_client_sub):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            pubsub = redis_client_sub.pubsub()
            while self.run_subscriber:
                pubsub = redis_client_sub.pubsub()
                if self._channels:
                    pubsub.subscribe(*self._channels)
                    channel_names = ', '.join(self._channels)
                    logger.info(f"Listening for messages on '{channel_names}'.")
                    for message in pubsub.listen():
                        if not self.run_subscriber:
                            break
                        message_type = message['type']
                        channel = message['channel'].decode()
                        data_parsed = message['data']
                        if isinstance(data_parsed, bytes):
                            decoded_data = data_parsed.decode('utf-8')
                            try:
                                data_json = json.loads(decoded_data)
                                data_parsed = data_json
                            except json.JSONDecodeError:
                                data_parsed = decoded_data
                        elif isinstance(data_parsed, str):
                            try:
                                data_json = json.loads(data_parsed)
                                data_parsed = data_json
                            except json.JSONDecodeError:
                                logger.error(f"Error parsing data as JSON: {data_parsed}")
                                data_parsed = data_parsed  # 將字串直接作為 data_parsed
                        elif isinstance(data_parsed, int):
                            logger.info(f"Received integer data: {data_parsed}")
                            continue
                        else:
                            logger.error(f"Unexpected data type: {type(data_parsed)}")
                            continue

                        logger.info(f"Receive: {{'type': {message_type}, 'channel': {channel}, 'data': {data_parsed} }}")
                        if message['type'] == 'message' and self._message_handler is not None:
                            self._message_handler(channel, data_parsed)
                    pubsub.close()
                else:
                    logger.info("No channels to subscribe to.")
                    break
        except redis.ConnectionError as e:
            logger.error(f"Error subscribing to Redis: {e}")



    # def message_handler(self, channels, data_parsed):
    #     raise NotImplementedError("Must override message_handler")

    def signal_handler(self, signum, frame):
        logger.info('Received SIGINT, shutting down...')
        self.run_subscriber = False
        if self.sub_thread is not None and self.sub_thread.is_alive():
            self.sub_thread.join(timeout=2)
        logger.info('Shutdown complete.')
        sys.exit(0)

    def cleanup(self):
        if self.sub_thread is not None and self.sub_thread.is_alive():
            self.sub_thread.join(timeout=2)
        logger.info('Shutdown complete.')
        
# RedisCore = RedisCoreClass()