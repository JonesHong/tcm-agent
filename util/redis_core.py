# -*- coding: utf-8 -*-

import json
import signal
import sys
import threading
import redis
from redis import Redis

class RedisCore:
    def __init__(self, host='localhost', port=51201, channels=None,message_handler=None):
        self.run_subscriber = True
        self.sub_thread = None

        self._host = host
        self._port = port
        self.channels = channels if channels is not None else []
        self.redis_client_pub = redis.Redis(host=host, port=port)
        self.redis_client_sub = redis.Redis(host=host, port=port)

        signal.signal(signal.SIGINT, self.signal_handler)
        self.sub_thread = threading.Thread(target=self.subscriber, args=(self.redis_client_sub,))
        self.sub_thread.daemon = True  # 設置為守護線程
        self.sub_thread.start()
        self.message_handler=message_handler

    def publisher(self, channel, data):
        # message = json.dumps(data)
        self.redis_client_pub.publish(channel, data)

    def subscriber(self, redis_client_sub):
        while self.run_subscriber:
            pubsub = redis_client_sub.pubsub()
            if self.channels:
                pubsub.subscribe(*self.channels)
                channel_names = ', '.join(self.channels)
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
                            
                    print(f"Receive: {{'type': {message_type}, 'channel': {channel}, 'data': {data_parsed} }}")
                    if message['type'] == 'message':
                        self.message_handler(channel, data_parsed)
                pubsub.close()
            else:
                print("No channels to subscribe to.")
                break

    def message_handler(self, channel, data_parsed):
        raise NotImplementedError("Must override message_handler")

    def signal_handler(self, signum, frame):
        print('Received SIGINT, shutting down...')
        self.run_subscriber = False
        if self.sub_thread.is_alive():
            self.sub_thread.join(timeout=2)
        print('Shutdown complete.')
        sys.exit(0)