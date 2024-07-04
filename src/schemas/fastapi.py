from datetime import datetime, timezone
from fastapi import File, Form, UploadFile
from pydantic import BaseModel
from typing import List, Optional


class LoginInModel(BaseModel):
    appId: str
    methodName: str
    password: str
    timestamp: str
    userKey: str

class QuanxiRequest(BaseModel):
    age: int = 35
    appkey: str = "v1eaevl3dum3i9g46ar5c8cghd8cle7t"
    file: UploadFile = None
    male: int = 0
    methodName: Optional[str] = "quanxi" # 全息
    confidence: Optional[float] = 0.7
    desease: Optional[str] = None
    frontCamera: Optional[int] = 1
    imageUrl: Optional[str] = "http://"
    isYuejin: Optional[int] = None
    name: Optional[str] = None
    timestamp: Optional[str] = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

class MessageModel(BaseModel):
    role: str
    content: str
class CompletionModel(BaseModel):
    conversation_id: str
    messages: List[MessageModel] = []
    quote: bool = True
    stream: bool = False
    # doc_ids:  Optional[str] = None

