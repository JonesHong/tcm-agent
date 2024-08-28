import __init__

from src.schemas._enum import MessageType
from src.utils.prompting.prompting_service import prompt_service_factory

string_lenth_limit = 50
user_prompt_prefix=f"以下整句話濃縮總結成一個不超過{string_lenth_limit}字的重點句子\n- - - -\n"
prompt_service_factory.create_prompt_service(
    name="summary",
    user_prompt_prefix=user_prompt_prefix,
    system_prompt=(
        MessageType.SYSTEM.value,
        f"請將使用者的整句話濃縮總結成一個不超過{string_lenth_limit}字的重點句子。",
    ),
    example_prompts=[
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}根据您的症状，我建议您使用刘某的中药方「平热散」进行治疗。该方由香附、川芎、当归、柴胡、秦艽、熟地黄、新疆延胡索、苦楝皮和槟榔组成。这些药物具有清热解毒、燥湿止带的功效，能够清除体内的风热毒素，从而改善您的头痛和发热等症状。建议您每次服用3钱，用水1盏煎8分钟后服用。在服用过程中，注意避免食用辛辣刺激性食物，以免影响药效。同时，建议您适当休息，保持心情舒畅，避免过度疲劳。如果症状没有改善或加重，请及时停止服用并咨询医生。此处方只适用于一定类型的症状，如初春感",
        ),
        (MessageType.ASSISTANT.value, "建议使用刘某的中药方「平热散」治疗头痛和发热，强调避免辛辣食物，并在无效时咨询医生。"),
    ]
# llm=
)

summary_agent = prompt_service_factory.summary

# # 直接通过名称访问并使用服务
# response_1 = summary_agent.invoke("中颱珊珊目前位於日本九州南方海面上，以時速4公里超慢速度朝北北西方向前進，已經開始影響日本。氣象粉專表示，美國模式仍預估珊珊會卡在九州，然後大迴轉往南逆襲，跑到台灣附近，值得注意的是，歐洲模式有部分小成員的看法也接近美國模式。氣象粉專「台灣颱風論壇｜天氣特急」發文指出，從珊珊颱風最新預測路徑來看，移動速度調慢許多，影響九州、四國等日本西部時間拉長，從九州走到關西就要花3天。粉專表示，美國全球模式仍然預估珊珊會卡在九州，然後大迴轉南落逆襲，跑到台灣附近，但前提是珊珊要捱過日本陸地摧殘；值得一提的是，歐洲模式已有部分小成員看法接近美國模式，「非常有趣、值得關注的趨勢。」對此，中央氣象署表示，由於颱風移動速度慢，且導引氣流不明顯，因此未來路徑充滿不確定性，雖然美國模式預測珊珊可能會回馬槍跑到台灣附近，但短期內主要影響仍以日本為主。")
# print("AI Response:", response_1.content)

message_2 = """
黄连汤是一种传统的中医方剂，主要用于治疗肝火犯胃、呕吐、腹痛等症状。其组成药物包括黄连、枳实、厚朴、甘草等。

中医诊断：黄连汤适用于肝火亢盛、胃火上炎、呕吐、腹痛等症状。

治疗原则：清肝泻火，解毒消炎。

处方建议：黄连6克，枳实15克，厚朴10克，甘草6克。服药方法：每日一剂，水煎服，分早晚两次温服。

注意：黄连汤有较强的清热解毒作用，应谨慎使用，不适合于孕妇、哺乳期女性和有出血倾向的人。
"""
response_2 = summary_agent.invoke(message_2)
print("AI Response:", response_2.content)