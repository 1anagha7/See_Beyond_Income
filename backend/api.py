from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from pydantic import BaseModel
import json

# Import custom modules
import database
from graph import agent_graph
import xp
import streak

router = APIRouter()

# -------------------------------------------------------
# Pydantic Schemas for Request/Response Validation
# -------------------------------------------------------

class UserResponse(BaseModel):
    id: str
    name: str
    xp: int
    streak: int
    level: int
    total_savings: float

class TransactionSchema(BaseModel):
    id: Optional[str] = None
    date: str
    category: str
    description: str
    amount: float

class SyncTransactionsRequest(BaseModel):
    transactions: List[TransactionSchema]

class QuestResponse(BaseModel):
    id: str
    category: str
    target: float
    reduction_percentage: float
    duration: int
    reward: str
    status: str
    current_spend: float
    current_day: int
    created_at: str
    analysis: Optional[str] = None

class ProgressCheckRequest(BaseModel):
    current_day: int
    current_spend: Optional[float] = None

class AdoptProductRequest(BaseModel):
    quest_id: str

# -------------------------------------------------------
# Endpoints
# -------------------------------------------------------

@router.get("/user", response_model=UserResponse)
def get_user_profile():
    """
    Fetches the profile details of the active user.
    """
    user = database.get_user("user_123")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/user/reset")
def reset_user_state():
    """
    Resets the database to its initial mock state (for demonstration purposes).
    """
    database.reset_db()
    return {"status": "success", "message": "Database reset to seed state successfully."}


@router.get("/transactions", response_model=List[TransactionSchema])
def get_transactions():
    """
    Gets transaction history for the user.
    """
    return database.get_transactions("user_123")


@router.post("/transactions", response_model=List[TransactionSchema])
def sync_transactions(data: SyncTransactionsRequest):
    """
    Synchronizes mock transactions edited/added on the frontend.
    Also dynamically updates the current spend of the active quest if applicable.
    """
    txs_dict = [tx.model_dump() for tx in data.transactions]
    updated_txs = database.set_transactions("user_123", txs_dict)
    
    # Recalculate spend on active quest if one exists
    active_quest = database.get_active_quest("user_123")
    if active_quest:
        category = active_quest["category"]
        # Sum transaction amounts matching this category
        matching_spend = sum(
            tx["amount"] for tx in updated_txs 
            if tx["category"].lower() == category.lower()
        )
        database.update_quest_progress(
            active_quest["id"], 
            matching_spend, 
            active_quest["current_day"], 
            active_quest["status"]
        )
        
    return updated_txs


@router.get("/quest/active")
def get_active_quest():
    """
    Retrieves the currently active quest for the user.
    """
    quest = database.get_active_quest("user_123")
    if not quest:
        return None
    return quest


