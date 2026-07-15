from fastapi import FastAPI
from schemas import ProgressInput
from behavior_agent import BehaviorAgent

app = FastAPI()

agent = BehaviorAgent()

@app.post("/check-progress")
def check_progress(data: ProgressInput):

    return agent.check_progress(data)