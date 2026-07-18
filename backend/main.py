from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import ProgressInput, TransactionHistoryInput, LearningInput
from behavior_agent import BehaviorAgent
from goal_agent import GoalAgent
from learning_agent import LearningAgent

app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

behavior_agent = BehaviorAgent()
goal_agent = GoalAgent()
learning_agent = LearningAgent()

@app.post("/check-progress")
def check_progress(data: ProgressInput):
    return behavior_agent.run(data)

@app.post("/generate-quest")
def generate_quest(data: TransactionHistoryInput):
    return goal_agent.run(data)

@app.post("/generate-learning-card")
def generate_learning_card(data: LearningInput):
    return learning_agent.run(data)