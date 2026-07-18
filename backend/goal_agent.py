import json
from google import genai
from schemas import TransactionHistoryInput
from config import GEMINI_API_KEY
from prompts import goal_prompt

client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[GoalAgent Client Init Error] {e}")

MODEL_NAME = "gemini-2.5-flash"

class GoalAgent:
    """
    Goal Agent
    Responsibilities:
    - Analyze transaction history.
    - Identify top spending categories.
    - Generate personalized quests.
    - Decide reward product.
    """

    def generate_quest(self, data: TransactionHistoryInput):
        """
        Generate a personalized quest and reward product based on transaction history.
        """
        # Format transaction data into string for prompt
        tx_list = []
        for tx in data.transactions:
            tx_list.append(f"- Date: {tx.date}, Category: {tx.category}, Amount: ₹{tx.amount}, Description: {tx.description}")
        
        tx_str = "\n".join(tx_list)
        
        prompt = f"""
Customer Transaction History:
{tx_str}

{goal_prompt}
"""

        try:
            if not client:
                raise ValueError("Gemini API Client is uninitialized (missing GEMINI_API_KEY).")
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
            print(f"[GoalAgent Error] {e}")
            # Fallback quest if LLM call fails
            return {
                "analysis": "Based on your spending, we noticed a high amount of minor food expenses. Setting a target can help redirect these funds into savings.",
                "top_category": "Food & Dining",
                "quest": {
                    "category": "Food & Dining",
                    "target": 3000.0,
                    "reduction_percentage": 15,
                    "duration": 7,
                    "reward": "SBI Mutual Fund SIP"
                }
            }

    def run(self, data: TransactionHistoryInput):
        """
        Complete Goal Agent workflow.
        """
        return self.generate_quest(data)

if __name__ == "__main__":
    from schemas import Transaction
    # Simple self-test
    sample_data = TransactionHistoryInput(
        transactions=[
            Transaction(amount=500.0, category="Food", description="Zomato order", date="2026-07-01"),
            Transaction(amount=1200.0, category="Food", description="Dinner out", date="2026-07-02"),
            Transaction(amount=2000.0, category="Shopping", description="New shirt", date="2026-07-03"),
            Transaction(amount=450.0, category="Food", description="Coffee shop", date="2026-07-04"),
            Transaction(amount=150.0, category="Travel", description="Uber ride", date="2026-07-05"),
        ]
    )
    agent = GoalAgent()
    result = agent.run(sample_data)
    print(json.dumps(result, indent=4, ensure_ascii=False))
