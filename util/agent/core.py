import __init__
from typing import Literal
from reactivex.subject.behaviorsubject import BehaviorSubject

from util.agent.mode import AgentMode
from util.agent.strategy import ChitchatStrategy, DiagnosticStrategy, EvaluationAndAdvice, InquiryStrategy, TongueDiagnosis


class Agent:
    user_info_from_yolo = None
    modeSub:BehaviorSubject
    def __init__(self):
        self.__mode = AgentMode.DIAGNOSTIC
        self.modeSub = BehaviorSubject(self.__mode)
        self.__qa = ["睡眠", "胃口", "大便", "小便", "口渴", "寒熱", "汗", "體力", "性功能", "月經"]
        self.__interrogation_details = {
            "睡眠": "你的睡眠狀況如何？晚上好睡嗎？有沒有早醒或多夢的情況？是否固定時間會醒來？",
            "胃口": "你最近食欲怎麼樣？會感覺餓嗎？有沒有特別想吃的食物或口味？胃口不好嗎？",
            "大便": "大便情況如何？有便秘嗎？每天都有大便嗎？大便顏色和氣味如何？",
            "小便": "小便顏色正常嗎？有頻尿或尿不出來的問題嗎？一天上幾次廁所？",
            "口渴": "你經常覺得口渴嗎？渴的時候喜歡喝什麼溫度的水？不渴的時候會忘記喝水嗎？",
            "寒熱": "你覺得身體是偏冷還是偏熱？手腳會不會冰冷？",
            "汗": "你容易出汗嗎？晚上會盜汗嗎？會不會動不動就流汗或完全不出汗？",
            "體力": "你最近精神狀況如何？感覺疲累嗎？早上起床精神好嗎？白天能集中精神嗎？",
            "性功能": "你的性功能正常嗎？有沒有什麼問題？",
            "月經": "月經情況怎麼樣？是準時還是會提前或延後？會痛嗎？有沒有生過小孩？"
        }
        self.initial()
        

    def initial(self):
        self.user_info_from_yolo = None
        self.__sex: Literal['male', 'female']  = 'male'
        self.__messages = []
        self.__questions = {}
        self.__answers = {}
        self.__question_count = 0
        self.mode = AgentMode.DIAGNOSTIC
        self.transformed_data = {"age": None, "male": None}
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
    def interrogation_details(self):
        return self.__interrogation_details
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
        if self.__mode != value:
            self.modeSub.on_next(value)
            
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
        # if self.question_count is not None:
        return self.__strategy.handle_interaction(self, user_input)
        # else:
        #     return '請稍後在試。'