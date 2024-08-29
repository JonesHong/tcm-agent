import time
import __init__

import copy
from typing import List, Tuple, Union
from src.services.agent_service.ollama_llm import ollama_llm as default_llm
from src.schemas._enum import MessageType
from src.utils.decorators.inject_llm import inject_llm
from src.utils.decorators.singleton import singleton
from src.utils.log import logger


@inject_llm(default_llm)
class PromptServiceBase:
    def __init__(self, user_prompt_prefix=None, system_prompt=None, example_prompts=None, llm=None):
        self.user_prompt_prefix = user_prompt_prefix
        self.system_prompt = system_prompt
        self.example_prompts = example_prompts or []
        self.llm = llm if llm else default_llm
        self.reset()

    def reset(self):
        self.value = None
        self._messages_history = []  # 初始化历史消息列表

    @property
    def messages_list_proto(self):
        # 如果 system_prompt 为 None，返回空列表
        return ([self.system_prompt] if self.system_prompt else []) + self.example_prompts

    def assemble_messages(self, user_input: Union[str, List[Tuple[str, str]]]):
        new_messages_list = copy.deepcopy(self.messages_list_proto)
        
        # 如果 user_input 是字符串，则将其转换为消息格式
        if isinstance(user_input, str):
            new_entry = (
                MessageType.USER.value,
                f"{self.user_prompt_prefix or ''}{user_input}",
            )
            
            # print(new_entry)
            new_messages_list.append(new_entry)
        elif isinstance(user_input, list):
            new_messages_list.extend(user_input)

        # 将新输入的消息添加到历史记录中
        self.add_to_history(new_messages_list[-1])
        return new_messages_list

    def invoke(self, user_input: Union[str, List[Tuple[str, str]]], measure_performance: bool = False):
        if measure_performance:
            start_time = time.time()

        messages = self.assemble_messages(user_input)
        ai_response = self.llm.invoke(messages)
        
        if measure_performance:
            end_time = time.time()
            total_time = end_time - start_time
            total_characters = len(ai_response.content)
            average_characters_per_second = total_characters / total_time
            
            logger.info(f"總執行時間: {total_time:.2f} 秒")
            logger.info(f"總字數: {total_characters} 字")
            logger.info(f"平均每秒字數: {average_characters_per_second:.2f} 字/秒")

        assistant_response = (MessageType.ASSISTANT.value, ai_response.content)
        self.add_to_history(assistant_response)
        return ai_response

    def add_to_history(self, message):
        self._messages_history.append(message)

    @property
    def messages_history_list(self):
        return self._messages_history

@singleton
class PromptServiceFactory:
    def __init__(self):
        self._services = {}

    def create_prompt_service(
        self, 
        name: str, 
        user_prompt_prefix: str = None, 
        system_prompt: str = None, 
        example_prompts: List[Tuple[str, str]] = None, 
        llm = None
    ) -> PromptServiceBase:
        service = PromptServiceBase(user_prompt_prefix, system_prompt, example_prompts, llm)
        self._services[name] = service
        return service

    def __getattr__(self, name) -> PromptServiceBase:
        if name in self._services:
            return self._services[name]
        raise AttributeError(f"'PromptServiceFactory' object has no attribute '{name}'")


# 使用工厂生成不同的 PromptService 实例
prompt_service_factory = PromptServiceFactory()
