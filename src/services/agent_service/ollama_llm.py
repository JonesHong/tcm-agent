import __init__
from langchain_ollama import ChatOllama

from src.utils.log import logger
from src.utils.config.manager import ConfigManager
# ChatOllama.c

config = ConfigManager()
agent_config = config.agent
model_name = agent_config.model_name

ollama_llm = ChatOllama(
    model= agent_config.model_name,
    temperature= agent_config.temperature,
    base_url= agent_config.ollama_host
    # other params...
)

# ollama_llm.copy(True)