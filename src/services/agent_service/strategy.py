import random
import time
import __init__
from src.schemas._enum import (
    AgentMode,
    Intent,
    MessageType,
    QaList,
    InterrogationDetails,
)
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from src.services.agent_service.agent import AgentClass

from src.services.agent_service.ollama_llm import ollama_llm as llm
from src.services.agent_service.rag_chain import JiudaTizhi, ZhongyiShiwen
from src.utils.config.manager import ConfigManager
from src.utils.redis.channel import RedisChannel
from src.utils.redis.core import RedisCore
from src.utils.log import logger
from src.utils.prompting.exports import (
    constitution_classification_agent,
    constitution_advice_agent,
    correct_sentence_flow_agent,
    intent_detection_agent,
    greeting_agent,
    farewell_agent,
    simplify_sentence_flow_agent,
    summary_agent,
    symptom_classification_agent,
    tcm_qa_agent,
)
from abc import ABC, abstractmethod

config = ConfigManager()
agent_config = config.agent
system_config = config.system
redis_core = RedisCore()


class InteractionStrategy(ABC):
    def __init__(self, agent: "AgentClass"):
        self.agent = agent

    @abstractmethod
    def handle_invoke(self, user_input):
        pass


class InitialStrategy(InteractionStrategy):
    def handle_invoke(self, user_input):
        response = greeting_agent.invoke(user_input, measure_performance=True).content
        self.agent.mode = AgentMode[agent_config.mode]
        return response


# Diagnostic mode for medical inquiry (問診模式")
class DiagnosticStrategy(InteractionStrategy):
    __step: Literal[0, 1, 2] = 0
    """
    第一階段固定提問: 病史、病因、用藥
    第二階段隨機提問: 隨機抽取三題關於，寒熱、汗、頭身、大便、小便、飲食、胸腹、耳聾耳鳴、口渴
    第三階段診斷和建議: 1. 用歷史對話去判斷體質 2. 用體質去換建議
    """
    __dialogue = []

    def handle_invoke(self, user_input):
        response = None

        self.__dialogue.append((MessageType.USER.value, user_input))
        
        def format_questions(questions: list) -> str:
            """
            将 tuple 列表转换为指定格式的字符。

            :param questions: List of tuples, where each tuple contains a question name and a value.
            :return: List of formatted strings.
            """
            return "；\n".join(
                [f"問 {name}，參考回答 {value}" for name, value in questions]
            )

        if self.__step == 0:
            fixed_questions = list(InterrogationDetails.items())[
                -3:
            ]  # 固定提問 = 只固定拿 InterrogationDetails最後三個
            formatted_fixed_questions = format_questions(fixed_questions)
            logger.info(f"Fixed questions: {formatted_fixed_questions}")
            response = simplify_sentence_flow_agent.invoke(
                formatted_fixed_questions
            ).content
            self.__dialogue.append((MessageType.ASSISTANT.value, response))
            logger.info(f"Response after fixed questions: {response}")
            self.__step = 1
        elif self.__step == 1:
            remaining_questions = list(InterrogationDetails.items())[
                :-3
            ]  # 剩下的問題 = InterrogationDetails去掉最後三個
            random_three_questions = random.sample(
                remaining_questions, 3
            )  # 隨機抽三提問 = 隨機抽取三個問題
            formatted_random_three_questions = format_questions(random_three_questions)
            logger.info(
                f"Randomly selected three questions: {formatted_random_three_questions}"
            )
            response = simplify_sentence_flow_agent.invoke(
                formatted_random_three_questions
            ).content
            logger.info(f"Response after random questions: {response}")
            self.__step = 2
        elif self.__step == 2:
            simplify_diologue = (
                simplify_sentence_flow_agent.format_dialogue_history(self.__dialogue)
            )
            logger.info(f"Simplified dialogue: {simplify_diologue}")
            classification = constitution_classification_agent.invoke(
                simplify_diologue
            ).content
            logger.info(f"Constitution classification: {classification}")
            response = constitution_advice_agent.invoke(classification).content
            logger.info(f"Response after constitution advice: {response}")
            self.__step = 0
            self.agent.__diagnostic_result = response
            self.agent.mode = AgentMode.INQUIRY

        return response


