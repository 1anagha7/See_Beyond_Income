import json

from google import genai

from schemas import ProgressInput
from config import GEMINI_API_KEY
from prompts import behavior_prompt


# -------------------------------------------------------
# Initialize Gemini Client
# -------------------------------------------------------

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

class BehaviorAgent:
    """
    Behavior Agent

    Responsibilities:
    - Analyse customer spending behaviour.
    - Detect behavioural drift.
    - Generate personalized recovery challenges.
    """

    def analyze_progress(self, data: ProgressInput):
        """
        Compare expected spending with actual spending.
        """

        expected_spend = (
            data.quest.target / data.quest.duration
        ) * data.current_day

        gap = round(data.current_spend - expected_spend, 2)

        return {
            "status": "On Track" if gap <= 0 else "Behind",
            "expected_spend": round(expected_spend, 2),
            "actual_spend": data.current_spend,
            "gap": abs(gap) if gap <= 0 else gap,
            "days_left": data.quest.duration - data.current_day,
            "recovery_needed": gap > 0
        }

    def generate_recovery(self, data: ProgressInput, progress: dict):
        """
        Generate a personalized recovery challenge using Gemini.
        """

        prompt = f"""
    
    Status: {progress['status']}

    Quest Category: {data.quest.category}

    Expected Spend Till Today: ₹{progress['expected_spend']:,.0f}

    Actual Spend Till Today: ₹{progress['actual_spend']:,.0f}

    Spending Gap: ₹{progress['gap']:,.0f}

    Days Remaining: {progress['days_left']}

    Reward Product: {data.quest.reward}

    {behavior_prompt}
    """

        try:

            response = client.models.generate_content(
                model = MODEL_NAME,
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

            print(f"[BehaviorAgent Error] {e}")

            return {
                "summary": (
                    "You're currently spending faster than planned. "
                    "There's still enough time to recover with a few mindful choices."
                ),
                "recovery_quest": (
                    "Reduce spending in your highest expense category over the next "
                    "two days and review every purchase before making it."
                )
            }

    def run(self, data: ProgressInput):
        """
        Complete Behavior Agent workflow.
        """

        progress = self.analyze_progress(data)

        if progress["recovery_needed"]:

            recovery = self.generate_recovery(
                data,
                progress
            )

            return {
                "progress": progress,
                "recovery": recovery,

                "motivation_input": {
                    "status": progress["status"],
                    "gap": progress["gap"],
                    "days_left": progress["days_left"],
                    "summary": recovery["summary"],
                    "recovery_quest": recovery["recovery_quest"]
                }
            }

        return {
            "progress": progress,
            "message": "Customer is on track. No recovery challenge required."
        }


# -------------------------------------------------------
# Local Testing
# -------------------------------------------------------

if __name__ == "__main__":

    sample_data = ProgressInput(
        quest={
            "category": "Food",
            "target": 2500,
            "duration": 30,
            "reward": "SIP"
        },
        current_spend=3000,
        current_day=15
    )

    agent = BehaviorAgent()

    result = agent.run(sample_data)

    print(json.dumps(result, indent=4, ensure_ascii=False))