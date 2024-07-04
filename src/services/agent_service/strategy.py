import __init__
from src.schemas._enum import AgentMode,QaList,InterrogationDetails
from src.services.agent_service.rag_chain import JiudaTizhi, ZhongyiShiwen, llm
from src.utils.config.manager import ConfigManager
from src.utils.redis.channel import RedisChannel
from src.utils.redis.core import RedisCore
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
        condition = None
        
        if system_config.mode == 'test':
            condition = (agent.sex == 'male' and agent.question_count >= 4) or (agent.sex == 'female' and agent.question_count >= 4)
        else:
            condition = (agent.sex == 'male' and agent.question_count >= 9) or (agent.sex == 'female' and agent.question_count >= 10)

        if agent.question_count == 0:
            QaList
            # self_introduction_response = SelfIntroduction({"input": "根據知識庫。請按照＂自我介紹.txt＂文件做自我介紹"})
            # zhongyi_shiwen_response = ZhongyiShiwen({"input": "根據知識庫。中醫十問當中的第一問的問診細節是什麼?只要問診細節：後面的文字就好"})
            # question_key = QaList[agent.question_count]
            # agent.questions[question_key] = zhongyi_shiwen_response['answer']

            # response = llm.invoke(f"請把以下兩句話請按照順序進行合併。第一句：{self_introduction_response['answer']}\n 接著讓我們來開始第一個問題 \n第二句：{zhongyi_shiwen_response['answer']}")
            self_introduction= "您好，我是虛擬中醫師。問診對我非常重要。會根據您的回答，開出適合的處方。治療過程中，身體可能會出現一些反應，這是正常的請不用擔心。中醫治病是根據身體的症狀，而非西醫的檢驗報告，所以請詳細描述您的症狀，這樣才能幫助我為您提供最好的治療"
            zhongyi_shiwen = "你的睡眠如何？是否一覺到天亮？是否每天定時會醒？如果會醒，是幾點會醒？是否多夢？"
            response = f"{self_introduction}，接著讓我們來開始第一個問題。\n{zhongyi_shiwen}"
        # elif (agent.sex == 'male' and agent.question_count >= 2) or (agent.sex == 'female' and agent.question_count >= 2):
        elif (condition):
            # 源邏輯，移去評估和建議了
            # response = llm.invoke(f"請把以下幾段話請按照順序進行合併。\n第一句話: 接著讓我們進行舌診，請將舌頭伸出，配合畫面上的資訊 \n　第二句話: 我們會結合剛剛的問診和舌診給出評估和建議")
            # response = f"接下是舌診，請將舌頭伸出，配合畫面上的指示。我們會結合剛剛的問診和舌診給出評估和建議"
            # RedisCore.publisher(RedisChannel.do_aikanshe_service,'do ai kan she from Agent strategy.')
            agent.mode = AgentMode.TONGUE_DIAGNOSIS 
            response = f"接下來進行舌診，請將舌頭伸出，配合畫面上的指示。稍後我會結合問診和舌診給出評估和建議"
            # agent.invoke('開始舌診')
            # pass
        else:
            # 儲存用戶回答
            answer_key = QaList[agent.question_count - 1]
            agent.answers[answer_key] = user_input

            # 獲取下一個問題的問診細節
            key = QaList[agent.question_count]
            # zhongyi_shiwen_response = ZhongyiShiwen({"input": f"根據知識庫。中醫十問當中的{key}的問診細節是什麼?只要問診細節：後面的的文字就好"})
            zhongyi_shiwen_response = InterrogationDetails[key]
            # logger.info(agent.interrogation_details,key,zhongyi_shiwen_response)
            
            # 儲存問診問題
            question_key = QaList[agent.question_count]
            # agent.questions[question_key] = zhongyi_shiwen_response['answer']
            agent.questions[question_key] = zhongyi_shiwen_response
            # logger.info(agent.questions[question_key])
            

            # llm_response = llm.invoke(f"如果以下文字內容是正面的，請你回答＂好的，我知道了！＂；如果以下文字內容是負面的，請總結以下文字大概意思就好字數不超過二十字，並在最前面加上＂我了解你有(_總結後的文字_)的問題。＂。\n{user_input}")
            # response = llm.invoke(f"請把以下幾段話請按照順序進行合併。 {llm_response} \n　接著讓我們來進行下一個問題 \n {zhongyi_shiwen_response['answer']}")
            
            llm_response = llm.invoke(f"請隊以下文字打分數(1~10)，分數越高代表越正面，反則為負面。如果以下文字內容是分數很高，請你回答＂好的，我知道了！＂；如果以下文字內容是分數很低，請總結以下文字大概意思就好字數不超過二十字，並在最前面加上＂我了解你有(_總結後的文字_)的問題。＂。\n{user_input}")
            # response = f"{llm_response}接著讓我們來進行下一個問題。\n{zhongyi_shiwen_response['answer']}"
            response = f"{llm_response}接著讓我們來進行下一個問題。\n{zhongyi_shiwen_response}"

        agent.question_count += 1
        if response is not None:
            agent.messages.append(response)
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
        agent.mode = AgentMode.SILENT # 之後要變成 INQUIRY 自由提問
        # response = llm.invoke(f"Chitchat response for input: {user_input}")
        agent.messages.append(response)
        
        
        message = {"text": response}
        redis_core.publisher(RedisChannel.do_tts_service, message)
        return response

# Inquiry mode for general questions (自由提問模式)
class InquiryStrategy(InteractionStrategy):
    def handle_interaction(self, agent, user_input):
        # 自由提問模式的具體邏輯在這裡實現
        # 串接 RagFlow 使用大量額外資料，提供自由問答
        response = llm.invoke(f"Chitchat response for input: {user_input}")
        agent.messages.append(response)
        return response
# Chitchat mode for casual conversation (閒聊模式)
class ChitchatStrategy(InteractionStrategy):
    def handle_interaction(self, agent, user_input):
        # 閒聊模式的具體邏輯在這裡實現
        response = llm.invoke(f"Chitchat response for input: {user_input}")
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