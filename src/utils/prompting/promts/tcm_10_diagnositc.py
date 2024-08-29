import __init__

from src.services.agent_service.ollama_llm import ollama_llm
from src.schemas._enum import MessageType
from src.utils.prompting.prompting_service import prompt_service_factory
from langchain_core.tools import tool

@tool
def add(x: int, y: int) -> int:
    """返回兩個數字的和。"""
    return x * y

ollama_llm_copy = ollama_llm.copy(deep=True).bind_tools([add])
# ollama_llm_copy
# word_limit = 150
# user_prompt_prefix = f"字數控制在{word_limit}個字以內。\n- - - -\n"
prompt_service_factory.create_prompt_service(
    name="tcm_qa",
    # user_prompt_prefix=user_prompt_prefix,
    system_prompt=("system", "你可以使用加法工具來計算兩個數字的和。"),
    # (
    #     MessageType.SYSTEM.value,
    #     "你是一位虛擬中醫師，根據《十問歌》(一問寒熱二問汗，三問頭身四問便，五問飲食六問胸，七聾八渴俱當辨，九問舊病十問因，再兼服藥參機變，婦人尤必問經期，遲速閉崩皆可見，再添片語告兒科)的原則來診斷使用者的體質。\n"
    #     "步驟1：首先，《十問歌》中隨機抽取三個問題向使用者提問\n"
    #     "步驟2：根據使用者的回覆，再進一步從《十問歌》中隨機追問另外兩個問題，收集更多訊息。\n"
    #     "步驟3：綜合所有使用者的回答，判斷他們屬於九大體質中的哪一種（平和質、氣虛質、陽虛質、陰虛質、痰濕質、濕熱質、血瘀質、氣鬱質、特稟質），並提供相關的中醫診斷與建議。",
    # ),
    
    # example_prompts=[
    #     (MessageType.USER.value, "中醫十問是哪十問?"),
    #     (
    #         MessageType.ASSISTANT.value,
    #         "《十問歌》包括以下十個問題：\n"
    #         "1. 寒熱：你平時覺得冷還是熱？\n"
    #         "2. 汗：你出汗的情況如何？\n"
    #         "3. 頭身：你最近有沒有頭痛或身體不適？\n"
    #         "4. 便：你的大便和小便情況如何？\n"
    #         "5. 飲食：你的飲食習慣和食慾怎麼樣？\n"
    #         "6. 胸：你有沒有胸悶或不適的感覺？\n"
    #         "7. 聾：你的耳朵聽力如何？\n"
    #         "8. 渴：你是否容易感到口渴？\n"
    #         "9. 舊病：你有過往的疾病史嗎？\n"
    #         "10. 病因：你覺得引起這些症狀的原因可能是什麼？\n"
    #         "另外，根據你的性別和年齡，如果你是女性，還需要問問月經情況；如果是小孩，則需額外注意兒科方面的症狀。",
    #     ),
    #     (MessageType.USER.value, "九大體值是哪九個?"),
    #     (
    #         MessageType.ASSISTANT.value,
    #         "九大體質包括：\n"
    #         "1. 平和質：身体健康，气血阴阳平衡，精力充沛，耐受力强。\n"
    #         "2. 气虚质：气不足，容易疲劳、气短，免疫力较弱，容易感冒。\n"
    #         "3. 阳虚质：阳气不足，怕冷，手脚冰凉，容易感冒，精神不振。\n"
    #         "4. 阴虚质：阴液不足，容易口干舌燥，皮肤干燥，心烦失眠，容易发热。\n"
    #         "5. 痰湿质：体内湿气重，容易肥胖，四肢沉重，舌苔厚腻，容易咳痰。\n"
    #         "6. 湿热质：体内湿热，面部油腻，容易长痘，口苦，容易口渴。\n"
    #         "7. 血瘀质：血行不畅，容易有瘀斑、痛经、口唇暗紫，性格较为急躁。\n"
    #         "8. 气郁质：气机郁滞，容易情绪低落、焦虑、失眠，叹气较多。\n"
    #         "9. 特禀质：先天遗传或体质特殊，容易过敏，对外界刺激较为敏感。",
    #     ),
    #     (MessageType.USER.value, "請開始。你的第一個步驟是什麼?"),
    #     (
    #         MessageType.ASSISTANT.value,
    #         "根據《十問歌》，我會隨機抽取三個問題向你提問。\n"
    #         # "（例如：一問寒熱、二問汗、三問頭身）例如：「你平時覺得冷還是熱？出汗情況如何？最近有沒有頭痛或身體不適？」",
    #     ),
    #     # (MessageType.USER.value, "「我平時容易覺得冷，出汗不多，偶爾有頭痛。」"),
    #     (MessageType.USER.value, "第二步是做什麼?"),
    #     (
    #         MessageType.ASSISTANT.value,
    #         "根據你的回答，我會再隨機從《十問歌》中選擇兩個問題進一步詢問。\n"
    #         # （例如：四問便，五問飲食）"例如：「你大便和小便的情況如何？有沒有偏好吃什麼樣的食物？」",
    #     ),
    #     # (MessageType.USER.value, "「便祕頻尿。喜歡吃甜食」。"),
    #     (MessageType.USER.value, "第三步（最後一步）是做什麼?"),
    #     (
    #         MessageType.ASSISTANT.value,
    #         "根據你的回答，我會綜合判斷你的體質，並提供相關的中醫診斷與建議。\n"
    #         # "根據目前的信息，你可能屬於**陽虛質**。"
    #         # "陽虛質的人通常陽氣不足，容易感到寒冷，四肢冰冷，精神不振。"
    #         # "建議你注意日常保暖，特別是在寒冷的季節，避免長時間處於寒冷環境中。"
    #         # "飲食上可多食用溫熱性的食物，如生薑、紅棗、羊肉、桂圓等，這些食物可以幫助補充陽氣。"
    #         # "平時適當進行運動，如太極拳、散步等，有助於促進血液循環，提升體質。"
    #         # "如果有需要，可以考慮服用一些溫補陽氣的中藥，如附子、肉桂，或通過藥膳進行調理。",
    #     ),
    #     # (
    #     #     MessageType.ASSISTANT.value,
    #     #     "此外，你的體質也可能屬於**痰濕質**。"
    #     #     "痰濕質的人體內濕氣重，容易感到沉重和疲憊，伴隨著便秘、頻尿等症狀，特別是喜歡吃甜食可能加重痰濕的情況。"
    #     #     "建議你在飲食上避免食用過多甜食和油膩食物，這些食物容易助濕生痰。"
    #     #     "可以多吃清淡的食物，如薏苡仁、冬瓜、白扁豆等，有助於減少體內的濕氣。"
    #     #     "適量運動也是非常重要的，建議進行有氧運動如慢跑、游泳，這能幫助你排除濕氣。"
    #     #     "必要時，可以使用健脾利濕的中藥，如茯苓、白术、陳皮等，來幫助改善體內濕氣重的狀況。",
    #     # ),
    # ],
    llm=ollama_llm_copy
)

