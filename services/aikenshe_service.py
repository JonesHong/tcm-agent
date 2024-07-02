import __init__
import argparse
import asyncio
import signal

from util.aikenshe.core import socket_app
from util.config.manager import ConfigManager

# 定義自訂的信號處理器來優雅地停止服務
def handle_exit(sig, frame):
    print("收到停止信號，正在停止服務...")
    for task in asyncio.all_tasks():
        task.cancel()
    loop = asyncio.get_event_loop()
    loop.stop()

def main():
    
    import uvicorn
    
    config = ConfigManager()
    ai_ken_she_config = config.ai_ken_she
    uvicorn_config = uvicorn.Config(socket_app, host=ai_ken_she_config.host, port=ai_ken_she_config.port)
    server = uvicorn.Server(uvicorn_config)
    
    loop = asyncio.get_event_loop()
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        loop.run_until_complete(server.serve())
    except (SystemExit, KeyboardInterrupt, asyncio.CancelledError):
        print("服務已停止")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        
if __name__ == "__main__":
    main()
