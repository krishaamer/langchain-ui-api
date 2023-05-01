import threading

from fastapi import APIRouter
from starlette.responses import StreamingResponse
from pydantic import BaseModel
from decouple import config
from queue import Queue

from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.callbacks.base import CallbackManager
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback

from lib.db import supabase as supabase_client
from lib.prompts import default_prompt
from lib.callbacks import StreamingLLMCallbackHandler


class Chatbot(BaseModel):
    message: str
        
        
router = APIRouter()

@router.post("/chatbots/{chatbot_id}", name="Chatbot", description="Chatbot endpoint")
async def chatbot(chatbot_id: int, body: Chatbot):
    """Chatbot endpoint"""
    message = body.message
    messages = supabase_client.table('ChatbotMessage').select("*").eq(
            'id', chatbot_id
        ).execute()
    history = ChatMessageHistory()
    history = [history.add_ai_message(chat_message["message"])
            if chat_message["agent"] == "ai"
            else history.add_user_message(chat_message["message"]) 
            for chat_message in messages.data]
    
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
            
    def conversation_run_thread(message, history):
        with get_openai_callback() as cb:  
            memory = ConversationBufferMemory(memory_key="chat_history")
            llm = ChatOpenAI(
                streaming=True, 
                openai_api_key=config("OPENAI_API_KEY"),  
                verbose=True,
                callback_manager=CallbackManager(
                    [StreamingLLMCallbackHandler(on_llm_new_token, on_llm_end)]
                )
            )
            conversation = LLMChain(
                llm=llm,
                memory=memory,
                prompt=default_prompt,
                verbose=True
            )
            conversation.run({
                "human_input": message, 
                "chat_history": history
            })
    
    data_queue = Queue()
    t = threading.Thread(
        target=conversation_run_thread, 
        args=(message, history)
    )
    t.start()
    response = StreamingResponse(
        event_stream(data_queue), 
        media_type='text/event-stream'
    )
    return response
