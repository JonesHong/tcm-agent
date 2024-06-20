# 获取项目根目录
import os
import sys


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 添加项目根目录到 sys.path
sys.path.append(project_root)

# from util.agent.mode import AgentMode
from util.rag_chain import SelfIntroduction, JiudaTizhi, ZhongyiShiwen, llm


from abc import ABC, abstractmethod

class InteractionStrategy(ABC):
    @abstractmethod
    def handle_interaction(self, agent, user_input):
        pass

      
# Diagnostic mode for medical inquiry (問診模式")
class DiagnosticStrategy(InteractionStrategy):
    def handle_interaction(self, agent, user_input):
        if agent.question_count == 0:
            self_introduction_response = SelfIntroduction({"input": "根據知識庫。請按照＂自我介紹.txt＂文件做自我介紹"})
            zhongyi_shiwen_response = ZhongyiShiwen({"input": "根據知識庫。中醫十問當中的第一問的問診細節是什麼?只要問診細節：後面的文字就好"})
            question_key = agent.qa[agent.question_count]
            agent.questions[question_key] = zhongyi_shiwen_response['answer']

            response = llm.invoke(f"請把以下兩句話請按照順序進行合併。第一句：{self_introduction_response['answer']}\n 接著讓我們來開始第一個問題 \n第二句：{zhongyi_shiwen_response['answer']}")
        elif (agent.sex == 'male' and agent.question_count >= 9) or (agent.sex == 'female' and agent.question_count >= 10):
            formatted_list = [f"問{key}，答 {value}" for key, value in agent.answers.items()]
            formatted_string = "。".join(formatted_list)
            jiuda_tizhi_response = JiudaTizhi({"input": f"根據知識庫。請分析文件，以下描述最接近哪幾種體質特徵(1~3種)?有什麼飲食上的建議?請用中文回答\n- - -\n{formatted_string}"})
            response = jiuda_tizhi_response['answer']
            
            # agent.mode = AgentMode.CHITCHAT # 之後英改成 InquiryStrategy模式
        else:
            answer_key = agent.qa[agent.question_count - 1]
            agent.answers[answer_key] = user_input

            key = agent.qa[agent.question_count]
            zhongyi_shiwen_response = ZhongyiShiwen({"input": f"根據知識庫。中醫十問當中的{key}的問診細節是什麼?只要問診細節：後面的的文字就好"})

            question_key = agent.qa[agent.question_count]
            agent.questions[question_key] = zhongyi_shiwen_response['answer']

            llm_response = llm.invoke(f"如果以下文字內容是正面的，請你回答＂好的，我知道了！＂；如果以下文字內容是負面的，請總結以下文字大概意思就好字數不超過二十字，並在最前面加上＂我了解你有(_總結後的文字_)的問題。＂。\n{user_input}")
            response = llm.invoke(f"請把以下幾段話請按照順序進行合併。 {llm_response} \n　接著讓我們來進行下一個問題 \n {zhongyi_shiwen_response['answer']}")

        agent.question_count += 1
        agent.messages.append(response)
        return response

# Tongue diagnosis mode for health assessment (舌診模式)
class TongueDiagnosis(InteractionStrategy):
    def handle_interaction(self, agent, user_input):
        agent.redis_client.publish(R)
        # response = llm.invoke(f"Chitchat response for input: {user_input}")
        # agent.messages.append(response)
        # return response

# Evaluation and advice mode (評估和建議模式)
class EvaluationAndAdvice(InteractionStrategy):
    def handle_interaction(self, agent, user_input):
        # 自由提問模式的具體邏輯在這裡實現
        # 串接 RagFlow 使用大量額外資料，提供自由問答
        response = llm.invoke(f"Chitchat response for input: {user_input}")
        agent.messages.append(response)
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