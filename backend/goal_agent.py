import json
from datetime import datetime
from google import genai
from schemas import TransactionHistoryInput
from config import GEMINI_API_KEY
from prompts import goal_prompt

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

class DataProcessingEngine:
    """
    Deterministic Analytics & Behavior Processing Engine
    Calculates statistical facts from raw transactions before passing to LLM.
    """

    @staticmethod
    def analyze_transactions(transactions):
        total_spend = 0.0
        category_totals = {}
        weekend_spend = {}
        weekday_spend = {}
        recurring_transactions = []

        subscription_keywords = ["netflix", "spotify", "prime", "sub", "membership", "bill", "recharge"]

        for tx in transactions:
            amount = tx.amount
            category = tx.category.strip()
            desc = tx.description.lower()
            date_str = tx.date

            total_spend += amount

            # Category totals
            category_totals[category] = category_totals.get(category, 0.0) + amount

            # Check weekend (5 = Saturday, 6 = Sunday)
            is_weekend = False
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if dt.weekday() >= 5 or "friday night" in desc:
                    is_weekend = True
            except Exception:
                pass

            if is_weekend:
                weekend_spend[category] = weekend_spend.get(category, 0.0) + amount
            else:
                weekday_spend[category] = weekday_spend.get(category, 0.0) + amount

            # Recurring / Subscription check
            if any(kw in desc for kw in subscription_keywords):
                recurring_transactions.append({"desc": tx.description, "amount": amount, "category": category})

        # Top Category
        top_category = max(category_totals, key=category_totals.get) if category_totals else "General"
        top_cat_total = category_totals.get(top_category, 0.0)
        top_cat_weekend = weekend_spend.get(top_category, 0.0)
        top_cat_weekend_pct = round((top_cat_weekend / top_cat_total * 100), 1) if top_cat_total > 0 else 0

        analytics_summary = {
            "total_spend": round(total_spend, 2),
            "top_category": top_category,
            "top_category_spend": round(top_cat_total, 2),
            "top_category_weekend_spend": round(top_cat_weekend, 2),
            "top_category_weekend_pct": top_cat_weekend_pct,
            "category_breakdown": {k: round(v, 2) for k, v in category_totals.items()},
            "recurring_detected": recurring_transactions
        }

        return analytics_summary


class GoalAgent:
    """
    FinPilot Goal Agent
    Responsibilities:
    - Run Deterministic Analytics Engine.
    - Feed computed facts to Gemini for explainable quest design.
    - Return actionable mission with data-backed reasoning.
    """

    def __init__(self):
        self.engine = DataProcessingEngine()

    def generate_quest(self, data: TransactionHistoryInput):
        # 1. Deterministic Analysis Engine
        analytics = self.engine.analyze_transactions(data.transactions)

        # 2. Formulate Prompt with Pre-computed Analytics
        prompt = f"""
DETERMINISTIC ANALYTICS SUMMARY:
- Total Spending across all categories: ₹{analytics['total_spend']:,.2f}
- Highest Spending Category: {analytics['top_category']} (₹{analytics['top_category_spend']:,.2f})
- Weekend Spending in {analytics['top_category']}: ₹{analytics['top_category_weekend_spend']:,.2f} ({analytics['top_category_weekend_pct']}% of category total)
- Category Breakdown: {json.dumps(analytics['category_breakdown'])}
- Recurring Subscriptions Found: {json.dumps(analytics['recurring_detected'])}

{goal_prompt}
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

            result = json.loads(clean_text)
            # Attach analytics engine output to response for frontend dashboard visualization
            result["analytics"] = analytics
            return result

        except Exception as e:
            print(f"[FinPilot GoalAgent Error] {e}")
            top_cat = analytics['top_category']
            top_total = analytics['top_category_spend']
            wknd_pct = analytics['top_category_weekend_pct']
            target = round(top_total * 0.2, 2)

            return {
                "quest_title": f"Trim {top_cat} Spending",
                "top_category": top_cat,
                "target_reduction": target,
                "duration_days": 7,
                "why_reasoning": f"You spent ₹{top_total:,.0f} on {top_cat}, and {wknd_pct}% occurred over weekends. Reducing just 2 impulse orders will save ₹{target:,.0f}.",
                "reward_product": "FinPilot Automated SIP",
                "analytics": analytics
            }

    def run(self, data: TransactionHistoryInput):
        return self.generate_quest(data)


if __name__ == "__main__":
    from schemas import Transaction
    sample_data = TransactionHistoryInput(
        transactions=[
            Transaction(amount=850.0, category="Food & Dining", description="Zomato Order", date="2026-07-11"),
            Transaction(amount=2400.0, category="Food & Dining", description="Friday Night Dinner", date="2026-07-10"),
            Transaction(amount=1200.0, category="Shopping", description="Amazon Purchase", date="2026-07-12"),
            Transaction(amount=650.0, category="Food & Dining", description="Swiggy Weekend", date="2026-07-11"),
            Transaction(amount=300.0, category="Transport", description="Uber Ride", date="2026-07-13"),
        ]
    )
    agent = GoalAgent()
    result = agent.run(sample_data)
    print(json.dumps(result, indent=4, ensure_ascii=True))

