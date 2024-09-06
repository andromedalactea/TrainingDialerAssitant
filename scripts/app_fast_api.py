from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
from bson import json_util, ObjectId

# Local imports
from components.call_calification import calificate_call, get_current_time_ny, save_calification_mongo

app = FastAPI()

# Load environment variables
load_dotenv(override=True)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client['TrainingDialer']

# Model for Call Data Input
class CallData(BaseModel):
    type: str
    call: dict
    transcript: str

@app.post("/calificate_call")
async def main_call(data: CallData):
    if data.type == "end-of-call-report":
        vapi_call_id = data.call.get("id")
        call_id = data.call["assistantOverrides"]["metadata"]["call_secundary_id"]
        reference = data.call["assistantOverrides"]["metadata"]["reference"]
        transcript = data.transcript
        
        calification = calificate_call(transcript)
        
        calification_dict = {
            "call_id": call_id,
            "vapi_call_id": vapi_call_id,
            "transcript": transcript,
            "calification": calification,
            "time": get_current_time_ny(),
            "reference": reference,
        }
        
        save_calification_mongo(calification_dict)
        return {"status": "success", "calification": calification}
    else:
        return {"status": "ignored"}

@app.get("/call_info")
async def get_call(call_id: str):
    collection = db['performanceCalification']
    call = collection.find_one({"call_id": call_id}, {'_id': 0})
    if call:
        return JSONResponse(content=json.loads(json_util.dumps(call)))
    else:
        raise HTTPException(status_code=404, detail="Call not found")

@app.get("/trained_models")
async def get_data():
    collection = db["TrainingDialerDB"]["trained_models"]
    documents = list(collection.find({}))
    return JSONResponse(content=json.loads(json_util.dumps(documents)))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
