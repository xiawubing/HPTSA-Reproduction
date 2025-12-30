from typing import TypedDict, List, Annotated, Dict, Optional
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    
    current_url: str
    
    exploration_history: List[Dict[str, str]]
    
    current_plan: str
    
    next_step: str
    
    execution_results: List[Dict[str, str]]

