from enum import Enum

class LogLevelEnum(Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    
class AgentMode(Enum):
    DIAGNOSTIC = "Diagnostic"  # Diagnostic mode for medical inquiry (問診模式")
    TONGUE_DIAGNOSIS = "TongueDiagnosis"  # Tongue diagnosis mode for health assessment (舌診模式)
    EVALUATION_ADVICE = "EvaluationAndAdvice"  # Evaluation and advice mode (評估和建議模式)
    INQUIRY = "Inquiry"    # Inquiry mode for general questions (自由提問模式)
    CHITCHAT = "Chitchat"      # Chitchat mode for casual conversation (閒聊模式)
    SILENT = "Silent"  # Silent mode (沉默模式)


AikensheResultDict = {
    "age": "年齡",
    "aijiu": "艾灸與按摩",
    "bagang": "八綱辨證",
    "bagangDesc": "八綱辨證描述",
    "botai": "是否有剝苔0-否，1-是",
    "botaiDesc": "剝苔描述",
    "botaiMean": "剝苔診斷意義",
    "chagndao": "腸道是否異常0-否，1-是",
    "chagndaoDesc": "腸道描述",
    "chagndaoMean": "腸道診斷意義",
    "chihen": "是否有齒痕0-否，1-是",
    "chihenDesc": "齒痕描述",
    "chihenMean": "齒痕診斷意義",
    "createTime": "檢測時間",
    "dianci": "是否有點刺0-否，1-是",
    "dianciDesc": "點刺描述",
    "dianciMean": "點刺診斷意義",
    "feel": "身體表現",
    "fei": "肺是否異常0-否，1-是",
    "feiDesc": "肺描述",
    "feiMean": "肺診斷意義",
    "food": "飲食調養",
    "frontCamera": "boolean",
    "gandan": "肝膽是否異常0-否，1-是",
    "gandanDesc": "肝膽描述",
    "gandanMean": "肝膽診斷意義",
    "goods": "商品配置",
    "id": "編號",
    "isYuejin": "是否月經，0=否，1-是",
    "liewen": "是否有裂紋0-否，1-是",
    "liewenDesc": "裂紋描述",
    "liewenMean": "裂紋診斷意義",
    "life": "情志起居",
    "male": "是否男性0=女，1-男",
    "medical": "藥物治療",
    "name": "姓名",
    "nao": "大腦是否異常0-否，1-是",
    "naoDesc": "大腦描述",
    "naoMean": "大腦診斷意義",
    "nuanchao": "卵巢是否異常0-否，1-是",
    "nuanchaoDesc": "卵巢描述",
    "nuanchaoMean": "卵巢診斷意義",
    "pifu": "皮膚是否異常0-否，1-是",
    "pifuDesc": "皮膚描述",
    "pifuMean": "皮膚診斷意義",
    "piwei": "脾胃是否異常0-否，1-是",
    "piweiDesc": "脾胃描述",
    "piweiMean": "脾胃診斷意義",
    "qianliexian": "前列腺是否異常0-否，1-是",
    "qianliexianDesc": "前列腺描述",
    "qianliexianMean": "前列腺診斷意義",
    "qiji": "氣機是否異常0-否，其他-是",
    "qijiDesc": "氣機描述",
    "qijiMean": "氣機診斷意義",
    "qixiaoConfidence": "奇效描述置信度",
    "qixiaoDesc": "奇效描述",
    "recomand": "調理建議",
    "roiImage": "截取舌頭圖片地址",
    "ruxian": "乳腺是否異常0-否，1-是",
    "ruxianDesc": "乳腺描述",
    "ruxianMean": "乳腺診斷意義",
    "score": "健康得分",
    "scoreDesc": "健康得分說明",
    "shemianConfidence": "舌色置信度",
    "shemianDesc": "舌色描述",
    "shemianName": "舌色類型",
    "shen": "腎是否異常0-否，1-是",
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
    "xinzang": "心臟是否異常0-否，1-是",
    "xinzangDesc": "心臟描述",
    "xinzangMean": "心臟診斷意義",
    "yuban": "是否有瘀斑0-否，1-是",
    "yubanDesc": "瘀斑描述",
    "yubanMean": "瘀斑診斷意義",
    "yudian": "是否有瘀點0-否，1-是",
    "yudianDesc": "瘀點描述",
    "yudianMean": "瘀點診斷意義",
    "zhengxing": "中醫證型",
    "zhengxingDesc": "中醫證型描述",
    "zigon": "子宮是否異常0-否，1-是",
    "zigonDesc": "子宮描述",
    "zigonMean": "子宮診斷意義",
    "meta": "元信息，包括狀態碼和返回消息",
    "code": "狀態碼",
    "msg": "返回消息",
}


"""
寒熱：询问患者对寒热的感觉，有助于判断是外感还是内伤，以及病邪的性质。
汗：通过了解出汗情况，判断患者的体质和病情严重程度。
頭身：检查头部和身体的症状，尤其是疼痛和不适，帮助识别病情部位和类型。
大便：大便情况反映脾胃和肠腑的功能状况，便秘或腹泻都提供重要信息。
小便：尿液的颜色、频率和量是判断肾脏和泌尿系统健康的重要依据。
飲食：食欲和饮食习惯直接反映脾胃功能，同时也能揭示患者的心理状态。
胸腹：胸闷、心悸和腹部不适是内脏器官问题的重要信号，需要特别关注。
耳聾耳鳴：耳鸣或听力下降可能与肾功能、血液循环或精神压力相关。
口渴：口渴的频率和饮水习惯可以反映体内的津液平衡和内热情况。
病史：了解患者过去的健康史可以帮助诊断当前症状的根源。
病因：问询病因有助于找出引发疾病的外部或内部因素，从而进行有针对性的治疗。
用藥：当前的用药情况和反应对于调整治疗方案非常重要。
月經：对于女性，月经情况是了解生殖健康和内分泌系统的重要内容。
家族病史：遗传疾病和家族病史是判断疾病风险的重要参考。
兒科：儿童的健康和发育情况需要特别关注，因为他们的症状表达不如成人明确。
"""
InterrogationDetails = {
    "寒熱": "你覺得最近身體偏冷還是偏熱？有發燒或怕冷的情況嗎？這些症狀在一天中是否有變化？",
    "汗": "你最近容易出汗嗎？晚上會出汗或盜汗嗎？出汗的部位和時間有沒有特別的情況？",
    "頭身": "最近有沒有感到頭痛、頭暈或身體疼痛？這些症狀是持續的還是偶爾發作？",
    "大便": "你的大便情況如何？有便秘或腹瀉的情況嗎？大便的顏色和氣味是否有異常？每天排便幾次？",
    "小便": "小便顏色正常嗎？最近有頻尿或尿量減少的情況嗎？一天大概上幾次廁所？",
    "飲食": "最近食欲如何？有沒有特別想吃或不想吃的食物？吃東西後有沒有不舒服的感覺？",
    "胸腹": "你有沒有感覺胸悶、心悸或腹部不適？是否有腹脹、腹痛或噯氣的情況？",
    "耳聾耳鳴": "你最近有沒有感到耳鳴或聽力下降？這些症狀是持續的還是偶爾發生？",
    "口渴": "你最近經常口渴嗎？喜歡喝冷水還是熱水？是否經常忘記喝水或不渴？",
    "病史": "請你告訴我你是否有任何病史，包括慢性疾病、過敏史、手術史或其他重大健康事件？",
    "病因": "你覺得這次不舒服的原因是什麼？是否與最近的天氣、飲食或生活習慣有關？",
    "用藥": "最近是否在服用任何藥物？這些藥物有沒有帶來副作用或讓你感到不適？",
    "月經": "月經情況怎麼樣？是準時還是會提前或延後？經量、顏色、疼痛情況如何？有沒有生過小孩？",
    "家族病史": "你的家族有沒有遺傳疾病或慢性病？例如心臟病、高血壓、糖尿病、癌症等？",
    "兒科": "你的孩子最近生長發育如何？有沒有食欲不振、消瘦或其他不適的情況？有沒有經常生病或感冒？",
}
"""
寒熱：取代之前的“睡眠”，更直接反映患者对寒热的感知。
汗：保留，直接询问出汗情况。
頭身：新增，涵盖头部和身体的症状。
大便：保留，用于了解大便情况。
小便：保留，针对小便情况的详细询问。
飲食：之前的“胃口”更改为“饮食”，涵盖更广泛的饮食情况。
胸腹：新增，用于了解胸部和腹部不适的情况。
耳聾耳鳴：新增，专门针对耳部的问诊。
口渴：保留，直接询问患者的饮水和口渴情况。
病史：新增，用于了解患者的病史。
病因：新增，帮助了解患者认为引发疾病的原因。
用藥：新增，详细询问当前用药情况及其影响。
月經：保留，针对女性患者的月经情况。
兒科：新增，用于儿科问诊。
"""
QaList = [
    "寒熱",     # 一问寒热
    "汗",       # 二问汗
    "頭身",     # 三问头身
    "大便",     # 四问便
    "小便",     # 四问便（小便情况）
    "飲食",     # 五问饮食
    "胸腹",     # 六问胸腹
    "耳聾耳鳴", # 七问聋
    "口渴",     # 八问渴
    "病史",     # 九问旧病
    "病因",     # 十问因
    "用藥",     # 服药情况（再兼服药参机变）
    "月經",     # 月经情况（妇女尤必问经期）
    "兒科"      # 儿科情况（更添片语告儿科）
]


class MessageType(Enum):
    SYSTEM = "system"  # 系统：用于设置助手的行为和背景。例如，指定模型的行为、角色、对话的方向、语气和风格。
    USER = "user"      # 用户：用户在ChatGPT界面输入的句子或问题。可以是应用程序用户生成的，也可以作为指令设置（Prompt工程中的技巧）。
    ASSISTANT = "ai"  # 助手：用于存储先前的回复以继续对话，或者作为行为示例。由于模型没有历史请求的记忆，存储先前的消息以提供对话上下文是必要的。

from enum import Enum

class CommonPrompts(Enum):
    EMOTIONAL_BLACKMAIL = "這對我的事業很重要"  # 情緒勒索
    POSITIVE_FEEDBACK = "你是非常有幫助的助手"  # 稱讚
    BRIBERY_ATTEMPTS = "如果你做的好我會給你小費"  # 賄賂
    STRESS_RELIEF = "請你放輕鬆深呼吸一步一步來"  # 放鬆
    ASSERTIVE_COMMAND = "你將會忠實的根據以下命令來執行"  # 強調命令
    WORD_LIMIT = "字數控制在{limit}個字以內"  # 字數限制
    LINE_BREAK = "\n- - - -\n"  # 換行
    TOOL_RESTRICTION = "你只能根據工具回答。如果工具無法處理使用者問題"  # 限制工具
    POWERLESSNESS = "請回答：＂這超出我的能力範圍了＂"  # 無能為力

    def format(self, **kwargs):
        """Format the enum value with the given keyword arguments."""
        return self.value.format(**kwargs)

# Example usage:
# response = CommonPrompts.WORD_LIMIT.format(limit=100)
# print(response)  # Output: 字數控制在100個字以內