# Tongue diagnosis mode for health assessment (舌診模式)
class TongueDiagnosis(InteractionStrategy):
    def handle_invoke(self, user_input):
        # logger.info(user_input)
        # response = llm.invoke(f"Chitchat response for input: {user_input}")
        response = (
            f"接下來進行舌診，請將舌頭伸出，配合畫面上的指示。稍後我們會給出評估和建議"
        )
        transformed_data = self.agent.transformed_data
        redis_core.publisher(RedisChannel.do_aikanshe_service, {**transformed_data})
        # self.agent.messages.append(response)
        return response


# Evaluation and advice mode (評估和建議模式)
class EvaluationAndAdvice(InteractionStrategy):
    def handle_invoke(self, user_input):
        # formatted_list = [f"問{key}，答 {value}" for key,
        #                   value in self.agent.answers.items()]
        # formatted_string = "。".join(formatted_list)
        # symptoms = f"{formatted_string}{user_input}"
        # # logger.info(f'symptoms: {symptoms}')
        # jiuda_tizhi_response = JiudaTizhi(
        #     {"input": f"根據知識庫。請分析文件，以下描述最接近哪幾種體質特徵(1~3種)?有什麼飲食上的建議?請用中文回答\n- - -\n{symptoms}"})
        # response = jiuda_tizhi_response['answer']
        # # logger.info(f'response: {response}')
        # self.agent.mode = AgentMode.INQUIRY  # 之後要變成 INQUIRY 自由提問
        # # response = llm.invoke(f"Chitchat response for input: {user_input}")
        # self.agent.messages.append(response)

        # message = {"text": response}
        # redis_core.publisher(RedisChannel.do_tts_service, message)
        # return response
        return


# Inquiry mode for general questions (自由提問模式)
class InquiryStrategy(InteractionStrategy):
    def handle_invoke(self, user_input):
        # 自由提問模式的具體邏輯在這裡實現
        response = None
        correct_sentence = correct_sentence_flow_agent.invoke(user_input).content
        intent = intent_detection_agent.invoke(correct_sentence).content

        def display_start_and_end(
            text: str, start_chars: int = 20, end_chars: int = 30
        ) -> str:
            if len(text) <= start_chars + end_chars:
                return text  # 如果文本长度小于或等于总字符数，直接返回整个文本
            start = text[:start_chars]
            end = text[-end_chars:]
            return f"{start}...{end}"

        logger.info(
            f"correct_sentence(修正句子): {display_start_and_end(correct_sentence)}"
        )
        logger.info(f"intent(意圖): {intent}")
        if intent == Intent.TONGUE_DIAGNOSIS.value or "舌" in intent:
            self.agent.mode = AgentMode.TONGUE_DIAGNOSIS
            response = self.agent.invoke(intent)
        elif intent == Intent.TCM_TEN_QUESTIONS.value or "十問" in intent:
            self.agent.mode = AgentMode.DIAGNOSTIC
            response = self.agent.invoke(intent)
        elif intent == Intent.END_CONVERSATION.value:
            response = farewell_agent.invoke("再見!").content
            # self.agent.mode = AgentMode.SILENT
        elif intent == Intent.FREE_QUESTION.value:
            response = tcm_qa_agent.invoke(user_input).content
        else:
            response = tcm_qa_agent.invoke(user_input).content
            pass

        # 串接 RagFlow 使用大量額外資料，提供自由問答
        # redis_core.deleter(RedisChannel.do_tts_service)
        # data = {"message_content": user_input, "stream": False}
        # redis_core.publisher(RedisChannel.do_ragflow_invoke, data)
        return response


# Chitchat mode for casual conversation (閒聊模式)
class ChitchatStrategy(InteractionStrategy):
    def handle_invoke(self, user_input):
        # 閒聊模式的具體邏輯在這裡實現
        # response = llm.invoke(f"Chitchat response for input: {user_input}")
        response = llm.stream(f"Chitchat response for input: {user_input}")
        self.agent.messages.append(response)
        return response


# Silent mode (沉默模式)


class Silent(InteractionStrategy):
    def handle_invoke(self, user_input):
        # 沉默模式的具體邏輯在這裡實現
        logger.info(
            "現行版本，流程上僅提供十問和舌診，評估與建議以後就保持沉默，等使用者離開"
        )
        # response = llm.invoke(f"Chitchat response for input: {user_input}")
        # self.agent.messages.append(response)
        # return response
        pass
