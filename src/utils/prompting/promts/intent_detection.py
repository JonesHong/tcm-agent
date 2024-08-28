import __init__

from src.schemas._enum import MessageType
from src.utils.prompting.prompting_service import prompt_service_factory


user_prompt_prefix="請問以下對話屬於舌診、中醫十問或是其他，用簡答。\n- - - -\n"
prompt_service_factory.create_prompt_service(
    name="intent_detection",
    user_prompt_prefix=user_prompt_prefix,
    system_prompt=(
        MessageType.SYSTEM.value,
        "根據使用者提供的訊息，判斷當前對話屬於舌診、中醫十問或其他中醫相關提問。"
        "如果訊息中提到舌診、舌頭，回應『舌診』；"
        "如果訊息中提到體質、問診、十問，回應『中醫十問』；"
        "如果訊息中沒有提及上述內容，回應『其他』。",
    ),
    example_prompts=[
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我最近頭暈、噁心、想吐，應該怎麼辦？",
        ),
        (MessageType.ASSISTANT.value, "其他"),
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
    ],
    # llm=
)
intent_detection_agent = prompt_service_factory.intent_detection
# 直接通过名称访问并使用服务
response = intent_detection_agent.invoke("我月經已經三個月沒來了，我是更年期了嗎")
print("AI Response:", response.content)