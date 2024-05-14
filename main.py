# run_redis_service.py
import time
from services.redis_service import RedisService

def main(): 
    RedisService(port=51201)
    # redis_handler()
    # try:
    #     RedisService()
    # except KeyboardInterrupt:
    #     print("Detected Ctrl+C, shutting down...")

if __name__ == "__main__":
    main()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program interrupted by user.")