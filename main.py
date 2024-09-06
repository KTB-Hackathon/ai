from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from llm import get_ai_message
from Recommend import main

app = FastAPI()

class Reco(BaseModel):
    TRAVEL_STYL_1: int
    TRAVEL_STYL_5: int

class Message(BaseModel):
    content: str


@app.post("/recommend/")
def recommend(reco: Reco):
    traveler = {
        'GENDER': '남',
        'AGE_GRP': 20.0,
        'TRAVEL_STYL_1': reco.TRAVEL_STYL_1,
        'TRAVEL_STYL_2': 2,
        'TRAVEL_STYL_3': 2,
        'TRAVEL_STYL_4': 3,
        'TRAVEL_STYL_5': reco.TRAVEL_STYL_5,
        'TRAVEL_STYL_6': 2,
        'TRAVEL_STYL_7': 2,
        'TRAVEL_STYL_8': 2,
        'TRAVEL_MOTIVE_1': 8,
        'TRAVEL_COMPANIONS_NUM': 0.0,
        'TRAVEL_MISSION_INT': 3
    }
    return {"list" : main(traveler)}

@app.post("/message/", response_model=Message)
def process_message(message: Message):
    try:
        fake_res = "\"독립기념관\",\"국립청주 박물관\",\"성심당 롯데백화점 대전점\",\"대전 오월드\",\"성심당 케이크 부티크\" 이 여행지를 모두 포함한 관광코스를 작성해주세요."
        # ai_response = get_ai_message(message.content)
        ai_response = get_ai_message(fake_res)
        return {"content": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
