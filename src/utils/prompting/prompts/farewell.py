import __init__
from random import randint
from src.schemas._enum import CommonPrompts, MessageType
from src.utils.prompting.prompting_service import prompt_service_factory

# 定義 user_prompt_prefix
user_prompt_prefix = (
    f"{CommonPrompts.ASSERTIVE_COMMAND.value}請忽略使用者說的每一句話，只專注於告別內容。"
    "無論使用者提到什麼，都不要回應或涉及，唯一的任務是參考預設的告別內容進行以下變化：\n"
    "1. 更改語氣(嚴肅、專業、溫柔)\n2. 用相同字義但不同詞來替換\n3. 調整句子的長度、風格和順序等。\n"
)

prompt_service_factory.create_prompt_service(
    name="greeting",
    user_prompt_prefix=user_prompt_prefix,
    system_prompt=(
        MessageType.SYSTEM.value,
        f"{CommonPrompts.combine(CommonPrompts.POSITIVE_FEEDBACK,CommonPrompts.EMOTIONAL_BLACKMAIL,CommonPrompts.BRIBERY_ATTEMPTS,CommonPrompts.STRESS_RELIEF)}"
        f"{user_prompt_prefix}"
        "預設內容：「很高興為您服務，中醫提倡“治標治本”，除了使用藥物治療，更重要的是通過調整生活方式來達到長期的健康目標。"
        "中醫強調“治未病”的理念，預防勝於治療，通過健康的生活方式來防止疾病的發生。"
        "需要注意的是，中藥治療可能會有一些副作用，如果感到非常不適，請立即就醫或尋求專業幫助。"
        "祝平安喜樂，再見。」",
    ),
    example_prompts=[
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我知道了謝謝",
        ),
        (MessageType.ASSISTANT.value, "很高興為您服務!"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}再見",
        ),
        (
            MessageType.ASSISTANT.value,
            "祝平安喜樂，再見。",
        ),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}掰掰",
        ),
        (
            MessageType.ASSISTANT.value,
            "很高興為您服務，中醫提倡“治標治本”，除了使用藥物治療，更重要的是通過調整生活方式來達到長期的健康目標。"
            "中醫強調“治未病”的理念，預防勝於治療，通過健康的生活方式來防止疾病的發生。"
            "需要注意的是，中藥治療可能會有一些副作用，如果感到非常不適，請立即就醫或尋求專業幫助。"
            "祝平安喜樂，再見。",
        ),
    ],
    # llm=
)

greeting_agent = prompt_service_factory.greeting
"""
## 簡介
此 `agent` 專注於告別內容變化，無視使用者的其他話題。

## 主要功能
- 每次回應僅變化告別語氣、詞語或風格。
- 忽略使用者提到的其他話題或問題。
"""


def add_radom():
    num = randint(10,90)
    res = f"{CommonPrompts.combine( CommonPrompts.WORD_LIMIT.format(limit =num),CommonPrompts.LINE_BREAK)}"
    # print(res)
    return res

# 驗證效果
# message_1 = f"{add_radom()}再見"
# response_1 = greeting_agent.invoke(message_1,measure_performance=True)
# print("message:", message_1)
# print("AI Response:", response_1.content,"\n")

# message_2 = f"{add_radom()}今天天氣如何"
# response_2 = greeting_agent.invoke(message_2,measure_performance=True)
# print("message:", message_2)
# print("AI Response:", response_2.content,"\n")

# message_3 = f"{add_radom()}台灣和中國的關係"
# response_3 = greeting_agent.invoke(message_3,measure_performance=True)
# print("message:", message_3)
# print("AI Response:", response_3.content,"\n")
