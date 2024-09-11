from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
import random
import math
import pandas as pd

from llm import get_ai_message
from Recommend import main

app = FastAPI()

# CORS 처리를 위한 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서의 접근을 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"]   # 모든 헤더 허용
)

class Reco(BaseModel):
    TRAVEL_STYL_1: int
    TRAVEL_STYL_5: int

class Message(BaseModel):
    content: List[str]

MONGO_DETAILS = "mongodb://10.178.0.3"
client = AsyncIOMotorClient(MONGO_DETAILS)
db = client["imagedb"]  # 데이터베이스 객체 생성
collection = db["image"]

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
    
    cursor = collection.aggregate([{"$sample": {"size": 15}}])
    random_data = await cursor.to_list(length=15)
    
    detailed_results = [
        [
            "https://storage.cloud.google.com/journey_mate_image/"+data.get("uri", ""),
            "" if pd.isna(data.get("road_nm", "")) else data.get("road_nm", ""),
            data.get("x", 0),
            data.get("y", 0),
            data.get("area", ""),
            data.get("description", "")
        ]
        for data in random_data
    ]
    
    return {"list": detailed_results}

@app.post("/message/")
def process_message(message: Message):
    try:
        places = ", ".join(f"\"{place}\"" for place in message.content)
        tour_description = f"{places} 이 여행지를 모두 포함한 관광코스를 작성해주세요."
        
        ai_response = get_ai_message(tour_description)
        
        return {"content": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
