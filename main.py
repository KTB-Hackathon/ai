from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from llm import get_ai_message

app = FastAPI()

class Message(BaseModel):
    content: str

@app.post("/message/", response_model=Message)
def process_message(message: Message):
    try:
        print(message.content)
        ai_response = get_ai_message(message.content)
        return {"content": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
