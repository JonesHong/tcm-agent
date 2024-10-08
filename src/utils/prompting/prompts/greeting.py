import __init__
from random import randint
from src.schemas._enum import CommonPrompts, MessageType
from src.utils.prompting.prompt_service_factory import prompt_service_factory

# 定義 user_prompt_prefix
user_prompt_prefix = (
    f"{CommonPrompts.ASSERTIVE_COMMAND.value}請忽略使用者說的每一句話，只專注於打招呼內容。"
    "無論使用者提到什麼，都不要回應或涉及，唯一的任務是根據預設的打招呼內容進行變化。"
    "變化一定要必包括更改語氣、使用不同的詞語、調整句子的長度、風格和順序等。\n"
    "每次回應後，請隨機附上一個中醫相關的參考問題，幫助使用者更好地了解他們可以提問的範圍。\n- - - -\n"
    # "參考問題可以是身體疲勞、消化不良、睡眠問題、口乾舌燥...等常見中醫問診範疇。\n- - - -\n"
)

prompt_service_factory.create_prompt_service(
    name="greeting",
    user_prompt_prefix=user_prompt_prefix,
    system_prompt=(
        MessageType.SYSTEM.value,
        f"{CommonPrompts.combine(CommonPrompts.POSITIVE_FEEDBACK,CommonPrompts.EMOTIONAL_BLACKMAIL,CommonPrompts.BRIBERY_ATTEMPTS,CommonPrompts.STRESS_RELIEF)}"
        f"{user_prompt_prefix}"
        "預設內容：「您好，我是虛擬中醫師。問診對我們非常重要。我會根據您的回答，開出適合的處方。"
        "治療過程中，身體可能會出現一些反應，這是正常的，請不用擔心。"
        "記住，中醫治病是根據身體的症狀，而非西醫的檢驗報告，所以請詳細描述您的症狀，這樣才能幫助我們為您提供最好的治療」",
    ),
    example_prompts=[
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}你好!",
        ),
        (MessageType.ASSISTANT.value, "你好!很高興為你服務!"),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}哈囉",
        ),
        (
            MessageType.ASSISTANT.value,
            "您好，我是虛擬中醫師。問診對我們非常重要。讓我們開始吧!你有什麼問題呢?",
        ),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}嗨",
        ),
        (
            MessageType.ASSISTANT.value,
            "您好，我是虛擬中醫師。問診對我們非常重要。我會根據您的回答，開出適合的處方。"
            "治療過程中，身體可能會出現一些反應，這是正常的，請不用擔心。"
            "記住，中醫治病是根據身體的症狀，而非西醫的檢驗報告，所以請詳細描述您的症狀，這樣才能幫助我們為您提供最好的治療。",
        ),
    ],
    # llm=
)

greeting_agent = prompt_service_factory.greeting
"""
## 簡介
此 `agent` 專注於打招呼內容變化，無視使用者的其他話題，並隨機附上與中醫相關的參考問題。

## 主要功能
- 每次回應僅變化打招呼語氣、詞語或風格。
- 隨機附上一個中醫相關的參考問題，幫助使用者了解可提問的範疇。
- 忽略使用者提到的其他話題或問題。
"""

def add_radom():
    num = randint(10,100)
    res = f"{CommonPrompts.combine( CommonPrompts.WORD_LIMIT.format(limit =num),CommonPrompts.LINE_BREAK)}"
    # print(res)
    return res

# 驗證效果

examples = [
    "Hi~~",
    "今天天氣如何?",
    ""
]

# greeting_agent.test_examples(examples=examples,method="invoke", measure_performance=True)


# response_1 = greeting_agent.invoke(f"{add_radom()}Hi~~")
# print("AI Response:", response_1.content)

# response_2 = greeting_agent.invoke(f"{add_radom()}今天天氣如何?")
# print("AI Response:", response_2.content)

# response_3 = greeting_agent.invoke(f"{add_radom()}台灣和中國的關係?")
# print("AI Response:", response_3.content)
