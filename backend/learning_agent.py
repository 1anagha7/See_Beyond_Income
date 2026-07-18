import json
from google import genai
from schemas import LearningInput
from config import GEMINI_API_KEY
from prompts import learning_prompt

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

class LearningAgent:
    """
    Learning Agent
    Responsibilities:
    - Generate 30-second explainers.
    - Create product cards features and taglines.
    - Assist in unlocking learning gates.
    """

    def generate_learning_card(self, data: LearningInput):
        """
        Generate a 30-second explainer and product card details.
        """
        prompt = f"""
Product Name: {data.product_name}

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
            print(f"[LearningAgent Error] {e}")
            # Fallback learning details
            return {
                "product_name": data.product_name,
                "subtitle": "Smart wealth creation in tiny steps",
                "explainer": f"The {data.product_name} allows you to grow your wealth systematically. By investing a small amount regularly, you benefit from compounding interest and rupee cost averaging, making financial growth effortless and disciplined over time.",
                "benefits": [
                    "Start with as little as ₹500/month",
                    "Compounding growth over time",
                    "Automated, hassle-free investments"
                ]
            }

    def run(self, data: LearningInput):
        """
        Complete Learning Agent workflow.
        """
        return self.generate_learning_card(data)

if __name__ == "__main__":
    sample_data = LearningInput(product_name="SBI Mutual Fund SIP")
    agent = LearningAgent()
    result = agent.run(sample_data)
    print(json.dumps(result, indent=4, ensure_ascii=False))
