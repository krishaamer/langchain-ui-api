from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

from lib.db import supabase as supabase_client


class Chatbot(BaseModel):
    message: str


app = FastAPI()
router = APIRouter()

@router.post("/chatbots/{chatbot_id}", name="Chatbot", description="Chatbot endpoint")
async def chatbot(chatbot_id: int, body: Chatbot):
    """Chatbot endpoint"""
    chatbot = supabase_client.table('Chatbot').select("*").execute()
    message = body.message
    return {"chatbot": chatbot}
    
    