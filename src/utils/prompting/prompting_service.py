import time
import copy
from typing import Dict, Iterator, List, Literal, Tuple, Union

from langchain_core.messages.base import BaseMessage, BaseMessageChunk
from opencc import OpenCC
from reactivex import Subject, create
from reactivex.operators import first
from src.services.agent_service.ollama_llm import ollama_llm as default_llm
from src.schemas._enum import MessageType
from src.utils.decorators.inject_llm import inject_llm
from src.utils.decorators.singleton import singleton
from src.utils.log import logger
from src.utils.config.manager import ConfigManager


config = ConfigManager()
system_config = config.system

cc = OpenCC(system_config.opencc_convert)
@inject_llm(default_llm)
class PromptServiceBase:
    """
    提供處理提示生成邏輯的基礎服務。

    Attributes:
        __chunk_subject (Subject): 用於單個chunk的事件通知。
        __content_collector_subject (Subject): 用於累積所有chunk並提供最終結果的事件通知。
        user_prompt_prefix (str, optional): 用戶提示的前綴。默認為 None。
        system_prompt (str, optional): 系統提示。默認為 None。
        example_prompts (List[Tuple[str, str]], optional): 提供示例提示列表。
        llm (ChatOllama, optional): 用於生成提示的LLM（大語言模型）。預設從 ollama_llm載入
    """

    def __init__(
        self,
        user_prompt_prefix=None,
        system_prompt=None,
        example_prompts=None,
        llm=None,
    ):
        self.__chunk_subject = Subject()  # 用於單個chunk的 Subject
        self.__content_collector_subject = Subject()  # 用於累加chunk的 Subject
        self.user_prompt_prefix = user_prompt_prefix
        self.system_prompt = system_prompt
        self.example_prompts = example_prompts or []
        self.llm = llm if llm else default_llm
        self.initial()

    def initial(self):
        """重置歷史消息列表"""
        self.value = None
        self._messages_history = []  # 初始化历史消息列表

    @property
    def messages_list_proto(self):
        """組合出基礎的消息列表，如果 system_prompt 為 None，返回空列表"""
        return (
            [self.system_prompt] if self.system_prompt else []
        ) + self.example_prompts

    def assemble_messages(self, user_input: Union[str, List[Tuple[str, str]]]):
        """
        組合最終的消息列表，將用戶輸入添加到歷史消息中。

        Args:
            user_input (Union[str, List[Tuple[str, str]]]): 用戶輸入，可以是字符串或列表格式。
        
        Returns:
            List: 最終組合的消息列表。
        """
        new_messages_list = copy.deepcopy(self.messages_list_proto)

        # 如果 user_input 是字符串，则将其转换为消息格式
        if isinstance(user_input, str):
            new_entry = (
                MessageType.USER.value,
                f"{self.user_prompt_prefix or ''}{user_input}",
            )
            new_messages_list.append(new_entry)
        elif isinstance(user_input, list):
            new_messages_list.extend(user_input)

        # 将新输入的消息添加到历史记录中
        self.add_to_history(new_messages_list[-1])
        return new_messages_list

    def _log_performance(self, response_content: str, start_time: float):
        """
        记录性能指标，如总执行时间、总字数及平均每秒字数。

        Args:
            response_content (str): 生成的回复内容。
            start_time (float): 计时开始的时间戳。
        """
        end_time = time.time()
        total_time = end_time - start_time
        total_characters = len(response_content)
        average_characters_per_second = total_characters / total_time

        logger.info(f"總執行時間: {total_time:.2f} 秒")
        logger.info(f"總字數: {total_characters} 字")
        logger.info(f"平均每秒字數: {average_characters_per_second:.2f} 字/秒")

    def invoke(
        self,
        user_input: Union[str, List[Tuple[str, str]]],
        measure_performance: bool = False,
    ) -> BaseMessage:
        """
        非流式呼叫，生成完整的回复。

        Args:
            user_input (Union[str, List[Tuple[str, str]]]): 用戶輸入。
            measure_performance (bool): 是否记录性能指标。

        Returns:
            BaseMessage: 包含生成内容的完整消息对象。
        """
        if measure_performance:
            start_time = time.time()

        messages = self.assemble_messages(user_input)
        ai_response = self.llm.invoke(messages)
        ai_response.content = cc.convert(ai_response.content)
        response_content = ai_response.content

        if measure_performance:
            self._log_performance(response_content, start_time)

        assistant_response = (MessageType.ASSISTANT.value, response_content)
        self.add_to_history(assistant_response)
        return ai_response  # 返回完整的BaseMessage對象

    def stream(
        self,
        user_input: Union[str, List[Tuple[str, str]]],
        measure_performance: bool = False,
    ) -> Iterator[BaseMessageChunk]:
        """
        流式呼叫，逐步生成回复内容。

        Args:
            user_input (Union[str, List[Tuple[str, str]]]): 用戶輸入。
            measure_performance (bool): 是否记录性能指标。

        Returns:
            Iterator[BaseMessageChunk]: 返回一个生成器，逐块生成 BaseMessageChunk。
        """
        if measure_performance:
            start_time = time.time()

        messages = self.assemble_messages(user_input)
        response_content = ""  # 用於存儲完整的回應內容
        stream_response = self.llm.stream(messages)  # 使用流式呼叫

        def generate_response():
            nonlocal response_content
            for chunk in stream_response:
                chunk.content = cc.convert(chunk.content)
                response_content += chunk.content  # 累積每個chunk的內容
                yield chunk

            if measure_performance:
                self._log_performance(response_content, start_time)

            assistant_response = (MessageType.ASSISTANT.value, response_content)
            self.add_to_history(assistant_response)

        return generate_response()

    def stream_with_rx(
        self,
        user_input: Union[str, List[Tuple[str, str]]],
        measure_performance: bool = False,
    ) -> Iterator[BaseMessageChunk]:
        """
        流式呼叫（Rx版），使用 RxPython 处理流式数据。

        Args:
            user_input (Union[str, List[Tuple[str, str]]]): 用戶輸入。
            measure_performance (bool): 是否记录性能指标。

        Returns:
            Iterator[BaseMessageChunk]: 返回一个生成器，逐块生成 BaseMessageChunk。
        """
        if measure_performance:
            start_time = time.time()

        messages = self.assemble_messages(user_input)
        response_content = ""  # 用於存儲完整的回應內容
        stream_response = self.llm.stream(messages)  # 使用流式呼叫

        def generate_response(observer, scheduler):
            try:
                nonlocal response_content
                for chunk in stream_response:
                    chunk.content = cc.convert(chunk.content)
                    response_content += chunk.content  # 累積每個chunk的內容
                    # 通知chunk_subject單個chunk
                    self.__chunk_subject.on_next(chunk)
                    # 通知content_collector_subject累加後的結果
                    self.__content_collector_subject.on_next(
                        {
                            "content": response_content,
                            "done": chunk.response_metadata.get("done", False),
                        }
                    )

                if measure_performance:
                    self._log_performance(response_content, start_time)

                assistant_response = (MessageType.ASSISTANT.value, response_content)
                self.add_to_history(assistant_response)

            except Exception as e:
                self.__chunk_subject.on_error(e)
                self.__content_collector_subject.on_error(e)

        # 使用 create 創建一個 Observable
        observable = create(generate_response)
        # 將 Observable 訂閱到兩個 Subject，這樣它們的訂閱者也會收到事件
        observable.subscribe(lambda x: None)  # 這個subscribe是為了啟動Observable

    def subscribe_to_chunk(self, observer):
        """允許外部訂閱chunk_subject"""
        return self.__chunk_subject.subscribe(observer)

    def subscribe_to_content_collector(self, observer):
        """允許外部訂閱content_collector_subject"""
        return self.__content_collector_subject.subscribe(observer)

    def add_to_history(self, message):
        """將消息添加到歷史記錄中"""
        self._messages_history.append(message)

    @property
    def messages_history_list(self):
        """返回消息歷史記錄的列表"""
        return self._messages_history

    def test_examples(
        self,
        examples: List[str],
        method: Literal["invoke", "stream", "stream_with_rx"] = "invoke",
        measure_performance: bool = False
    ):
        """
        测试多个示例，使用指定的方法和性能测量选项。

        Args:
            examples (List[str]): 要测试的示例列表。
            method (Literal["invoke", "stream", "stream_with_rx"]): 调用方法，'invoke'、'stream' 或 'stream_with_rx'。默认为 'invoke'。
            measure_performance (bool): 是否记录性能指标。默认为 False。
        """
        for example in examples:
            print(f"Original Message: {example}")

            if method == "invoke":
                response = self.invoke(example, measure_performance=measure_performance)
                print(f"AI Response: {response.content}")
            elif method == "stream":
                for chunk in self.stream(example, measure_performance=measure_performance):
                    print(f"Chunk: {chunk.content}")
                print("Completed stream.")
            elif method == "stream_with_rx":
                def handle_test_examples(result):
                    # print(result)
                    if result['done']:
                        print(result['content'])
                subscriptions = self.subscribe_to_content_collector(handle_test_examples)
                self.stream_with_rx(example, measure_performance=measure_performance)
                # for chunk in:
                # print(f"Chunk: {chunk.content}")
                subscriptions.dispose()
                print("Completed stream with Rx.")
            else:
                raise ValueError("Unsupported method. Choose from 'invoke', 'stream', or 'stream_with_rx'.")

            print("\n")  # 在每个测试示例之间插入空行

