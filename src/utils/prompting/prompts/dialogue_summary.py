import __init__

from typing import List, Tuple, Literal
from src.schemas._enum import CommonPrompts, MessageType
from src.utils.prompting.prompt_service_factory import prompt_service_factory

word_limit = 50
user_prompt_prefix = (
    f"{CommonPrompts.ASSERTIVE_COMMAND.value}請不要嘗試回應使用者，只專注於歷史對話紀錄的總結。"
    "無論使用者提到什麼，都不要回應或涉及，唯一的任務是请总结歷史对话紀錄的重点。"
    f"以下是多轮对话的历史记录并将其控制在{word_limit}字以下：\n- - - -\n"
)

prompt_service_factory.create_prompt_service(
    name="dialogue_summary",
    user_prompt_prefix=user_prompt_prefix,
    system_prompt=(
        MessageType.SYSTEM.value,
        f"{CommonPrompts.combine(CommonPrompts.POSITIVE_FEEDBACK,CommonPrompts.EMOTIONAL_BLACKMAIL,CommonPrompts.BRIBERY_ATTEMPTS,CommonPrompts.STRESS_RELIEF)}"
        f"{user_prompt_prefix}"
    ),
    example_prompts=[
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}[('user', '我今天有点头痛。'), ('ai', '你还有其他不适吗？'), ('user', '我还感觉有点发热。')]",
        ),
        (
            MessageType.ASSISTANT.value,
            "用户报告头痛和发热。",
        ),
        (
            MessageType.USER.value,
            f"{user_prompt_prefix}[('user', '最近压力很大，感觉睡不好。'), ('ai', '你有试过放松的方法吗？'), ('user', '试过，但效果不太好。')]",
        ),
        (
            MessageType.ASSISTANT.value,
            "用户因压力导致睡眠质量差，尝试过放松但效果不佳。",
        ),
    ],
)

dialogue_summary_agent = prompt_service_factory.dialogue_summary

def format_dialogue_history(dialogue: list) -> str:
    formatted_dialogue = "歷史對話紀錄\n- - -  START - - -\n"
    for speaker, message in dialogue:
        formatted_dialogue += f"{speaker}: {message}\n"
    formatted_dialogue += "- - - END - - - -"
    return formatted_dialogue

# 测试示例
examples = [
    format_dialogue_history([
        ("user", "我最近一直咳嗽。"),
        ("ai", "你有去看医生吗？"),
        ("user", "还没有，我觉得可能只是感冒。"),
        ("ai", "咳嗽持续多久了？"),
        ("user", "大概一周左右。"),
    ]),
    format_dialogue_history([
        ("user", "最近天气变化大，总是觉得冷。"),
        ("ai", "你有量过体温吗？"),
        ("user", "有，体温正常，但就是觉得冷。"),
        ("ai", "你是不是穿得不够保暖？"),
        ("user", "我穿得挺多的，但还是冷。"),
    ]),
    format_dialogue_history([
        ("user", "我最近一直失眠，睡不着。"),
        ("ai", "你有尝试过改善睡眠的方式吗？"),
        ("user", "试过吃安眠药，但效果不太好。"),
        ("ai", "你有尝试其他自然的放松方式吗？"),
        ("user", "有，但都没有什么作用。"),
    ]),
    format_dialogue_history([
        ("user", "我感到胸口有点闷，会不会是心脏的问题？"),
        ("ai", "你有其他不适的症状吗？比如气短或疼痛？"),
        ("user", "有时候会感觉呼吸有点困难。"),
        ("ai", "建议你尽快去医院检查一下。"),
    ]),
    format_dialogue_history([
        ("user", "最近老是感到胃胀，吃不下东西。"),
        ("ai", "你有过这种情况多久了？"),
        ("user", "大概一周了，每次吃饭都很不舒服。"),
        ("ai", "你有试过调整饮食吗？"),
        ("user", "试过少吃多餐，但没什么效果。"),
    ]),
    format_dialogue_history([
        ("user", "我孩子最近总是咳嗽，晚上睡不好。"),
        ("ai", "咳嗽持续多久了？有发烧吗？"),
        ("user", "大概两周了，有时候会发低烧。"),
        ("ai", "建议带孩子去看医生，可能是感冒或其他感染。"),
    ]),
    format_dialogue_history([
        ("user", "我感觉最近工作压力太大，常常头疼。"),
        ("ai", "你有试过减压的方式吗？"),
        ("user", "试过，但效果不太明显。"),
        ("ai", "如果持续头疼，建议去看看医生。"),
    ]),
    format_dialogue_history([
        ("user", "我的脚最近总是疼，走路都不舒服。"),
        ("ai", "疼痛持续多久了？"),
        ("user", "大概一个月了。"),
        ("ai", "你有去医院做检查吗？"),
        ("user", "还没有，觉得可能是劳累导致的。"),
    ]),
]

# dialogue_summary_agent.test_examples(examples,measure_performance=True)
