from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from llm import get_ai_message

app = FastAPI()

class Message(BaseModel):
    content: str

@app.post("/message/", response_model=Message)
def process_message(message: Message):
    try:
        # AI 모델을 통해 메시지 처리
        requestContent = message.content + "카이스트 맛집 추천"
        ai_response = get_ai_message(requestContent)
        return {"content": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
