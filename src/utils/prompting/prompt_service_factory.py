import __init__

from typing import Dict, List, Tuple
from src.utils.prompting.prompt_service_base import PromptServiceBase
from src.utils.decorators.singleton import singleton


@singleton
class PromptServiceFactory:
    """
    工廠類，用於創建和管理多個 PromptServiceBase 實例，並集中管理所有服務的歷史記錄。

    Attributes:
        _services (dict): 存儲所有創建的 PromptServiceBase 實例。
        history (List[Tuple[str, str]]): 集中存儲所有服務的歷史對話記錄。
    """

    def __init__(self):
        self._services: Dict[str, PromptServiceBase] = {}
        self.history: List[Tuple[str, str]] = []

    def add_to_history(self, message: Tuple[str, str]):
        """將新的歷史記錄添加到集中歷史記錄中"""
        self.history.append(message)

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
            user_prompt_prefix, system_prompt, example_prompts, llm, factory=self
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
            service.reset()
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