from enum import Enum

class AgentMode(Enum):
    DIAGNOSTIC = "Diagnostic"  # Diagnostic mode for medical inquiry (問診模式")
    TONGUE_DIAGNOSIS = "TongueDiagnosis"  # Tongue diagnosis mode for health assessment (舌診模式)
    EVALUATION_ADVICE = "EvaluationAndAdvice"  # Evaluation and advice mode (評估和建議模式)
    INQUIRY = "Inquiry"    # Inquiry mode for general questions (自由提問模式)
    CHITCHAT = "Chitchat"      # Chitchat mode for casual conversation (閒聊模式)