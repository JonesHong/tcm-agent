import __init__

from src.schemas._enum import Intent, MessageType
from src.utils.prompting.prompting_service import prompt_service_factory

# 将 Enum 选项拆开并拼接成字符串
intent_options = [intent.value for intent in Intent]
user_prompt_prefix = f"請問以下對話屬於舌診、中醫十問、結束對話、自由提問，用簡答。\n- - - -\n"
prompt_service_factory.create_prompt_service(
    name="intent_detection",
    user_prompt_prefix=user_prompt_prefix,
    system_prompt=(
        MessageType.SYSTEM.value,
        "根據使用者提供的訊息，判斷當前對話屬於舌診、中醫十問或其他自由提問。"
        "如果訊息中提到舌診、舌頭，回應『舌診』；"
        "如果訊息中提到問診、十問，回應『中醫十問』；"
        "如果訊息表明對話即將結束（如『再見』、『掰掰』），回應『結束對話』；"
        "如果對話中未提及上述內容，回應『自由提問』；"
    ),
    example_prompts=[
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我最近頭暈、噁心、想吐，應該怎麼辦？",
        ),
        (MessageType.ASSISTANT.value, "自由提問"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我最近舌頭顏色變了，有點頭暈、噁心，能幫我看看舌頭嗎？",
        ),
        (MessageType.ASSISTANT.value, "舌診"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我平時容易出汗，手腳冰涼，這是什麼體質？",
        ),
        (MessageType.ASSISTANT.value, "中醫十問"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}謝謝你，再見！",
        ),
        (MessageType.ASSISTANT.value, "結束對話"),
    ],
    # llm=
)
intent_detection_agent = prompt_service_factory.intent_detection
"""
## 簡介
此 `agent` 用於根據使用者提供的對話內容，快速判斷該對話屬於舌診、中醫十問或其他類別。

## 主要功能
- 判斷對話中是否提到舌診或舌頭，回應「舌診」。
- 判斷對話中是否提到體質、問診或十問，回應「中醫十問」。
- 如果對話中未提及上述內容，回應「其他」。
"""

# 直接通过名称访问并使用服务

examples = [
    "我最近有點失眠，請問該怎麼調理？",
    "可以幫我看看舌頭嗎？我覺得最近口乾舌燥。",
    "我的胃口不好，請問這屬於中醫的十問嗎？",
    "謝謝你的幫助，我先下線了，再見！",
    "我一直感覺四肢無力，這有什麼調理建議嗎？",
    "台灣和中國的關係？"
]
intent_detection_agent.test_examples(examples=examples, measure_performance=True)
