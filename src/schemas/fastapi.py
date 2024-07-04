from datetime import datetime, timezone
from fastapi import File, Form, UploadFile
from pydantic import BaseModel
from typing import Optional


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
    
aikenshe_result_dict = {
    "age": "年齡",
    "aijiu": "艾灸與按摩",
    "bagang": "八綱辨證",
    "bagangDesc": "八綱辨證描述",
    "botai": "是否有剝苔,0-否，1-是",
    "botaiDesc": "剝苔描述",
    "botaiMean": "剝苔診斷意義",
    "chagndao": "腸道是否異常,0-否，1-是",
    "chagndaoDesc": "腸道描述",
    "chagndaoMean": "腸道診斷意義",
    "chihen": "是否有齒痕,0-否，1-是",
    "chihenDesc": "齒痕描述",
    "chihenMean": "齒痕診斷意義",
    "createTime": "檢測時間",
    "dianci": "是否有點刺,0-否，1-是",
    "dianciDesc": "點刺描述",
    "dianciMean": "點刺診斷意義",
    "feel": "身體表現",
    "fei": "肺是否異常,0-否，1-是",
    "feiDesc": "肺描述",
    "feiMean": "肺診斷意義",
    "food": "飲食調養",
    "frontCamera": "boolean",
    "gandan": "肝膽是否異常,0-否，1-是",
    "gandanDesc": "肝膽描述",
    "gandanMean": "肝膽診斷意義",
    "goods": "商品配置",
    "id": "id",
    "isYuejin": "是否月經，0:否，1-是",
    "liewen": "是否有裂紋,0-否，1-是",
    "liewenDesc": "裂紋描述",
    "liewenMean": "裂紋診斷意義",
    "life": "情志起居",
    "male": "是否男性,0:女，1-男",
    "medical": "藥物治療",
    "name": "姓名",
    "nao": "大腦是否異常,0-否，1-是",
    "naoDesc": "大腦描述",
    "naoMean": "大腦診斷意義",
    "nuanchao": "卵巢是否異常,0-否，1-是",
    "nuanchaoDesc": "卵巢描述",
    "nuanchaoMean": "卵巢診斷意義",
    "pifu": "皮膚是否異常,0-否，1-是",
    "pifuDesc": "皮膚描述",
    "pifuMean": "皮膚診斷意義",
    "piwei": "脾胃是否異常,0-否，1-是",
    "piweiDesc": "脾胃描述",
    "piweiMean": "脾胃診斷意義",
    "qianliexian": "前列腺是否異常,0-否，1-是",
    "qianliexianDesc": "前列腺描述",
    "qianliexianMean": "前列腺診斷意義",
    "qiji": "氣機是否異常,0-否，其他-是",
    "qijiDesc": "氣機描述",
    "qijiMean": "氣機診斷意義",
    "qixiaoConfidence": "奇效描述置信度",
    "qixiaoDesc": "奇效描述",
    "recomand": "調理建議",
    "roiImage": "截取舌頭圖片地址",
    "ruxian": "乳腺是否異常,0-否，1-是",
    "ruxianDesc": "乳腺描述",
    "ruxianMean": "乳腺診斷意義",
    "score": "健康得分",
    "scoreDesc": "健康得分說明",
    "shemianConfidence": "舌色置信度",
    "shemianDesc": "舌色描述",
    "shemianName": "舌色類型",
    "shen": "腎是否異常,0-否，1-是",
    "shenDesc": "腎描述",
    "shenMean": "腎診斷意義",
    "shexinConfidence": "舌型置信度",
    "shexinDesc": "舌型描述",
    "shexinName": "舌型類型",
    "sport": "運動保健",
    "symptom": "症狀名稱",
    "symptomDesc": "症狀解釋",
    "taiseConfidence": "苔色置信度",
    "taiseDesc": "苔色描述",
    "taiseName": "苔色類型",
    "taizhiConfidence": "苔質置信度",
    "taizhiDesc": "苔質描述",
    "taizhiName": "苔質類型",
    "tonguePicAddr": "標記圖片地址",
    "typeConfidence": "體質置信度",
    "typeId": "體質類型",
    "typeName": "體質類型",
    "uid": "uid",
    "uploadPath": "原圖圖片地址",
    "xinzang": "心臟是否異常,0-否，1-是",
    "xinzangDesc": "心臟描述",
    "xinzangMean": "心臟診斷意義",
    "yuban": "是否有瘀斑,0-否，1-是",
    "yubanDesc": "瘀斑描述",
    "yubanMean": "瘀斑診斷意義",
    "yudian": "是否有瘀點,0-否，1-是",
    "yudianDesc": "瘀點描述",
    "yudianMean": "瘀點診斷意義",
    "zhengxing": "中醫證型",
    "zhengxingDesc": "中醫證型描述",
    "zigon": "子宮是否異常,0-否，1-是",
    "zigonDesc": "子宮描述",
    "zigonMean": "子宮診斷意義",
    "meta": "元信息，包括狀態碼和返回消息",
    "code": "狀態碼",
    "msg": "返回消息"
}
