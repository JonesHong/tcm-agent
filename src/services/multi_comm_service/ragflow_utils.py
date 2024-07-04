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
            # "Content-Type": "application/json",
            "Authorization": f'Bearer {ragflow_config.api_token}',
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url_dict['new_conversation'], headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, detail="Failed to new conversation")
            data = response.json()
            # print(data)
            redis_core.setter(RedisChannel.conversation_id, data['data']['id'])
            return data
    except Exception as e:
        logger.info(f"新建聊天 發生錯誤: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to new conversation")

def post_completion(message_content):
    try:
        redis_conversation_id = redis_core.getter(RedisChannel.conversation_id)
        conversation_id = redis_conversation_id if redis_conversation_id else get_new_conversation()
        logger.info("送出訊息")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {ragflow_config.api_token}',
        }
        body = CompletionModel(
            conversation_id=conversation_id,
            quote=True,
            stream=False,
            messages=[
                MessageModel(
                    role="system",
                    content="你是一个智能助手，請总结知识库的内容来回答问题，请列举知识库中的数据详细回答。当所有知识库内容都与问题无关时，你的回答必须包括“知识库中未找到您要的答案！”这句话。回答需要考虑聊天历史 {history}。\n          以下是知识库：\n          {knowledge}\n          以上是知识库。"
                ).model_dump(),
                MessageModel(
                    role="user",
                    content=f"請用中文回答我。{message_content}"
                ).model_dump()
            ]
        ).model_dump()

        # logger.info(f"Request Body: {json.dumps(body, indent=2, ensure_ascii=False)}")  # 打印请求体

        for attempt in range(5):  # 重试机制
            try:
                response = requests.post(url_dict['completion'], json=body, headers=headers)
                logger.info(f"Response Status Code: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    return data
                else:
                    logger.info(f"Response Content: {response.text}")  # 打印响应内容
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
            import time
            time.sleep(1)  # 重试前等待
        raise HTTPException(status_code=500, detail="Failed to post completion after 5 attempts")
    except Exception as e:
        logger.info(f"送出訊息 發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Failed to post completion")
# async def post_completion(message_content):
#     try:
#         redis_conversation_id = redis_core.getter(RedisChannel.conversation_id)
#         conversation_id = redis_conversation_id if redis_conversation_id else await get_new_conversation()
#         logger.info("送出訊息")
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f'Bearer {ragflow_config.api_token}',
#         }
#         body = CompletionModel(
#             conversation_id=conversation_id,
#             quote=True,
#             stream=False,
#             messages=[
#                 MessageModel(
#                     role="system",
#                     content="你是一个智能助手，請总结知识库的内容来回答问题，请列举知识库中的数据详细回答。当所有知识库内容都与问题无关时，你的回答必须包括“知识库中未找到您要的答案！”这句话。回答需要考虑聊天历史 {history}。\n          以下是知识库：\n          {knowledge}\n          以上是知识库。"
#                 ).model_dump(),
#                 MessageModel(
#                     role="user",
#                     content=f"請用中文回答我。{message_content}"
#                 ).model_dump()
#             ]
#         ).model_dump()

#         # body = {
#         #     "conversation_id": conversation_id,
#         #     "quote": True,
#         #     "stream": False,
#         #     "messages": [
#         #         # {"role":"system","content":"你是一个智能助手，請总结知识库的内容来回答问题，请列举知识库中的数据详细回答。当所有知识库内容都与问题无关时，你的回答必须包括“知识库中未找到您要的答案！”这句话。回答需要考虑聊天历史 {history}。\n          以下是知识库：\n          {knowledge}\n          以上是知识库。"},
#         #         {"role":"user","content":f"請用中文回答我。{message_content}"}
#         #     ]
#         # }
#         # print(body)
#         logger.info(f"Request Body: {json.dumps(body, indent=2, ensure_ascii=False)}")  # 打印请求体


#         # logger.info(
#         #     f"Request Body: {json.dumps(body, indent=2, ensure_ascii=False)}")  # 打印请求体

#         async with httpx.AsyncClient() as client:  # 修改为异步上下文管理器
#             response = None  # 在循环前定义response变量
#             for attempt in range(5):  # 重试机制
#                 try:
#                     response = await client.post(url_dict['completion'],  json=body, headers=headers)
#                     logger.info(
#                         f"Response Status Code: {response.status_code}")
#                     if response.status_code == 200:
#                         data = response.json()
#                         return data
#                     else:
#                         logger.info(
#                             f"Response Content: {response.text}")  # 打印响应内容
#                 except httpx.RequestError as e:
#                     logger.error(f"Request attempt {attempt + 1} failed: {e}")
#                 except httpx.HTTPStatusError as e:
#                     logger.error(f"HTTP error on attempt {attempt + 1}: {e.response.status_code} - {e.response.text}")
#                 except Exception as e:
#                     logger.error(f"Attempt {attempt + 1} failed: {e}")
#                     await asyncio.sleep(1)  # 重试前等待
#             if response is None:
#                 raise HTTPException(
#                     status_code=500, detail="Failed to post completion after 5 attempts")
#             else:
#                 raise HTTPException(
#                     status_code=response.status_code, detail="Failed to post completion after 5 attempts")
#     except Exception as e:
#         logger.info(f"送出訊息 發生錯誤: {e}")
#         raise HTTPException(
#             status_code=500, detail="Failed to post completion")
