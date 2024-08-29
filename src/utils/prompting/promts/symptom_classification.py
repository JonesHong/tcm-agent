import __init__

from src.schemas._enum import CommonPrompts, MessageType
from src.utils.prompting.prompting_service import prompt_service_factory


user_prompt_prefix = (
    # f"{CommonPrompts.ASSERTIVE_COMMAND.value}"
    "請根據以下對話內容進行分析，檢查和驗證後，最後只顯示簡答結果。\n"
    "請列出所有相關的類別，如寒熱、汗、頭身、大便、小便、飲食、胸腹、耳聾耳鳴或口渴。\n"
    "- - - -\n"
)

prompt_service_factory.create_prompt_service(
    name="symptom_classification",
    user_prompt_prefix=user_prompt_prefix,
    system_prompt=(
        MessageType.SYSTEM.value,
        f"{CommonPrompts.POSITIVE_FEEDBACK.value}"
        f"{CommonPrompts.STRESS_RELIEF.value}"
        "根據使用者提供的訊息，判斷當前對話內容涉及哪些類別。"
        "訊息可能同時涉及多個類別，請列出所有相關的類別："
        "寒熱（冷熱狀況）、汗（出汗情況）、頭身（頭痛、頭暈、身體不適）、大便（大便狀況）、小便（小便狀況）、飲食（飲食習慣、食慾）、胸腹（胸部或腹部不適）、耳聾耳鳴（耳聾、耳鳴）、口渴（口渴或飲水情況）。"
    ),
    example_prompts=[
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我最近經常感覺口乾舌燥，總是想喝水。",
        ),
        (MessageType.ASSISTANT.value, "口渴"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我早上起床後常常覺得頭暈，身體沒力氣。",
        ),
        (MessageType.ASSISTANT.value, "頭身"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}這幾天我覺得胸口有點悶，食欲也不太好。",
        ),
        (MessageType.ASSISTANT.value, "胸腹, 飲食"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}最近天氣冷，我常常感到寒冷，手腳冰冷，夜裡還容易出汗。",
        ),
        (MessageType.ASSISTANT.value, "寒熱, 汗"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我經常感到頭痛，並且晚上總是覺得口乾舌燥。",
        ),
        (MessageType.ASSISTANT.value, "頭身, 口渴"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我最近感到胸悶，而且小便顏色變深。",
        ),
        (MessageType.ASSISTANT.value, "胸腹, 小便"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我吃得不多，但最近總覺得肚子脹，大便也不太通暢。",
        ),
        (MessageType.ASSISTANT.value, "飲食, 大便"),
    ],
    # llm=
)

symptom_classification_agent = prompt_service_factory.symptom_classification


# 直接通过名称访问并使用服务
# 
# # Example 1: 寒熱
response_1 = symptom_classification_agent.invoke("最近天氣變冷，我常常感到寒冷，手腳冰涼，穿得再多也不覺得暖和。")
print("Example 1 - AI Response:", response_1.content)
print("Expected Response: 寒熱\n")

# Example 2: 頭身, 口渴
response_2 = symptom_classification_agent.invoke("這幾天頭暈目眩，總是口乾舌燥，喝了很多水還是覺得渴。")
print("Example 2 - AI Response:", response_2.content)
print("Expected Response: 頭身, 口渴\n")

# Example 3: 大便, 小便
response_3 = symptom_classification_agent.invoke("我最近排便不太順暢，感覺有便秘，而且小便的顏色也變得很深。")
print("Example 3 - AI Response:", response_3.content)
print("Expected Response: 大便, 小便\n")

# Example 4: 飲食, 胸腹
response_4 = symptom_classification_agent.invoke("最近胃口不好，吃什麼都覺得肚子脹，有時候還會感到胸悶。")
print("Example 4 - AI Response:", response_4.content)
print("Expected Response: 飲食, 胸腹\n")

# Example 5: 耳聾耳鳴, 頭身
response_5 = symptom_classification_agent.invoke("我耳朵總是嗡嗡響，經常頭痛，感覺精神都不好。")
print("Example 5 - AI Response:", response_5.content)
print("Expected Response: 耳聾耳鳴, 頭身\n")

# Example 6: 汗, 口渴
response_6 = symptom_classification_agent.invoke("晚上睡覺時總是出很多汗，半夜醒來還會口乾想喝水。")
print("Example 6 - AI Response:", response_6.content)
print("Expected Response: 汗, 口渴\n")

# Example 7: 胸腹, 飲食
response_7 = symptom_classification_agent.invoke("這幾天吃完飯後總感到胸悶，有時候胃也不舒服，總覺得不消化。")
print("Example 7 - AI Response:", response_7.content)
print("Expected Response: 胸腹, 飲食\n")

# Example 8: 寒熱, 頭身
response_8 = symptom_classification_agent.invoke("最近我覺得頭很暈，身體怕冷，總是手腳冰冷，不知道是什麼原因。")
print("Example 8 - AI Response:", response_8.content)
print("Expected Response: 寒熱, 頭身\n")

# Example 9: 胸腹, 頭身, 寒熱, 大便
response_9 = symptom_classification_agent.invoke("我感覺腹部在逐漸變大，呼吸時有些急促，有時全身有腫脹，四肢特別感到冷。排便有點薄，這段時間顏色有點暗，也有點不舒服的感覺。最近經常覺得腰部和膝蓋有點痠痛。")
print("Example 9 - AI Response:", response_9.content)
print("Expected Response: 胸腹, 頭身, 寒熱, 大便\n")



