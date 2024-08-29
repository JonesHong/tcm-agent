import __init__

from src.schemas._enum import MessageType
from src.utils.prompting.prompting_service import prompt_service_factory

string_length_limit = 30
user_prompt_prefix = f"1. 嘗試理解使用者上下文、語境想表達的內容\n2. 用你自己的話重新闡述，盡可能的語意通順、白話文一點\n3. 最重要的是字數控制在{string_length_limit}個字以內。\n- - - -\n"
prompt_service_factory.create_prompt_service(
    name="simplify_sentence_flow",
    user_prompt_prefix=user_prompt_prefix,
    system_prompt=(
        MessageType.SYSTEM.value,
        f"你是非常有幫助的助手。這對我的事業很重要，如果你做的好我會給你小費，請你放輕鬆一步一步來。你將會忠實的根據以下命令來執行{user_prompt_prefix}",
    ),
    example_prompts=[
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}問汗問便問渴",
        ),
        (MessageType.ASSISTANT.value, "你平時出汗情況如何？是容易出汗還是很少出汗？你最近的大便和小便情況如何？有沒有便秘或尿頻等問題？你平時容易口渴嗎？飲水量是否比平常多？"),
    
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}不入虎穴，焉得虎子。",
        ),
        (MessageType.ASSISTANT.value, "不進入老虎的洞穴，怎麼能捉到小老虎呢？意思是要有所收穫，必須勇敢去嘗試。"),
    ]
# llm=
)

simplify_sentence_flow_agent = prompt_service_factory.simplify_sentence_flow

# # 直接通过名称访问并使用服务
response_1 = simplify_sentence_flow_agent.invoke("問寒熱問飲食問聾")
print("AI Response:", response_1.content)

message_2 = "欲速則不達，見小利則大事不成"
response_2 = simplify_sentence_flow_agent.invoke(message_2)
print("AI Response:", response_2.content)

message_3 = "你覺得最近身體偏冷還是偏熱？有發燒或怕冷的情況嗎？這些症狀在一天中是否有變化？你有沒有感覺胸悶、心悸或腹部不適？是否有腹脹、腹痛或噯氣的情況？小便顏色正常嗎？最近有頻尿或尿量減少的情況嗎？一天大概上幾次廁所？"
response_3 = simplify_sentence_flow_agent.invoke(message_3)
print("AI Response:", response_3.content)