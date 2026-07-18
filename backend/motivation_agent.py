import json

from google import genai

from schemas import MotivationInput
from config import GEMINI_API_KEY
from prompts import motivation_prompt


# -------------------------------------------------------
# Initialize Gemini Client
# -------------------------------------------------------

client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[MotivationAgent Client Init Error] {e}")

MODEL_NAME = "gemini-2.5-flash"


class MotivationAgent:
    """
    Motivation Agent

    Responsibilities:
    - Generate personalized motivational nudges.
    - Encourage positive financial behaviour.
    - Create WhatsApp-style notifications.
    """

    def generate_notification(self, data: MotivationInput):
        """
        Generate a motivational notification using Gemini.
        """

        prompt = f"""
Customer Status: {data.status}

Spending Gap: ₹{data.gap:,.0f}

Days Remaining: {data.days_left}

Financial Summary:
{data.summary}

Recovery Challenge:
{data.recovery_quest}

{motivation_prompt}
"""

        try:
            if not client:
                raise ValueError("Gemini API Client is uninitialized (missing GEMINI_API_KEY).")

            response = client.models.generate_content(
                model= MODEL_NAME,
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

            print(f"[MotivationAgent Error] {e}")

            return {
                "notification": (
                    "Every small financial decision counts. "
                    "Complete today's recovery challenge and keep moving toward your financial goal!"
                )
            }

    def run(self, data: MotivationInput):
        """
        Complete Motivation Agent workflow.
        """

        return self.generate_notification(data)


# -------------------------------------------------------
# Local Testing
# -------------------------------------------------------

if __name__ == "__main__":

    sample_data = MotivationInput(
        status="Behind",
        gap=1750,
        days_left=15,
        summary=(
            "You've currently spent ₹3,000 on food, exceeding your expected "
            "spend of ₹1,250 by ₹1,750."
        ),
        recovery_quest=(
            "Prepare your meals at home instead of ordering food online."
        )
    )

    agent = MotivationAgent()

    result = agent.run(sample_data)

    print(json.dumps(result, indent=4, ensure_ascii=False))