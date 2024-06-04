from enum import Enum

class AgentMode(Enum):
    DIAGNOSTIC = "Diagnostic"  # Diagnostic mode for medical inquiry (問診模式")
    INQUIRY = "Inquiry"    # Inquiry mode for general questions (自由提問模式)
    CHITCHAT = "Chitchat"      # Chitchat mode for casual conversation (閒聊模式)