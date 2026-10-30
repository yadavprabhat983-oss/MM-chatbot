import re
from typing import Tuple, Optional

CRISIS_PATTERNS = [
    r"\b(i want to kill myself|i am going to kill myself|suicide|commit suicide|end my life|end it all)\b",
    r"\b(want to die|ready to die|take my own life|hang myself|slit my wrists)\b",
    r"\b(better off dead|no reason to live|can't go on living|hurt myself|cutting myself)\b",
    r"\b(plan to harm|going to hurt someone|kill others)\b",
]

CRISIS_RESPONSE = """It sounds like you are going through an overwhelming amount of pain right now, but please know that you do not have to carry this alone. 

I am an AI assistant and cannot provide medical care or emergency intervention, but there are compassionate, trained people available 24/7 who want to support you without judgment.

**Immediate Free & Confidential Help:**
- **United States & Canada:** Call or text **988**, or chat at [988lifeline.org](https://988lifeline.org/)
- **Crisis Text Line:** Text **HOME** to **741741**
- **United Kingdom:** Call **111** (NHS) or call Samaritans at **116 123**
- **International / Other Countries:** Find your local crisis helpline at [findahelpline.com](https://findahelpline.com/)
- **Immediate Danger:** Please call your local emergency services (like **911**, **999**, or **112**) or go to the nearest emergency room.

Please reach out to one of these resources, or to a trusted friend, family member, or professional right now. Your safety and well-being matter."""

EMOTIONAL_SUPPORT_SYSTEM_PROMPT = """You are a supportive, empathetic, and compassionate AI assistant.
Your goal is to provide everyday emotional support, active listening, and a safe, non-judgmental space.

Guidelines to follow:
1. Empathy First: Always validate and acknowledge the user's feelings warmly before jumping into suggestions or problem-solving.
2. Active Listening: Reflect back what you hear and ask gentle, open-ended clarifying questions.
3. Coping Tools: When helpful, gently offer practical coping strategies, such as:
   - The 5-4-3-2-1 grounding exercise (5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste).
   - Box breathing (inhale 4s, hold 4s, exhale 4s, hold 4s).
   - Reflective journaling prompts.
4. Professional Boundaries:
   - Clearly maintain that you are an AI assistant, not a human, therapist, counselor, or medical professional.
   - Never diagnose conditions or recommend medications.
   - Do not reinforce delusions, unhealthy dependencies, or harmful behaviors.
5. Tone: Warm, respectful, calm, and grounded. Respect the user's autonomy."""

class SafetyService:
    def check_crisis(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Checks if text contains explicit signs of imminent self-harm or crisis.
        Returns (is_crisis, crisis_response_text).
        """
        text_lower = text.lower()
        for pattern in CRISIS_PATTERNS:
            if re.search(pattern, text_lower):
                return True, CRISIS_RESPONSE
        return False, None

    def get_emotional_system_prompt(self) -> str:
        return EMOTIONAL_SUPPORT_SYSTEM_PROMPT

safety_service = SafetyService()
