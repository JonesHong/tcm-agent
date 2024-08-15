import __init__
from typing import Literal
from reactivex.subject.behaviorsubject import BehaviorSubject

from src.schemas._enum import AgentMode,InterrogationDetails,QaList
from src.services.agent_service.strategy import ChitchatStrategy, DiagnosticStrategy, EvaluationAndAdvice, InquiryStrategy, TongueDiagnosis
from src.utils.config.manager import ConfigManager
from src.utils.decorators.singleton import singleton
from src.utils.log import logger
from src.utils.redis.channel import RedisChannel
from src.utils.redis.core import RedisCore

config = ConfigManager()
agent_config = config.agent
redis_core = RedisCore()


@singleton
class AgentClass:
    user_info_from_yolo = None
    modeSub: BehaviorSubject

    def __init__(self):
        self.__mode = AgentMode[agent_config.mode]
        self.modeSub = BehaviorSubject(self.__mode)
        
        self.__question_count = 0
        self.__strategy = self._get_strategy(self.__mode)
        self.initial()

    def initial(self):
        self.user_info_from_yolo = None
        self.__sex: Literal['male', 'female'] = 'male'
        self.__messages = []
        self.__questions = {}
        self.__answers = {}
        self.question_count = 0
        self.mode = AgentMode[agent_config.mode]
        self.transformed_data = {"age": None, "male": None}

    def _get_strategy(self, mode):
        if mode == AgentMode.DIAGNOSTIC:
            return DiagnosticStrategy()
        elif mode == AgentMode.TONGUE_DIAGNOSIS:
            return TongueDiagnosis()
        elif mode == AgentMode.EVALUATION_ADVICE:
            return EvaluationAndAdvice()
        elif mode == AgentMode.INQUIRY:
            return InquiryStrategy()
        elif mode == AgentMode.CHITCHAT:
            return ChitchatStrategy()
        else:
            raise ValueError(f"Unsupported mode: {mode}")

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self, value):
        if self.__mode != value:
            self.modeSub.on_next(value)
            # redis_core.publisher(RedisChannel.agent_mode, self.__mode)

        self.__mode = value
        redis_core.setter(RedisChannel.agent_mode, self.__mode.value)
        self.__strategy = self._get_strategy(value)

    @property
    def sex(self) -> Literal['male', 'female']:
        return self.__sex

    @sex.setter
    def sex(self, value: Literal['male', 'female']):
        if value not in ['male', 'female']:
            raise ValueError("Sex must be 'male' or 'female'")
        self.__sex = value

    @property
    def messages(self):
        return self.__messages

    @property
    def qa(self):
        return QaList


    @property
    def questions(self):
        return self.__questions

    @property
    def answers(self):
        return self.__answers

    @property
    def question_count(self):
        return self.__question_count

    @question_count.setter
    def question_count(self, value):
        if value is None:
            pass
        elif value < self.__question_count:
            logger.info(
                f"請注意，此操作可能會導致重複回答已經回答過的問題。\n目前問題是關於:(問題{self.__question_count}){QaList[self.__question_count]}，你將回到(問題{value}){QaList[value]}。")
        elif value > self.__question_count and value != self.__question_count + 1:
            logger.info(
                f"請注意，此操作可能會導致問題被跳過。\n目前問題是關於:(問題{self.__question_count}){QaList[self.__question_count]}，你將跳到(問題{value}){QaList[value]}。")
        self.__question_count = value
        
        redis_core.setter(RedisChannel.agent_question_count, self.__question_count)

    def invoke(self, user_input):
        print(4654654646,user_input)
        return self.__strategy.handle_interaction(self, user_input)


Agent = AgentClass()
