from pydantic import BaseModel


class Quest(BaseModel):
    category: str
    target: float
    duration: int
    reward: str


class ProgressInput(BaseModel):
    quest: Quest
    current_spend: float
    current_day: int
    
class MotivationInput(BaseModel):
    status: str
    gap: float
    days_left: int
    summary: str
    recovery_quest: str


class Transaction(BaseModel):
    amount: float
    category: str
    description: str
    date: str


class TransactionHistoryInput(BaseModel):
    transactions: list[Transaction]


class LearningInput(BaseModel):
    category: str = "General"
    quest_title: str = "Budget Challenge"
    struggle_context: str = "High discretionary spending"