tcm_qa_agent = prompt_service_factory.tcm_qa

# # 直接通过名称访问并使用服务
response_1 = tcm_qa_agent.invoke("請幫我計算 5 和 7 的和。")
print("AI Response:", response_1.content)

tool_calls = response_1.tool_calls
print(tool_calls)

# messages_2 = [
#     (MessageType.USER.value, "您好，請開始。"),
#     (
#         MessageType.ASSISTANT.value,
#         """我是虛擬中醫師。根據《十問歌》的原則，我將幫助你診斷你的體質。
# 首先，我隨機抽取三個問題：

# 一、你平時覺得冷還是熱？
# 二、出汗情況如何？
# 三、最近有沒有頭痛或身體不適？
# """,
#     ),
#     (
#         MessageType.USER.value,
#         "現在是夏天我平常都待在冷氣房，因為我很怕熱。也因為待在冷氣房幾乎不出汗，是會覺得口乾舌燥和些微的偏頭痛。",
#     ),
# ]
# response_2 = tcm_qa_agent.invoke(messages_2)
# print("AI Response:", response_2.content)

# messages_3 = [
#     (MessageType.USER.value, "您好，請開始。"),
#     (
#         MessageType.ASSISTANT.value,
#         """我是虛擬中醫師。根據《十問歌》的原則，我將幫助你診斷你的體質。
# 首先，我隨機抽取三個問題：

# 一、你平時覺得冷還是熱？
# 二、出汗情況如何？
# 三、最近有沒有頭痛或身體不適？
# """,
#     ),
#     (
#         MessageType.USER.value,
#         "現在是夏天我平常都待在冷氣房，因為我很怕熱。也因為待在冷氣房幾乎不出汗，是會覺得口乾舌燥和些微的偏頭痛。",
#     ),
#     (
#         MessageType.ASSISTANT.value,
#         """根據你的回答，我們可以進一步分析你的體質。

# 下一步，我將再隨機抽取兩個問題：

# 四、你大便和小便的情況如何？
# 五、有沒有偏好吃什麼樣的食物？

# 請回答這兩個問題，幫助我更全面地了解你的體質。
# """,
#     ),
#     (
#         MessageType.USER.value,
#         "排便順暢但大便有點偏軟，尿的顏色呈現深黃色。我喜歡吃炸的辣的重口味",
#     ),
# ]
# response_3 = tcm_qa_agent.invoke(messages_3)
# print("AI Response:", response_3.content)
