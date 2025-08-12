from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    """Request model for a chat interaction."""
    user_input: str
    session_id: Optional[str] = None 

class ChatResponse(BaseModel):
    """Response model for a chat interaction."""
    output: str
    tool_used: Optional[str] = None