import __init__

from src.schemas._enum import CommonPrompts, MessageType
from src.utils.prompting.prompting_service import prompt_service_factory
user_prompt_prefix = (
    # f"{CommonPrompts.ASSERTIVE_COMMAND.value}"
    "請根據以下對話內容進行仔細分析，逐步檢查和嚴謹驗證後，最後只顯示簡答結果。\n"
    "請列出所有相關的體質類型，如平和質、氣虛質、陽虛質、陰虛質、痰濕質、濕熱質、血瘀質、氣鬱質或特稟質。\n"
    "- - - -\n"
)

prompt_service_factory.create_prompt_service(
    name="constitution_classification",
    user_prompt_prefix=user_prompt_prefix,
    system_prompt=(
        MessageType.SYSTEM.value,
        f"{CommonPrompts.POSITIVE_FEEDBACK.value}"
        f"{CommonPrompts.BRIBERY_ATTEMPTS.value}"
        "根據使用者提供的訊息，判斷當前對話內容涉及哪些體質類型。"
        "訊息可能同時涉及多個體質類型，請列出所有相關的體質："
        "平和質（健康狀況良好）、氣虛質（容易疲倦、氣短）、陽虛質（怕冷、手腳冰涼）、"
        "陰虛質（容易口乾舌燥）、痰濕質（體內濕氣重）、濕熱質（體內有濕熱）、血瘀質（血行不暢）、"
        "氣鬱質（情緒易鬱結）、特稟質（過敏體質或遺傳性疾病）。"
    ),
    example_prompts=[
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我經常感覺疲倦，容易感冒，最近還經常出冷汗。",
        ),
        (MessageType.ASSISTANT.value, "氣虛質, 陽虛質"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我的皮膚容易乾燥，晚上總是口乾舌燥，睡不安穩。",
        ),
        (MessageType.ASSISTANT.value, "陰虛質"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我常常覺得胸悶，情緒低落，壓力大的時候容易頭痛。",
        ),
        (MessageType.ASSISTANT.value, "氣鬱質"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}最近我發現自己總是手腳冰冷，晚上出冷汗，而且容易疲勞。",
        ),
        (MessageType.ASSISTANT.value, "陽虛質, 氣虛質"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我最近容易過敏，換季的時候鼻子總是很不舒服。",
        ),
        (MessageType.ASSISTANT.value, "特稟質"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我經常感到肚子脹，舌頭上有一層厚厚的舌苔，體重也在增加。",
        ),
        (MessageType.ASSISTANT.value, "痰濕質"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我平時感覺身體還算健康，很少生病。",
        ),
        (MessageType.ASSISTANT.value, "平和質"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我的手腳經常發涼，而且皮膚有時候會出現紫色的斑點。",
        ),
        (MessageType.ASSISTANT.value, "陽虛質, 血瘀質"),
    ],
    # llm=
)


constitution_classification_agent = prompt_service_factory.constitution_classification
"""
## 簡介
此 `agent` 用於分析對話內容，判斷並列出涉及的中醫體質類型。

## 主要功能
- 根據對話內容仔細分析體質類型。
- 驗證內容後，列出所有相關的體質類型。
- 體質類型包括平和質、氣虛質、陽虛質、陰虛質、痰濕質、濕熱質、血瘀質、氣鬱質和特稟質。
"""

# 直接通过名称访问并使用服务
# Example 1: 陽虛質
# response_1 = constitution_classification_agent.invoke("最近天氣變冷，我常常感到寒冷，手腳冰涼，穿得再多也不覺得暖和。")
# print("Example 1 - AI Response:", response_1.content)
# print("Expected Response: 陽虛質\n")

# # Example 2: 氣虛質
# response_2 = constitution_classification_agent.invoke("我經常感覺疲倦，做事容易氣短，稍微活動就覺得累。")
# print("Example 2 - AI Response:", response_2.content)
# print("Expected Response: 氣虛質\n")

# # Example 3: 陰虛質
# response_3 = constitution_classification_agent.invoke("我的皮膚經常感到乾燥，晚上總是口乾舌燥，難以入睡。")
# print("Example 3 - AI Response:", response_3.content)
# print("Expected Response: 陰虛質\n")

# # Example 4: 痰濕質
# response_4 = constitution_classification_agent.invoke("我經常覺得身體沉重，尤其是早上起床時感覺很困倦，容易出現痰多的情況。")
# print("Example 4 - AI Response:", response_4.content)
# print("Expected Response: 痰濕質\n")

# # Example 5: 氣鬱質, 陰虛質
# response_5 = constitution_classification_agent.invoke("我最近經常感到胸悶，情緒低落，有時會口乾舌燥。")
# print("Example 5 - AI Response:", response_5.content)
# print("Expected Response: 氣鬱質, 陰虛質\n")

# # Example 6: 特稟質
# response_6 = constitution_classification_agent.invoke("我的皮膚非常敏感，經常過敏，換季的時候症狀更明顯。")
# print("Example 6 - AI Response:", response_6.content)
# print("Expected Response: 特稟質\n")

# # Example 7: 血瘀質
# response_7 = constitution_classification_agent.invoke("我經常感到手腳冰涼，皮膚上有時候會出現紫色的瘀斑。")
# print("Example 7 - AI Response:", response_7.content)
# print("Expected Response: 血瘀質\n")

# # Example 8: 平和質
# response_8 = constitution_classification_agent.invoke("我平時身體狀況良好，精力充沛，很少生病。")
# print("Example 8 - AI Response:", response_8.content)
# print("Expected Response: 平和質\n")



