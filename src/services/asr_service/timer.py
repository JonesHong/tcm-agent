import threading
import time
from src.utils.config.manager import ConfigManager

config = ConfigManager()
system_config = config.system

class ResettableTimer:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.timer = None
        self.lock = threading.Lock()
        self.tick_thread = None
        self.stop_tick = threading.Event()

    def reset(self):
        with self.lock:
            if self.timer is not None:
                self.timer.cancel()
            self.timer = threading.Timer(self.interval, self.action)
            self.timer.start()
            
            # 停止之前的 tick 线程（如果存在）
            if self.tick_thread is not None and self.tick_thread.is_alive():
                self.stop_tick.set()
                self.tick_thread.join()

            # 启动新的 tick 线程
            self.stop_tick.clear()
            self.tick_thread = threading.Thread(target=self._tick)
            self.tick_thread.start()

    def stop(self):
        with self.lock:
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None
        self.stop_tick.set()
        if self.tick_thread is not None:
            self.tick_thread.join()

    def _tick(self):
        while not self.stop_tick.is_set():
            if system_config.mode == "test":
                print("Tick")
                time.sleep(1)
