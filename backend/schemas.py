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