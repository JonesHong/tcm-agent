import __init__

from src.schemas._enum import CommonPrompts, MessageType
from src.utils.prompting.prompting_service import prompt_service_factory

word_limit = 150
user_prompt_prefix = f"给出中医诊断和处方建议，{CommonPrompts.WORD_LIMIT.format(limit=word_limit)}\n- - - -\n"
prompt_service_factory.create_prompt_service(
    name="tcm_qa",
    user_prompt_prefix=user_prompt_prefix,
    system_prompt=(
        MessageType.SYSTEM.value,
        f"你是一位虛擬中醫師，根據使用者提出的問題進行回覆。請結合中醫理論，提供具體的診斷、建議或治療方案，並盡量解釋症狀背後的中醫原理。{CommonPrompts.WORD_LIMIT.format(limit=word_limit)}",
    ),
    example_prompts=[
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}"
            "戴某某，女，22岁，未婚。三年来行经腹痛，第一、二天痛剧，开始血量少，待三日血量渐多而痛稍减，色谈有块，周期尚准。"
            "平素喜暖畏寒，体倦乏力，不耐劳累，经至必服止痛片及中药，以求暂安。"
            "此次行经少腹痛剧，虽已过十余天，少腹仍绵绵作痛，时有发胀，舌淡苔白，脉细而迟。"
            "给出中医诊断和处方建议",
        ),
        (
            MessageType.ASSISTANT.value,
            "根据患者的症状和体征，可以做出以下中医诊断和处方建议："
            "中医诊断："
            "患者的主要症状为经行腹痛，伴有喜暖畏寒、体倦乏力、舌淡苔白、脉细而迟等症状，这些表现提示为“寒凝血瘀”及“气血虚弱”所致。"
            "证型分析："
            "寒凝血瘀：经行腹痛剧烈，喜暖畏寒，血色淡，有血块，提示寒邪凝滞，导致血瘀不通。"
            "气血虚弱：平素体倦乏力，不耐劳累，经至必服止痛片及中药，舌淡，脉细而迟，提示气血亏虚，不能推动血液运行，导致痛经。"
            "治疗原则：温经散寒，活血化瘀，补气养血。"
            "处方建议："
            "四物汤加减：当归10克，川芎8克，白芍12克，熟地黄12克，艾叶10克，肉桂5克，延胡索10克，香附10克，茯苓12克，红花6克。"
            "服药方法：每日一剂，水煎服，分早晚两次温服。"
            "其他建议：注意保暖，避免受寒，特别是在月经期间。饮食宜温热，避免生冷寒凉食物。适度运动，增强体质，但避免过劳。",
        ),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}"
            "最近晚上睡不好，早上起來還會偏頭痛，大便又乾又硬，小便三小時才一次，感覺汗也流不出來，全身脹脹的",
        ),
        (
            MessageType.ASSISTANT.value,
            "根据患者的症状，可以做出以下中医诊断和处方建议："
            "中医诊断："
            "患者的主要症状为睡眠不好、偏头痛、大便乾硬、小便量少、汗不出、全身脹脹，这些表现提示为“气虚血瘀”及“肝火犯胃”所致。"
            "证型分析："
            "气虚血瘀：患者的睡眠不好，早上起來偏头痛，可能是由于气虚导致血液不畅，引起头痛。同时，大便乾硬，小便量少，也提示气虚导致肠道和尿路功能不佳。"
            "肝火犯胃：患者的全身脹脹，可能是由于肝火亢盛，影响到胃部，导致胃火上炎。"
            "治疗原则："
            "补气养血：通过补充气血来改善睡眠和头痛。"
            "清肝泻火：通过清除肝火来缓解全身脹脹和胃火上炎的症状。"
            "处方建议："
            "九味甘草汤加减：当归10克，川芎8克，白芍12克，熟地黄12克，艾叶10克，肉桂5克，延胡索10克，香附10克，茯苓12克。"
            "黄连汤加减：黄连6克，枳实15克，厚朴10克，甘草6克。"
            "服药方法："
            "九味甘草汤加减，每日一剂，水煎服，分早晚两次温服。"
            "黄连汤加减，每日一剂，水煎服，分早晚两次温服。"
            "其他建议："
            "注意保养肝脏和胃部，避免过度劳累和精神紧张。"
            "适当运动和饮食调节，可以帮助改善睡眠和头痛。"
            "如果症状严重，请及时就医。",
        ),
    ],
    # llm=
)

tcm_qa_agent = prompt_service_factory.tcm_qa

# # 直接通过名称访问并使用服务
response_1 = tcm_qa_agent.invoke(
    "李某某，女，15岁。病起于外感，高热（39.5℃ ），头痛，肢体酸楚。至五六日后，突发上腹部疼痛，午后发热更甚，切脉弦紧有力，舌质红绛而苔腻，皮肤亢热，腹部板硬疼痛拒按，大便已七日未解，小便短赤，时发谵语。给出中医诊断和处方建议"
,measure_performance=True
)
print("AI Response:", response_1.content)

response_2 = tcm_qa_agent.invoke(
    "心跳最近總感覺慢一拍，胸口悶痛，大小便正常，最近因工作常熬夜",measure_performance=True
)
print("AI Response:", response_2.content)

response_3 = tcm_qa_agent.invoke(
    "黄连汤是什麼?有何效用?",measure_performance=True
)
print("AI Response:", response_3.content)
