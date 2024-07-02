# -*- coding: utf-8 -*-
import asyncio
import __init__
import json
import signal
import sys
import threading
import redis
from redis import Redis

from util.config.schema import RedisSchema

class RedisCore:
    ## python SingleTon
    _instance = None 
    def __new__(cls, *args, **kwargs): 
        if cls._instance is None: 
            cls._instance = super().__new__(cls) 
        return cls._instance
    
    def __init__(self,config: RedisSchema,channel=None,message_handler=None):
    # def __init__(self, host='localhost', port=51201, channels=None, message_handler=None):
        self._config = config
        self.run_subscriber = True
        self.sub_thread = None

        self._host = config.host
        self._port = config.port
        self._redis_client = redis.Redis(host=config.host, port=config.port)
        self._redis_client_sub = redis.Redis(host=config.host, port=config.port)

        self._channels = channel 
        self._message_handler = message_handler
        signal.signal(signal.SIGINT, self.signal_handler)
        if channel is not None and message_handler is not None:
            self.sub_thread = threading.Thread(target=self.subscriber, args=(self._redis_client_sub,))
            self.sub_thread.daemon = True  # 設置為守護線程
            self.sub_thread.start()
        
    
    def publisher(self, channel, data):
        if not isinstance(data, str):
            try:
                message = json.dumps(data)
            except (TypeError, ValueError) as e:
                print(f"Error converting data to JSON: {e}")
                return
        else:
            message = data

        self._redis_client.publish(channel, message)


    # def subscriber(self, _redis_client_sub):
    #     while self.run_subscriber:
    #         pubsub = _redis_client_sub.pubsub()
    #         if self._channels:
    #             pubsub.subscribe(*self._channels)
    #             channel_names = ', '.join(self._channels)
    #             print(f"Listening for messages on '{channel_names}'.")
    #             for message in pubsub.listen():
    #                 if not self.run_subscriber:
    #                     break
    #                 message_type = message['type']
    #                 channel = message['channel'].decode()
    #                 data_parsed = message['data']
    #                 if isinstance(data_parsed, bytes):
    #                     decoded_data = data_parsed.decode('utf-8')
    #                     try:
    #                         data_json = json.loads(decoded_data)
    #                         data_parsed = data_json
    #                     except json.JSONDecodeError:
    #                         data_parsed = decoded_data
                            
    #                 print(f"Receive: {{'type': {message_type}, 'channel': {channel}, 'data': {data_parsed} }}")
    #                 if message['type'] == 'message' and self._message_handler is not None:
    #                     self._message_handler(channel, data_parsed)
    #             pubsub.close()
    #         else:
    #             print("No channels to subscribe to.")
    #             break
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
                    print(f"Listening for messages on '{channel_names}'.")
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
                                print(f"Error parsing data as JSON: {data_parsed}")
                                data_parsed = data_parsed  # 將字串直接作為 data_parsed
                        elif isinstance(data_parsed, int):
                            print(f"Received integer data: {data_parsed}")
                            continue
                        else:
                            print(f"Unexpected data type: {type(data_parsed)}")
                            continue

                        print(f"Receive: {{'type': {message_type}, 'channel': {channel}, 'data': {data_parsed} }}")
                        if message['type'] == 'message' and self._message_handler is not None:
                            self._message_handler(channel, data_parsed)
                    pubsub.close()
                else:
                    print("No channels to subscribe to.")
                    break
        except redis.ConnectionError as e:
            print(f"Error subscribing to Redis: {e}")



    # def message_handler(self, channel, data_parsed):
    #     raise NotImplementedError("Must override message_handler")

    def signal_handler(self, signum, frame):
        print('Received SIGINT, shutting down...')
        self.run_subscriber = False
        if self.sub_thread.is_alive():
            self.sub_thread.join(timeout=2)
        print('Shutdown complete.')
        sys.exit(0)