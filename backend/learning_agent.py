import json
from google import genai
from schemas import LearningInput
from config import GEMINI_API_KEY
from prompts import learning_prompt

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

class LearningAgent:
    """
    FinPilot Adaptive Learning Agent
    Responsibilities:
    - Analyzes user's spending struggle and active quest.
    - Dynamically selects an educational topic (SIP, Emergency Fund, Subscription Audit, etc.).
    - Generates a tailored 30-second explainer with key takeaways and an actionable next step.
    """

    def generate_learning_card(self, data: LearningInput):
        prompt = f"""
USER FINANCIAL CONTEXT:
- Spending Category: {data.category}
- Active Quest: {data.quest_title}
- Financial Struggle / Context: {data.struggle_context}

{learning_prompt}
"""

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if not response.text:
                raise ValueError("Empty response from Gemini.")

            clean_text = (
                response.text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            return json.loads(clean_text)

        except Exception as e:
            print(f"[FinPilot LearningAgent Error] {e}")
            # Fallback adaptive content
            return {
                "topic_title": "Automated Micro-Investing (SIP)",
                "subtitle": "Turn your saved quest money into compound wealth",
                "explainer_30s": f"By completing your '{data.quest_title}' quest, you free up cash flow. Instead of letting it sit idle, automatically channeling it into a Systematic Investment Plan (SIP) uses compounding interest to grow your savings exponentially without manual effort.",
                "key_takeaways": [
                    "Automated monthly or weekly contributions",
                    "Dollar-cost averaging reduces market volatility risk",
                    "Compounding turns small savings into substantial capital"
                ],
                "recommended_action": "Set up a ₹500 recurring monthly auto-sip with your quest savings."
            }

    def run(self, data: LearningInput):
        return self.generate_learning_card(data)


if __name__ == "__main__":
    sample_data = LearningInput(
        category="Food & Dining",
        quest_title="Trim Weekend Dining",
        struggle_context="72% of food spend happens on weekend impulse orders."
    )
    agent = LearningAgent()
    result = agent.run(sample_data)
    print(json.dumps(result, indent=4, ensure_ascii=True))

