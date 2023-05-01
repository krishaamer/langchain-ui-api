import threading

from fastapi import APIRouter
from starlette.responses import StreamingResponse
from pydantic import BaseModel
from decouple import config
from queue import Queue

from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback

from lib.db import supabase as supabase_client
from lib.callbacks import StreamingLLMCallbackHandler


class Chatbot(BaseModel):
    message: str
        
        
router = APIRouter()



@router.post("/chatbots/{chatbot_id}", name="Chatbot", description="Chatbot endpoint")
async def chatbot(chatbot_id: int, body: Chatbot):
    """Chatbot endpoint"""
    payload = body.message
    messages = supabase_client.table('ChatbotMessage').select("*").eq(
            'chatbotId', chatbot_id
        ).order(column="createdAt", desc=True).limit(size=4).execute()
    history = ChatMessageHistory()
    [history.add_ai_message(message["message"])
     if message["agent"] == "ai" 
     else history.add_user_message(message["message"]) 
     for message in messages.data]
    
    def on_llm_new_token(token: str) -> None:
        data_queue.put(token)
        
    def on_llm_end() -> None:
        data_queue.put("CLOSE")
    
    def event_stream(data_queue: Queue) -> str:
        while True:
            data = data_queue.get()
            if data == "CLOSE":
                yield f"data: {data}\n\n"
                break
            yield f"data: {data}\n\n"
            
    def conversation_run_thread(payload: str) -> None:
        with get_openai_callback() as cb:  
            memory = ConversationBufferMemory(chat_memory=history)
            llm = ChatOpenAI(
                streaming=True, 
                openai_api_key=config("OPENAI_API_KEY"),  
                verbose=True,
                callbacks=[StreamingLLMCallbackHandler(on_llm_new_token, on_llm_end)]
            )
            conversation = LLMChain(
                llm=llm,
                memory=memory,
                verbose=True
            )
            conversation.run(payload)

    data_queue = Queue()
    t = threading.Thread(target=conversation_run_thread, args=(payload,))
    t.start()
    response = StreamingResponse(
        event_stream(data_queue), 
        media_type='text/event-stream'
    )
    return response
