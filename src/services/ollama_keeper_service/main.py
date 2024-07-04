import os
import __init__
import requests
import time
from datetime import datetime
import pytz

__init__.logger_start(__file__)
from src.utils.log import logger


def get_bj_time():
    beijing_tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(beijing_tz).strftime("%Y-%m-%d %H:%M:%S")

def keep_model_alive():
    while True:
        data = {"model": "llamafamily/llama3-chinese-8b-instruct", "keep_alive": "5m"}
        headers = {'Content-Type': 'application/json'}
        high_precision_time = time.perf_counter()
        response = requests.post('http://localhost:11434/api/generate', json=data, headers=headers)
        high_precision_time_end = time.perf_counter()
        time_elapsed = high_precision_time_end - high_precision_time
        logger.info(f"高精度時間（精確到微秒）: {time_elapsed * 1000:.6f} ms")
        jsonResponse = response.content.decode('utf-8')  # 将 bytes 转换为字符串以便打印
        logger.info(jsonResponse)
        logger.info(f"當前時間：{get_bj_time()}")
        time.sleep(280)  # 暂停280秒后再次执行

        # '''
        # 7b初次加载模型时间：3.867187177s， 第二次加载模型时间：0.766666ms
        # 14b初次加载模型时间：5.180146173s , 第二次加载模型时间：0.753414ms
        # 72b初次加载模型时间：16.991763358s，第二次加载模型时间：1.358505ms

def main():
    logger.info("OllamaKeeper service is starting...")
    keep_model_alive()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.error("Program interrupted by user.")