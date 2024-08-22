import asyncio
import json
import __init__
import httpx
from fastapi import HTTPException
import requests

from src.schemas.fastapi import CompletionModel, MessageModel
from src.utils.config.manager import ConfigManager
from src.utils.log import logger
from src.utils.redis.channel import RedisChannel
from src.utils.redis.core import RedisCore

redis_core = RedisCore()
config = ConfigManager()
multicomm_config = config.multicomm
ragflow_config = config.ragflow

# 定義 url_dict
url_dict = {
    "new_conversation": f"{ragflow_config.base_url}api/new_conversation",
    "completion": f"{ragflow_config.base_url}api/completion",
}

async def get_new_conversation():
    try:
        logger.info("新建聊天")
        headers = {
            "Authorization": f'Bearer {ragflow_config.api_token}',
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url_dict['new_conversation'], headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, detail="Failed to new conversation")
            data = response.json()
            conversation_id = data['data']['id']  # 获取 conversation_id
            redis_core.setter(RedisChannel.conversation_id, conversation_id)  # 保存到 Redis
            return conversation_id  # 返回 conversation_id 作为字符串
    except Exception as e:
        logger.info(f"新建聊天 發生錯誤: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to new conversation")





async def post_completion(message_content, stream=None):
    try:
        # 從 Redis 中獲取 conversation_id，或創建一個新的
        redis_conversation_id = redis_core.getter(RedisChannel.conversation_id)
        conversation_id = redis_conversation_id if redis_conversation_id else await get_new_conversation()

        logger.info("送出訊息")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {ragflow_config.api_token}',
            "Connection": "keep-alive"
        }

        body = {
            "conversation_id": conversation_id,
            "quote": True,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是一個虛擬中醫智能助手，根據知識庫的內容來回答問題。"
                        "請參考知識庫中的數據，結合中醫理論，詳細回答問題。"
                        "當所有知識庫內容都與問題無關時，請包括“知識庫中未找到相關答案！”這句話。"
                        "在回答時，應考慮之前的聊天歷史，以提供更準確和連貫的建議。\n\n"
                        "以下是知識庫：\n{knowledge}\n以上是知識庫。"
                    )
                },
                {
                    "role": "user",
                    "content": f"請用中文回答我。{message_content}。给出中医诊断和处方建议"
                }
            ]
        }

        logger.info(f"Request Body: {json.dumps(body, indent=2, ensure_ascii=False)}")

        async with httpx.AsyncClient() as client:
            if stream is None or stream:  # 啟用 stream 模式
                try:
                    async with client.stream("POST", url_dict['completion'], json=body, headers=headers, timeout=httpx.Timeout(10.0)) as response:
                        logger.info(f"Response Status Code: {response.status_code}")

                        if response.status_code == 200:
                            response_text = ""
                            async for chunk in response.aiter_text():
                                cleaned_chunk = chunk.strip()

                                if '"data": true' in cleaned_chunk:  # 檢測到結束標記
                                    logger.info("Final chunk received, processing the accumulated response.")
                                    try:
                                        # 移除前面的 'data:' 標頭並轉換為 JSON 物件
                                        if isinstance(response_text, str):
                                            data_str = response_text.replace('data:', '')
                                            data = json.loads(data_str)
                                            # print(1111111,response_text)
                                            # print(22222222,data)
                                            return data
                                        else:
                                            logger.error(f"Unexpected type for response_text: {type(response_text)}")
                                    except json.JSONDecodeError as e:
                                        logger.error(f"Failed to decode JSON after receiving the final chunk: {e}")
                                    break

                                # 只保留當前的 chunk
                                response_text = cleaned_chunk
                                logger.info(f"Received chunk: {cleaned_chunk}")
                        else:
                            logger.warning(f"Response Content: {response.text}")
                except Exception as e:
                    logger.error(f"Exception during streaming: {e}")
                finally:
                    await response.aclose()  # 確保生成器正確關閉
            else:  # 不啟用 stream 模式
                response = None
                for attempt in range(3):  # 重試最多3次
                    try:
                        response = await client.post(
                            url_dict['completion'], 
                            json=body, 
                            headers=headers, 
                            timeout=httpx.Timeout(10.0)  # 設置超時為10秒
                        )
                        logger.info(f"Response Status Code: {response.status_code}")

                        if response.status_code == 200:
                            if response.text.strip():  # 檢查回應是否為空
                                try:
                                    data = response.json()
                                    return data  # 成功後返回資料
                                except json.JSONDecodeError:
                                    logger.error(f"Failed to decode JSON from response: {response.text}")
                            else:
                                logger.error("Response content is empty.")
                        else:
                            logger.warning(f"Response Content: {response.text}")

                    except httpx.RequestError as e:
                        logger.error(f"Request attempt {attempt + 1} failed: {e}")
                    except httpx.HTTPStatusError as e:
                        logger.error(f"HTTP error on attempt {attempt + 1}: {e.response.status_code} - {e.response.text}")
                    except Exception as e:
                        logger.error(f"Attempt {attempt + 1} failed: {e}")
                        await asyncio.sleep(1)  # 重試前等待

                # 如果所有重試均失敗，根據情況拋出 HTTP 例外
                if response is None:
                    raise HTTPException(status_code=500, detail="Failed to post completion after 3 attempts")
                else:
                    raise HTTPException(status_code=response.status_code, detail="Failed to post completion after 3 attempts")

    except Exception as e:
        logger.error(f"送出訊息 發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Failed to post completion due to an unexpected error")
