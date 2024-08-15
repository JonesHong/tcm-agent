from pydantic import BaseModel
import __init__
import os
from fastapi import APIRouter, FastAPI, HTTPException, Form, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime, timezone

from src.schemas.fastapi import CompletionModel
from src.utils.log import logger
from src.services.multi_comm_service.aikenshe_utils import get_new_token, get_token,  process_file
from src.services.multi_comm_service.ragflow_utils import get_new_conversation, post_completion


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_router = APIRouter()

# FastAPI 路由
app.include_router(api_router)
UPLOAD_DIR = os.path.join(__init__.SRC_DIR, "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@api_router.get("/")
async def read_main():
    return {"message": "Hello from FastAPI"}

@api_router.get("/account/login")
async def get_account_login():
    try:
        token = await get_new_token()
        return {"token": token}
    except Exception as e:
        logger.info(f"登入失敗: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@api_router.get("/login", response_model=dict)
async def post_login():
    try:
        token = await get_token()
        return {"token": token}
    except Exception as e:
        logger.info(f"登入失敗: {e}")
        raise HTTPException(status_code=500, detail="Login failed")
    
@api_router.post("/agency/quanxi", response_model=dict)
async def quanxi_analysis_api(
    age: int = Form(35),
    appkey: str = Form('v1eaevl3dum3i9g46ar5c8cghd8cle7t'),
    file: UploadFile = File(...),
    male: int = Form(...),
    methodName: Optional[str] = Form("quanxi"),
    confidence: Optional[float] = Form(0.7),
    desease: Optional[str] = Form(None),
    frontCamera: Optional[int] = Form(1),
    imageUrl: Optional[str] = Form("http://"),
    isYuejin: Optional[int] = Form(None),
    name: Optional[str] = Form(None),
    timestamp: Optional[str] = Form(datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'))
):
    try:
        file.file.seek(0)
        uploaded_file_data = await file.read()
        result = await process_file(
            uploaded_file_data,
            file.filename,
            age,
            appkey,
            male,
            methodName,
            confidence,
            desease,
            frontCamera,
            imageUrl,
            isYuejin,
            name,
            timestamp
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.info(f"全息舌像分析發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")
    
async def quanxi_analysis_local_file(
    file_path: str,
    age: int = 35,
    appkey: str = "v1eaevl3dum3i9g46ar5c8cghd8cle7t" ,
    male: int = 1,
    methodName: str = "quanxi",
    confidence: float = 0.7,
    desease: Optional[str] = None,
    frontCamera: int = 1,
    imageUrl: str = "http://",
    isYuejin: Optional[int] = None,
    name: Optional[str] = None,
    timestamp: Optional[str] = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
):
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
        result = await process_file(
            file_data,
            os.path.basename(file_path),
            age,
            appkey,
            male,
            methodName,
            confidence,
            desease,
            frontCamera,
            imageUrl,
            isYuejin,
            name,
            timestamp
        )
        return result
    except HTTPException as e:
        logger.info(f"處理檔案發生錯誤: {e.detail}")
        raise
    except Exception as e:
        logger.info(f"處理本地檔案發生錯誤: {e}")
        raise HTTPException(status_code=500, detail="Processing failed")


@api_router.get("/get_new_conversation")
async def get_new_conversation_api():
    try:
        data = await get_new_conversation()
        return data
    except Exception as e:
        logger.info(f"新建對話失敗: {e}")
        raise HTTPException(status_code=500, detail="Get new conversation failed")
    

@api_router.post("/post_completion")
async def post_completion_api(message_content: str= Form(...)):
    try:
        print(message_content)
        data = await post_completion(message_content)
        return data
    except Exception as e:
        logger.info(f"送出對話失敗: {e}")
        raise HTTPException(status_code=500, detail="Post completion failed")
# @api_router.post("/post_completion")
# def post_completion_api(message_content: str = Form(...)):
#     try:
#         # print(message_content)
#         data = post_completion(message_content)
#         return data
#     except Exception as e:
#         logger.info(f"送出對話失敗: {e}")
#         raise HTTPException(status_code=500, detail="Post completion failed")

# class MessageContent(BaseModel):
#     message_content: str
# @api_router.post("/get_answer")
# def post_completion_api(message:MessageContent):
#     import requests
#     print(message)

#     url = "http://localhost/v1/api/completion"
#     headers = {
#         "Authorization": "Bearer ragflow-k1M2NhZjU0Mzk2NDExZWY5YmVkMDI0Mm",
#         "Content-Type": "application/json"
#     }
#     data = {
#         "conversation_id": "0776ebca396511ef991a0242ac190003",
#         "quote": True,
#         "stream": False,
#         "messages": [
#             {
#                 "role": "user",
#                 "content": "最近一直咳嗽，可能是什麼原因，要怎麼改善?"
#             }
#         ]
#     }

#     response = requests.post(url, headers=headers, json=data)
#     print(response.json())

