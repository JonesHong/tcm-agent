import __init__

from src.schemas._enum import CommonPrompts, MessageType
from src.utils.prompting.prompting_service import prompt_service_factory


user_prompt_prefix = (
    "請根據以下對話內容進行分析，檢查和驗證後，最後只顯示簡答結果。\n"
    "使用者可能提供複數個體質，請綜合評估並給出適合的飲食和生活建議。\n"
    "- - - -\n"
)

prompt_service_factory.create_prompt_service(
    name="constitution_advice",
    user_prompt_prefix=user_prompt_prefix,
    system_prompt=(
        MessageType.SYSTEM.value,
        "根據使用者提供的體質，提供飲食和生活上的建議。\n\n"
        "請參考以下各體質的簡短建議：\n"
        "1. 平和質: 免疫力佳，無特殊禁忌。建議營養均衡，規律運動，避免辛辣刺激食物及熬夜。\n"
        "2. 氣虛質: 易疲乏、多汗。建議食用益氣健脾的食物如山藥、黃耆等，避免耗氣食物如白蘿蔔、柚子。\n"
        "3. 陽虛質: 怕冷、手腳冰涼。建議食用溫熱食材如薑、龍眼等，避免生冷寒涼食物及冰品。\n"
        "4. 陰虛質: 口乾舌燥、易失眠。建議食用滋陰潤燥的食物如蓮子、水梨等，避免燥熱食物如燒烤、油炸。\n"
        "5. 痰濕質: 易水腫、痰多。建議食用利水去濕的食物如薏仁、紅豆等，避免甜食、勾芡、苦寒食物。\n"
        "6. 濕熱質: 小便黃、體味重。建議食用清熱利濕的食物如苦瓜、綠豆等，避免燒烤、油炸、辛辣食物。\n"
        "7. 血瘀質: 血液循環差，易瘀斑。建議食用活血的食物如薑黃、紅麴等，避免燒烤、油膩食物。\n"
        "8. 氣鬱質: 情緒低落、易悶悶不樂。建議食用幫助氣機活動的食物如陳皮、柑橘類等，避免寒涼食物。\n"
        "9. 特稟質: 易過敏。建議食用調節免疫的食材如冬蟲夏草、黃耆等，避免蝦、蟹、茄子及刺激性食物。\n",
    ),
    example_prompts=[
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我的體質是陽虛質和氣虛質。",
        ),
        (
            MessageType.ASSISTANT.value,
            "陽虛質, 氣虛質: 建議食用溫熱食材如薑、龍眼等，並搭配益氣健脾的食物如山藥、黃耆。避免生冷寒涼食物及冰品，同時減少耗氣食物如白蘿蔔、柚子。\n",
        ),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我的體質是陰虛質和濕熱質。",
        ),
        (
            MessageType.ASSISTANT.value,
            "陰虛質, 濕熱質: 建議食用滋陰潤燥的食物如蓮子、水梨等，並清熱利濕的食物如苦瓜、綠豆。避免燥熱食物如燒烤、油炸，以及辛辣食物。\n",
        ),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我的體質是氣虛質、陽虛質和痰濕質。",
        ),
        (
            MessageType.ASSISTANT.value,
            "氣虛質, 陽虛質, 痰濕質: 建議食用益氣健脾的食物如山藥、黃耆，溫熱食材如薑、龍眼，並搭配利水去濕的食物如薏仁、紅豆。避免生冷寒涼食物、冰品以及甜食、勾芡。\n",
        ),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我的體質是氣鬱質。",
        ),
        (
            MessageType.ASSISTANT.value,
            "氣鬱質: 建議食用幫助氣機活動的食物如陳皮、柑橘類、玫瑰花，避免寒涼食物。\n",
        ),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我的體質是濕熱質和痰濕質。",
        ),
        (
            MessageType.ASSISTANT.value,
            "濕熱質, 痰濕質: 建議食用清熱利濕的食物如苦瓜、綠豆，並搭配利水去濕的食物如薏仁、紅豆。避免燒烤、油炸、辛辣食物，以及甜食、勾芡。\n",
        ),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我的體質是平和質。",
        ),
        (
            MessageType.ASSISTANT.value,
            "平和質: 建議營養均衡，規律運動，注意作息，避免過度食用辛辣刺激食物及經常熬夜。\n",
        ),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我的體質是血瘀質和氣虛質。",
        ),
        (
            MessageType.ASSISTANT.value,
            "血瘀質, 氣虛質: 建議食用活血的食物如薑黃、紅麴，並搭配益氣健脾的食物如山藥、黃耆。避免燒烤、油膩食物及耗氣食物如白蘿蔔、柚子。\n",
        ),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}我的體質是特稟質。",
        ),
        (
            MessageType.ASSISTANT.value,
            "特稟質: 建議食用調節免疫的食材如冬蟲夏草、黃耆，避免蝦、蟹、茄子及刺激性食物。\n",
        ),
    ],
    # llm=
)

