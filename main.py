from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List

from llm import get_ai_message
from Recommend import main

app = FastAPI()

class Reco(BaseModel):
    TRAVEL_STYL_1: int
    TRAVEL_STYL_5: int

class Message(BaseModel):
    content: List[str]

MONGO_DETAILS = "mongodb://10.178.0.3"
client = AsyncIOMotorClient(MONGO_DETAILS)
db = client["imagedb"]  # 데이터베이스 객체 생성
collection = db["image"]

async def fetch_travel_data(area_name):
    """ MongoDB에서 주어진 지역 이름에 맞는 데이터를 조회합니다. """
    data = await collection.find_one({"area": area_name})
    return data if data else {}


@app.post("/recommend/")
async def recommend(reco: Reco):
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
    result_list = main(traveler)  # 이 함수는 area 이름 리스트를 반환한다고 가정합니다.
    print(result_list)
    detailed_results = [await fetch_travel_data(area) for area in result_list]
    return {"list": detailed_results}

@app.post("/message/")
def process_message(message: Message):
    try:
        places = ", ".join(f"\"{place}\"" for place in message.content)
        tour_description = f"{places} 이 여행지를 모두 포함한 관광코스를 작성해주세요."
        
        ai_response = get_ai_message(tour_description)
        
        # 결과를 동일한 구조로 반환
        return {"content": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
