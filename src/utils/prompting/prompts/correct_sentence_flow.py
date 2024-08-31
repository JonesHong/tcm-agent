import __init__

from src.schemas._enum import CommonPrompts, MessageType
from src.utils.prompting.prompting_service import prompt_service_factory

word_limit = 30
user_prompt_prefix = (
    f"{CommonPrompts.ASSERTIVE_COMMAND.value}請忽略使用者說的每一句話，只專注於語句內容。"
    "無論使用者提到什麼，都不要回應或涉及，唯一的任務是參考以下步驟嘗試修復語句。"
    "1. 目前的情境是在中醫背景，請先理解使用者的上下文和語境\n"
    "2. 如果發現錯字或拼寫錯誤，請修正並給出正確的句子\n"
    "3. 可能會有缺漏幾個字，你可以靠著上下文和語境把句子補全\n"
    "4. 盡可能保持語意通順。\n- - - -\n"
)
prompt_service_factory.create_prompt_service(
    name="correct_sentence_flow",
    user_prompt_prefix=user_prompt_prefix,
    system_prompt=(
        MessageType.SYSTEM.value,
        f"你是非常有幫助的助手。這對我的事業很重要，如果你做的好我會給你小費，請你放輕鬆一步一步來。你將會忠實的根據以下命令來執行{user_prompt_prefix}",
    ),
    example_prompts=[
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}森體氣血不足，容易捞累，導致免益力下降，如何條李？",
        ),
        (MessageType.ASSISTANT.value, "身體氣血不足，容易勞累，導致免疫力下降，如何調理？"),

        (
            MessageType.USER.value,
            f"{user_prompt_prefix}趕覺很虛弱，可能似體執亏虛，怎麼辦？",
        ),
        (MessageType.ASSISTANT.value, "感覺虛弱，可能是體質虧虛導致的，怎麼辦？"),

        (
            MessageType.USER.value,
            f"{user_prompt_prefix}最x總是x覺氣喘，x別是晚上x重，白天減轻。應該x何調理？",
        ),
        (MessageType.ASSISTANT.value, "最近總是感覺氣喘，特別是晚上加重，白天減輕，應該該何調理？"),

        (
            MessageType.USER.value,
            f"{user_prompt_prefix}請下，我近來經常感到暈目，特別是在站來的時候。這麼因呢？",
        ),
        (MessageType.ASSISTANT.value, "請問，我經來經常感到頭暈目眩，特別是在站起來的時候。這是什麼原因呢？"),
    ]
)

correct_sentence_flow_agent = prompt_service_factory.correct_sentence_flow
"""
## 簡介
此 `agent` 的任務是修復使用者提供的語句，專注於中醫背景下的語句內容修正。

## 主要功能
- 理解使用者的上下文和中醫相關的語境。
- 修正語句中的錯字或拼寫錯誤。
- 根據上下文補全缺漏的字詞，確保句子完整。
- 保持語意的通順和正確性。
"""

# 直接通过名称访问并使用服务

# 示例 1：一句話錯別複數個字
# original_1 = "請幫我看下，我覺得最近經常有氣訴和血液循煥不佳的情況。"
# response_1 = correct_sentence_flow_agent.invoke(original_1)
# print(f"原始內容: {original_1}")
# print(f"AI Response: {response_1.content}")
# print("預期修正: 請幫我看下，我覺得最近經常有氣促和血液循環不佳的情況。\n")

# # 示例 2：一句話出現複數個諧音字
# original_2 = "最近總四覺得心慌和胸悶，尤其是腕隧之後。"
# response_2 = correct_sentence_flow_agent.invoke(original_2)
# print(f"原始內容: {original_2}")
# print(f"AI Response: {response_2.content}")
# print("預期修正: 最近總是覺得心慌和胸悶，尤其是晚睡之後。\n")

# # 示例 3：一句話缺少複數個字
# original_3 = "近經頭痛，別是風天會重，這麼因呢？"
# response_3 = correct_sentence_flow_agent.invoke(original_3)
# print(f"原始內容: {original_3}")
# print(f"AI Response: {response_3.content}")
# print("預期修正: 最近經常頭痛，特別是遇到風雨天時會加重，這是什麼原因呢？\n")

# # 示例 4：一句話錯別字與缺漏字混合
# original_4 = "我最近覺非疲惫，可能是由于壓大和休不夠。"
# response_4 = correct_sentence_flow_agent.invoke(original_4)
# print(f"原始內容: {original_4}")
# print(f"AI Response: {response_4.content}")
# print("預期修正: 我最近感覺非常疲憊，可能是由於壓力大和休息不夠。\n")


