from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from app.models.chat_models import ChatRequest, ChatResponse
from app.core.agent import run_agent
from app.services.firebase_service import (
    verify_firebase_token, 
    save_message_to_firestore, 
    get_conversations_from_firestore,
    delete_conversation_from_firestore,
    delete_single_session_from_firestore
)

from app.services.vector_db_service import add_text_to_vector_db
from app.core.crews.blog_crew import create_blog_post_crew

router = APIRouter()

class CrewRequest(BaseModel):
    topic: str

# FIXED: Custom dependency to extract Firebase token from Authorization header
def get_firebase_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = auth_header.split("Bearer ")[1]
    return token

# FIXED: Custom dependency to verify Firebase token and get user data
def get_current_user(token: str = Depends(get_firebase_token)) -> dict:
    try:
        user_data = verify_firebase_token(token)
        if not user_data or not user_data.get('uid'):
            raise HTTPException(status_code=401, detail="Invalid or expired authentication token.")
        return user_data
    except Exception as e:
        print(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token.")

@router.post("", response_model=ChatResponse)
async def handle_chat(request: ChatRequest, user_data: dict = Depends(get_current_user)):
    user_id = user_data['uid']

    # --- THIS IS THE FIX ---
    # We save the user's message to both databases BEFORE running the agent.
    add_text_to_vector_db(
        user_id=user_id,
        text=request.user_input,
        metadata={'sender': 'user', 'session_id': request.session_id}
    )
    save_message_to_firestore(user_id, request.session_id, 'user', request.user_input)

    # Run the agent to get a response
    agent_result = run_agent(request.user_input, request.session_id, user_id)
    agent_output = agent_result.get("output", "I'm sorry, I encountered an error and couldn't process your request.")
    
    # And we save the agent's response to both databases AFTER it has been generated.
    add_text_to_vector_db(
        user_id=user_id,
        text=agent_output,
        metadata={'sender': 'agent', 'session_id': request.session_id}
    )
    save_message_to_firestore(user_id, request.session_id, 'agent', agent_output)
    
    return ChatResponse(output=agent_output)

@router.post("/invoke_crew")
async def handle_crew_invocation(request: CrewRequest, user_data: dict = Depends(get_current_user)):
    if not request.topic:
        raise HTTPException(status_code=400, detail="A topic is required.")
    try:
        result = create_blog_post_crew(request.topic)
        return {"result": result}
    except Exception as e:
        print(f"Error during crew invocation: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while the AI crew was working.")

@router.get("/history")
async def get_chat_history(user_data: dict = Depends(get_current_user)):
    user_id = user_data['uid']
    conversations = get_conversations_from_firestore(user_id)
    if conversations is None:
        raise HTTPException(status_code=500, detail="Could not fetch conversation history.")
    return {"history": conversations}

@router.delete("/history")
async def delete_chat_history(user_data: dict = Depends(get_current_user)):
    user_id = user_data['uid']
    success = delete_conversation_from_firestore(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete conversation history.")
    return {"message": "Conversation history deleted successfully."}

@router.delete("/history/{session_id}")
async def delete_single_chat_session(session_id: str, user_data: dict = Depends(get_current_user)):
    user_id = user_data['uid']
    success = delete_single_session_from_firestore(user_id, session_id)
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to delete session {session_id}.")
    return {"message": f"Session {session_id} deleted successfully."}