@router.post("/generate-quest")
def generate_quest(data: Optional[SyncTransactionsRequest] = None):
    """
    Invokes LangGraph to analyze transaction history, generate a quest,
    and save it in the database.
    If a transaction payload is provided, syncs it in the database first.
    """
    if data and data.transactions:
        txs_dict = [tx.model_dump() for tx in data.transactions]
        database.set_transactions("user_123", txs_dict)
        
    txs = database.get_transactions("user_123")
    if not txs:
        raise HTTPException(status_code=400, detail="Cannot generate quest with empty transactions.")
        
    # Prepare input for LangGraph
    state_input = {
        "transactions": txs
    }
    
    try:
        # Run orchestrator
        graph_output = agent_graph.invoke(state_input)
        quest_data = graph_output.get("quest")
        
        if not quest_data or "quest" not in quest_data:
            raise HTTPException(status_code=500, detail="Failed to parse quest from Goal Agent.")
            
        analysis = quest_data.get("analysis", "")
        quest_details = quest_data["quest"]
        
        # Save active quest
        quest_id = database.save_quest("user_123", quest_details, analysis)
        
        # Earn XP for starting a quest (+100 XP)
        database.update_user_gamification("user_123", xp_gain=100)
        
        # Retrieve the updated quest
        saved_quest = database.get_active_quest("user_123")
        return saved_quest
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-progress")
def check_progress(data: ProgressCheckRequest):
    """
    Performs behavioral checks, drift detection, and motivational nudges
    for the active quest using LangGraph. Updates gamification states.
    """
    active_quest = database.get_active_quest("user_123")
    if not active_quest:
        raise HTTPException(status_code=400, detail="No active quest to check progress on.")
        
    # Calculate spend dynamically if not provided
    current_spend = data.current_spend
    if current_spend is None:
        txs = database.get_transactions("user_123")
        category = active_quest["category"]
        current_spend = sum(
            tx["amount"] for tx in txs 
            if tx["category"].lower() == category.lower()
        )
        
    # Construct state for LangGraph
    state_input = {
        "quest": active_quest,
        "progress": {
            "current_spend": current_spend,
            "current_day": data.current_day
        }
    }
    
    try:
        graph_output = agent_graph.invoke(state_input)
        
        progress = graph_output.get("progress", {})
        recovery = graph_output.get("recovery", {})
        notification = graph_output.get("notification", {})
        
        status = progress.get("status", "On Track")
        is_recovery_needed = progress.get("recovery_needed", False)
        
        # Calculate gamification changes
        user = database.get_user("user_123")
        current_streak = user["streak"]
        
        new_streak = streak.calculate_new_streak(
            current_streak=current_streak, 
            status=status,
            completed_recovery=False
        )
        
        xp_gain = xp.get_xp_for_action("daily_check", status)
        
        database.update_user_gamification(
            "user_123", 
            xp_gain=xp_gain, 
            streak_val=new_streak
        )
        
        nudge_message = None
        if is_recovery_needed and notification:
            nudge_message = notification.get("notification", "")
            # Log nudge to notification/WhatsApp simulator database
            database.add_notification("user_123", nudge_message, "whatsapp")
            
        # Update quest progress in the DB
        database.update_quest_progress(
            active_quest["id"], 
            current_spend, 
            data.current_day, 
            "active"
        )
        
        return {
            "progress": progress,
            "recovery": recovery,
            "nudge": nudge_message,
            "gamification": {
                "xp_earned": xp_gain,
                "new_streak": new_streak
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-learning-card")
def generate_learning_card(payload: dict = Body(...)):
    """
    Generates a 30-second explainer for the SBI product unlocked by the quest.
    """
    active_quest = database.get_active_quest("user_123")
    product_name = payload.get("product_name")
    
    if not product_name and active_quest:
        product_name = active_quest["reward"]
        
    if not product_name:
        raise HTTPException(status_code=400, detail="Product name is required.")
        
    # Check if we already have it in DB
    if active_quest:
        existing_lc = database.get_learning_card(active_quest["id"])
        if existing_lc:
            return existing_lc
            
    # Compile state for LangGraph
    state_input = {
        "product_name": product_name
    }
    
    try:
        graph_output = agent_graph.invoke(state_input)
        lc_data = graph_output.get("learning_card")
        
        # Save to DB if quest is active
        if active_quest:
            database.save_learning_card(active_quest["id"], lc_data)
            # Award +100 XP for unlocking learning gate
            database.update_user_gamification("user_123", xp_gain=100)
            
        return lc_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/adopt-product")
def adopt_reward_product(data: AdoptProductRequest):
    """
    Handles SBI deep link clicks. Marks product as adopted, rewards commission to the bank,
    rewards user with +1000 XP and completes the quest.
    """
    active_quest = database.get_active_quest("user_123")
    if not active_quest or active_quest["id"] != data.quest_id:
        # Fallback to verify historical or retrieve specific
        # We can adopt it directly
        pass
        
    database.adopt_product(data.quest_id)
    return {"status": "success", "message": "Product adopted successfully! 1000 XP rewarded."}


@router.get("/notifications")
def get_user_notifications():
    """
    Returns WhatsApp notification log.
    """
    return database.get_notifications("user_123")


@router.get("/bank/metrics")
def get_bank_analytics():
    """
    Calculates analytical metrics and revenue projections for the bank.
    """
    return database.get_bank_metrics()


@router.get("/bank/customers")
def get_bank_customer_directory():
    """
    Fetches engagement directory profiles for all customers.
    """
    return database.get_all_customers()
