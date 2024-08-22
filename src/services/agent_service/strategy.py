import random
import __init__
from src.schemas._enum import AgentMode,QaList,InterrogationDetails
from src.services.agent_service.rag_chain import JiudaTizhi, ZhongyiShiwen, llm
from src.utils.config.manager import ConfigManager
from src.utils.redis.channel import RedisChannel
from src.utils.redis.core import RedisCore
from src.utils.log import logger
from abc import ABC, abstractmethod

config = ConfigManager()
system_config = config.system
redis_core = RedisCore()

class InteractionStrategy(ABC):
    @abstractmethod
    def handle_interaction(self, agent, user_input):
        pass

    
# Diagnostic mode for medical inquiry (問診模式")
class DiagnosticStrategy(InteractionStrategy):
    def handle_interaction(self, agent, user_input):
        response = None

        # 隨機從3到5之間選擇一個數字
        num_questions = random.randint(3, 5)

        # 從InterrogationDetails中隨機抽取num_questions個題目
        selected_keys = random.sample(list(InterrogationDetails.keys()), num_questions)
        
        # 初始化一個列表來保存要詢問的問題
        questions_to_ask = []

        for key in selected_keys:
            # 獲取對應的問診細節
            interrogation_detail = InterrogationDetails[key]
            questions_to_ask.append(interrogation_detail)

            # 儲存這次問診的問題和回答的對應
            agent.questions[key] = interrogation_detail

        # 將選中的問題合併成一段話
        combined_questions = " ".join(questions_to_ask)
        
        # 假設self_introduction是初始的自我介紹，已經在其他地方定義
        if agent.question_count == 0:
            # self_introduction = "您好，我是虛擬中醫師。問診對我非常重要。會根據您的回答，開出適合的處方。治療過程中，身體可能會出現一些反應，這是正常的請不用擔心。中醫治病是根據身體的症狀，而非西醫的檢驗報告，所以請詳細描述您的症狀，這樣才能幫助我為您提供最好的治療"
            self_introduction = "您好，我是虛擬中醫師。問診對我非常重要。會根據您的回答，開出適合的處方。治療過程中，身體可能會出現一些反應，這是正常的請不用擔心。中醫治病是根據身體的症狀，而非西醫的檢驗報告，所以請詳細描述您的症狀，這樣才能幫助我為您提供最好的治療"
            response = f"{self_introduction}。接下來讓我們開始問診。\n{combined_questions}"
        else:
            # 用LLM合併成一題去做詢問
            llm_response = llm.invoke(f"請根據以下問題合併成一段自然的詢問。\n{combined_questions}")
            response = llm_response

        # 將生成的問題添加到agent的消息記錄中
        agent.messages.append(response)

        # 增加問診的計數
        agent.question_count += 1

        return response

# Tongue diagnosis mode for health assessment (舌診模式)
class TongueDiagnosis(InteractionStrategy):
    def handle_interaction(self, agent, user_input):
        # logger.info(user_input)
        # response = llm.invoke(f"Chitchat response for input: {user_input}")
        # response = f"接下來進行舌診，請將舌頭伸出，配合畫面上的指示。稍後我們會結合問診和舌診給出評估和建議"
        transformed_data = agent.transformed_data
        redis_core.publisher(RedisChannel.do_aikanshe_service,{**transformed_data})
        # agent.messages.append(response)
        # return response
        # pass

# Evaluation and advice mode (評估和建議模式)
class EvaluationAndAdvice(InteractionStrategy):
    def handle_interaction(self, agent, user_input):
        formatted_list = [f"問{key}，答 {value}" for key, value in agent.answers.items()]
        formatted_string = "。".join(formatted_list)
        symptoms = f"{formatted_string}{user_input}"
        # logger.info(f'symptoms: {symptoms}')
        jiuda_tizhi_response = JiudaTizhi({"input": f"根據知識庫。請分析文件，以下描述最接近哪幾種體質特徵(1~3種)?有什麼飲食上的建議?請用中文回答\n- - -\n{symptoms}"})
        response = jiuda_tizhi_response['answer']
        # logger.info(f'response: {response}')
        agent.mode = AgentMode.INQUIRY # 之後要變成 INQUIRY 自由提問
        # response = llm.invoke(f"Chitchat response for input: {user_input}")
        agent.messages.append(response)
        
        
        message = {"text": response}
        redis_core.publisher(RedisChannel.do_tts_service, message)
        return response

# Inquiry mode for general questions (自由提問模式)
class InquiryStrategy(InteractionStrategy):
    def handle_interaction(self, agent, user_input):
        print(user_input)
        # 自由提問模式的具體邏輯在這裡實現
        # 串接 RagFlow 使用大量額外資料，提供自由問答
        # response = llm.invoke(f"Chitchat response for input: {user_input}")
        agent.messages.append(user_input)
        redis_core.publisher(RedisChannel.do_ragflow_invoke, user_input)
        return None
# Chitchat mode for casual conversation (閒聊模式)
class ChitchatStrategy(InteractionStrategy):
    def handle_interaction(self, agent, user_input):
        # 閒聊模式的具體邏輯在這裡實現
        # response = llm.invoke(f"Chitchat response for input: {user_input}")
        response = llm.stream(f"Chitchat response for input: {user_input}")
        agent.messages.append(response)
        return response
    
# Silent mode (沉默模式)
class Silent(InteractionStrategy):
    def handle_interaction(self, agent, user_input):
        # 沉默模式的具體邏輯在這裡實現
        logger.info("現行版本，流程上僅提供十問和舌診，評估與建議以後就保持沉默，等使用者離開")
        # response = llm.invoke(f"Chitchat response for input: {user_input}")
        # agent.messages.append(response)
        # return response
        pass