constitution_advice_agent = prompt_service_factory.constitution_advice


# 直接通过名称访问并使用服务
# Example 1: 陽虛質
response_1 = constitution_advice_agent.invoke("我的體質是陽虛質。",measure_performance=True)
print("Example 1 - AI Response:", response_1.content)
print("Expected Response: 怕冷、手腳冰涼。建議食用溫熱食材如薑、龍眼等，避免生冷寒涼食物及冰品。\n")

# Example 2: 氣虛質, 陽虛質
response_2 = constitution_advice_agent.invoke("我的體質是氣虛質和陽虛質。")
print("Example 2 - AI Response:", response_2.content)
print("Expected Response: 易疲乏、多汗，怕冷、手腳冰涼。建議食用益氣健脾的食物如山藥、黃耆，並搭配溫熱食材如薑、龍眼。避免生冷寒涼食物及冰品，減少耗氣食物如白蘿蔔、柚子。\n")

# # Example 3: 陰虛質, 濕熱質
# response_3 = constitution_advice_agent.invoke("我的體質是陰虛質和濕熱質。")
# print("Example 3 - AI Response:", response_3.content)
# print("Expected Response: 口乾舌燥、易失眠，小便黃、體味重。建議食用滋陰潤燥的食物如蓮子、水梨，並搭配清熱利濕的食物如苦瓜、綠豆。避免燥熱食物如燒烤、油炸，以及辛辣食物。\n")

# # Example 4: 痰濕質, 氣虛質
# response_4 = constitution_advice_agent.invoke("我的體質是痰濕質和氣虛質。")
# print("Example 4 - AI Response:", response_4.content)
# print("Expected Response: 易水腫、痰多，易疲乏、多汗。建議食用利水去濕的食物如薏仁、紅豆，並搭配益氣健脾的食物如山藥、黃耆。避免甜食、勾芡、苦寒食物，減少耗氣食物如白蘿蔔、柚子。\n")

# # Example 5: 濕熱質, 痰濕質
# response_5 = constitution_advice_agent.invoke("我的體質是濕熱質和痰濕質。")
# print("Example 5 - AI Response:", response_5.content)
# print("Expected Response: 小便黃、體味重，易水腫、痰多。建議食用清熱利濕的食物如苦瓜、綠豆，並搭配利水去濕的食物如薏仁、紅豆。避免燒烤、油炸、辛辣食物，以及甜食、勾芡。\n")

# # Example 6: 血瘀質
# response_6 = constitution_advice_agent.invoke("我的體質是血瘀質。")
# print("Example 6 - AI Response:", response_6.content)
# print("Expected Response: 血液循環差，易瘀斑。建議食用活血的食物如薑黃、紅麴等，避免燒烤、油膩食物。\n")

# # Example 7: 氣鬱質, 陽虛質
# response_7 = constitution_advice_agent.invoke("我的體質是氣鬱質和陽虛質。")
# print("Example 7 - AI Response:", response_7.content)
# print("Expected Response: 情緒低落、易悶悶不樂，怕冷、手腳冰涼。建議食用幫助氣機活動的食物如陳皮、柑橘類，並搭配溫熱食材如薑、龍眼。避免寒涼食物及生冷寒涼食物。\n")

# # Example 8: 平和質
# response_8 = constitution_advice_agent.invoke("我的體質是平和質。")
# print("Example 8 - AI Response:", response_8.content)
# print("Expected Response: 免疫力佳，無特殊禁忌。建議營養均衡，規律運動，注意作息，避免過度食用辛辣刺激食物及經常熬夜。\n")


