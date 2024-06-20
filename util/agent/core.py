
# 获取项目根目录
import os
import sys
from typing import Literal

from redis import Redis

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 添加项目根目录到 sys.path
sys.path.append(project_root)

from util.agent.mode import AgentMode
# from util.rag_chain import SelfIntroduction, JiudaTizhi, ZhongyiShiwen, llm
from util.agent.strategy import ChitchatStrategy, DiagnosticStrategy, EvaluationAndAdvice, InquiryStrategy, TongueDiagnosis


class Agent:
    user_info_from_yolo = None
    def __init__(self):
        self.__mode = AgentMode.DIAGNOSTIC
        self.__qa = ["睡眠", "胃口", "大便", "小便", "口渴", "寒熱", "汗", "體力", "性功能", "女子月經"]
        self.initial()
        

    def initial(self):
        self.user_info_from_yolo = None
        self.__sex: Literal['male', 'female']  = 'male'
        self.__messages = []
        self.__questions = {}
        self.__answers = {}
        self.__question_count = 0
        self.__strategy = DiagnosticStrategy()
        self.transformed_data = {"age": None, "male": None}
        self.redis_client:Redis = None
        # self.question_count = None
        
    @property
    def mode(self):
        return self.__mode
    @property
    def sex(self) -> Literal['male', 'female']:
        return self.__sex
    @property
    def messages(self):
        return self.__messages
    @property
    def qa(self):
        return self.__qa
    @property
    def questions(self):
        return self.__questions
    @property
    def answers(self):
        return self.__answers
    @property
    def question_count(self):
        return self.__question_count
    
    @mode.setter
    def mode(self, value):
        self.__mode = value
        if value == AgentMode.DIAGNOSTIC:
            self.__strategy = DiagnosticStrategy()
        elif value == AgentMode.TONGUE_DIAGNOSIS:
            self.__strategy = TongueDiagnosis()
        elif value == AgentMode.EVALUATION_ADVICE:
            self.__strategy = EvaluationAndAdvice()
        elif value == AgentMode.INQUIRY:
            self.__strategy = InquiryStrategy()
        elif value == AgentMode.CHITCHAT:
            self.__strategy = ChitchatStrategy()
            
    @sex.setter
    def sex(self, value: Literal['male', 'female']):
        if value not in ['male', 'female']:
            raise ValueError("Sex must be 'male' or 'female'")
        self.__sex = value
    @question_count.setter
    def question_count(self, value):
        if value is None:
            pass
        elif value < self.__question_count:
            print(f"請注意，此操作可能會導致重複回答已經回答過的問題。\n目前問題是關於:(問題{self.__question_count}){self.__qa[self.__question_count]}，你將回到(問題{value}){self.__qa[value]}。")
        elif value > self.__question_count and value != self.__question_count + 1:
            print(f"請注意，此操作可能會導致問題被跳過。\n目前問題是關於:(問題{self.__question_count}){self.__qa[self.__question_count]}，你將跳到(問題{value}){self.__qa[value]}。")
        self.__question_count = value

    def invoke(self, user_input):
        if self.question_count is not None:
            return self.__strategy.handle_interaction(self, user_input)
        else:
            return '請稍後在試。'