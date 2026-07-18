from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    transactions: Optional[List[dict]]
    quest: Optional[dict]
    progress: Optional[dict]
    recovery: Optional[dict]
    notification: Optional[dict]
    learning_card: Optional[dict]
    product_name: Optional[str]