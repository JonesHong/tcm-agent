import __init__
import asyncio
import signal

from src.services.multi_comm_service.core import socket_app
from src.utils.config.manager import ConfigManager
from src.utils.log import logger, uvicorn_init_config

__init__.logger_start()
# 定義自訂的信號處理器來優雅地停止服務
def handle_exit(sig, frame):
    logger.info("收到停止信號，正在停止服務...")
    for task in asyncio.all_tasks():
        task.cancel()
    loop = asyncio.get_event_loop()
    loop.stop()

def main():
    
    import uvicorn
    
    config = ConfigManager()
    multicomm_config = config.multicomm
    # aikanshe_config = config.aikanshe
    uvicorn_config = uvicorn.Config(socket_app, host=multicomm_config.host, port=multicomm_config.port,timeout_keep_alive=60)
    server = uvicorn.Server(uvicorn_config)
    
    loop = asyncio.get_event_loop()
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        # # 将uvicorn输出的全部让loguru管理
        uvicorn_init_config()

        loop.run_until_complete(server.serve())
    except (SystemExit, KeyboardInterrupt, asyncio.CancelledError):
        logger.info("服務已停止")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        
if __name__ == "__main__":
    main()