@singleton
class PromptServiceFactory:
    """
    工廠類，用於創建和管理多個 PromptServiceBase 實例。

    Attributes:
        _services (dict): 存儲所有創建的 PromptServiceBase 實例。
    """

    def __init__(self):
        self._services: Dict[str, PromptServiceBase] = {}

    def create_prompt_service(
        self,
        name: str,
        user_prompt_prefix: str = None,
        system_prompt: str = None,
        example_prompts: List[Tuple[str, str]] = None,
        llm=None,
    ) -> PromptServiceBase:
        """
        創建一個新的 PromptServiceBase 實例並存儲在 _services 字典中。

        Args:
            name (str): 服務名稱。
            user_prompt_prefix (str, optional): 用戶提示前綴。默認為 None。
            system_prompt (str, optional): 系統提示。默認為 None。
            example_prompts (List[Tuple[str, str]], optional): 示例提示列表。默認為 None。
            llm (optional): 指定的大語言模型。默認為 None。

        Returns:
            PromptServiceBase: 創建的 PromptServiceBase 實例。
        """
        service = PromptServiceBase(
            user_prompt_prefix, system_prompt, example_prompts, llm
        )
        self._services[name] = service
        return service

    def remove_prompt_service(self, name: str):
        """
        移除指定名稱的 PromptServiceBase 實例。

        Args:
            name (str): 服務名稱。

        Raises:
            AttributeError: 當指定的服務名稱不存在時拋出。
        """
        if name in self._services:
            del self._services[name]
        else:
            raise AttributeError(f"Service '{name}' does not exist.")

    def clear(self):
        self._services.clear()
    def reset(self):
        """重置所有存儲的 PromptServiceBase 實例。"""
        for service in self._services.values():
            service.initial()
        self._services.clear()

    def __getattr__(self, name) -> PromptServiceBase:
        """
        獲取指定名稱的 PromptServiceBase 實例。

        Args:
            name (str): 服務名稱。

        Raises:
            AttributeError: 當指定的服務名稱不存在時拋出。

        Returns:
            PromptServiceBase: 對應的 PromptServiceBase 實例。
        """
        if name in self._services:
            return self._services[name]
        raise AttributeError(f"'PromptServiceFactory' object has no attribute '{name}'")


# 使用工厂生成不同的 PromptService 实例
prompt_service_factory = PromptServiceFactory()
