from typing import Literal
from langgraph.graph import StateGraph, END
from state import AgentState
from goal_agent import GoalAgent
from behavior_agent import BehaviorAgent
from motivation_agent import MotivationAgent
from learning_agent import LearningAgent
from schemas import (
    TransactionHistoryInput, 
    Transaction, 
    ProgressInput, 
    Quest, 
    MotivationInput, 
    LearningInput
)

# Initialize components
goal_agent = GoalAgent()
behavior_agent = BehaviorAgent()
motivation_agent = MotivationAgent()
learning_agent = LearningAgent()

# -------------------------------------------------------
# Node Implementations
# -------------------------------------------------------

def goal_node(state: AgentState):
    """
    Analyzes transactions and outputs quest + reward.
    """
    tx_list = []
    for tx in state.get("transactions", []):
        tx_list.append(Transaction(
            amount=float(tx.get("amount", 0)),
            category=tx.get("category", "General"),
            description=tx.get("description", ""),
            date=tx.get("date", "")
        ))
        
    data = TransactionHistoryInput(transactions=tx_list)
    result = goal_agent.run(data)
    
    # Save the resulting structure back into state
    return {"quest": result}


def behavior_node(state: AgentState):
    """
    Checks spending progress and detects drift.
    """
    active_quest = state.get("quest")
    if not active_quest:
        raise ValueError("No active quest in state for progress check.")
        
    # The saved quest might have a nested quest structure from GoalAgent output
    q_data = active_quest.get("quest", active_quest)
    
    quest_obj = Quest(
        category=q_data["category"],
        target=float(q_data["target"]),
        duration=int(q_data["duration"]),
        reward=q_data["reward"]
    )
    
    progress_data = state["progress"]
    
    data = ProgressInput(
        quest=quest_obj,
        current_spend=float(progress_data["current_spend"]),
        current_day=int(progress_data["current_day"])
    )
    
    result = behavior_agent.run(data)
    
    # Return updates for progress and recovery
    return {
        "progress": result["progress"],
        "recovery": result.get("recovery", {})
    }


def motivation_node(state: AgentState):
    """
    Generates an empathetic WhatsApp nudge for customers who fall behind.
    """
    progress = state["progress"]
    recovery = state["recovery"]
    
    data = MotivationInput(
        status=progress["status"],
        gap=float(progress["gap"]),
        days_left=int(progress["days_left"]),
        summary=recovery.get("summary", ""),
        recovery_quest=recovery.get("recovery_quest", "")
    )
    
    result = motivation_agent.run(data)
    
    return {"notification": result}


def learning_node(state: AgentState):
    """
    Unlocks the learning explainer for the SBI reward product.
    """
    product_name = state.get("product_name")
    
    data = LearningInput(product_name=product_name)
    result = learning_agent.run(data)
    
    return {"learning_card": result}


# -------------------------------------------------------
# Graph Routing & Setup
# -------------------------------------------------------

def route_progress(state: AgentState) -> Literal["motivation_agent", "__end__"]:
    """
    Determines whether a motivation nudge is needed.
    """
    progress = state.get("progress")
    if progress and progress.get("recovery_needed"):
        return "motivation_agent"
    return END


def route_entry(state: AgentState) -> Literal["goal_agent", "behavior_agent", "learning_agent", "__end__"]:
    """
    Conditional entry point routing to start at the correct node.
    """
    if state.get("transactions") is not None:
        return "goal_agent"
    elif state.get("progress") is not None and "current_spend" in state["progress"]:
        return "behavior_agent"
    elif state.get("product_name") is not None:
        return "learning_agent"
    return END


# Compile the LangGraph
workflow = StateGraph(AgentState)

workflow.add_node("goal_agent", goal_node)
workflow.add_node("behavior_agent", behavior_node)
workflow.add_node("motivation_agent", motivation_node)
workflow.add_node("learning_agent", learning_node)

# Connect edges
workflow.add_conditional_edges(
    "behavior_agent",
    route_progress,
    {
        "motivation_agent": "motivation_agent",
        END: END
    }
)

workflow.add_edge("motivation_agent", END)
workflow.add_edge("goal_agent", END)
workflow.add_edge("learning_agent", END)

workflow.set_conditional_entry_point(
    route_entry,
    {
        "goal_agent": "goal_agent",
        "behavior_agent": "behavior_agent",
        "learning_agent": "learning_agent",
        END: END
    }
)

# Export the compiled graph
agent_graph = workflow.compile()
