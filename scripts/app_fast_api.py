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


@app.post("/api/calificate_call")
async def main_call( data: dict):
    """Webhook endpoint that receives POST requests and processes call transcriptions."""   
    
    message = data.get("message")
    if  message.get("type") == "end-of-call-report":

        # Extract call id of vapi
        call_info = message.get("call")
        vapi_call_id = call_info.get("id")

        # Extract call id
        call_data = message.get("call", {})
        call_id = message["call"]["assistantOverrides"]["metadata"]["call_secundary_id"]
        reference = message["call"]["assistantOverrides"]["metadata"]["reference"]
        
        
        # Extract the transcript from the message
        transcript = message.get("transcript")
        
        # Generate the calification
        calification = calificate_call(transcript)
        
        # Prepare the dictionary to be saved
        calification_dict = {
            "call_id": call_id,
            "vapi_call_id": vapi_call_id,
            "transcript": transcript,
            "calification": calification,
            "time" : get_current_time_ny(),
            "reference": reference,
        }

        # Save the calification in a file like a jsonl
        save_calification_mongo(calification_dict)
        print("Calification saved")
        return {"status": "success", "calification": calification}
    else:
        return {"status": "ignored"}

@app.get("/api/call_info")
async def get_call(call_id: str):
    collection = db['performanceCalification']
    call = collection.find_one({"call_id": call_id}, {'_id': 0})
    if call:
        return JSONResponse(content=json.loads(json_util.dumps(call)))
    else:
        raise HTTPException(status_code=404, detail="Call not found")
    
@app.get("/api/call_info_paginated")
async def get_calls_paginated(page: int = 1, limit: int = 10):
    collection = db['performanceCalification']
    
    # Total documents in the collection
    total_calls = collection.count_documents({})
    
    # Sort the calls by time and get the paginated result
    calls = collection.find({}, {'_id': 0}).sort('time', -1).skip((page - 1) * limit).limit(limit)
    
    return {
        "total_calls": total_calls,
        "calls": list(calls),
        "page": page,
        "limit": limit
    }

@app.get("/api/search_calls")
async def search_calls(query: str, page: int = 1, limit: int = 10):
    collection = db['performanceCalification']
    
    # Realizar la búsqueda por coincidencias parciales en call_id o reference
    search_filter = {
        "$or": [
            {"call_id": {"$regex": query, "$options": "i"}},  # Búsqueda insensible a mayúsculas
            {"reference": {"$regex": query, "$options": "i"}}
        ]
    }
    
    total_calls = collection.count_documents(search_filter)
    
    # Ordenar por tiempo, como lo haces en la otra API
    calls = collection.find(search_filter, {'_id': 0}).sort('time', -1).skip((page - 1) * limit).limit(limit)
    
    return {
        "total_calls": total_calls,
        "calls": list(calls),
        "page": page,
        "limit": limit
    }

@app.get("/trained_models")
async def get_data():
    collection = db["TrainingDialerDB"]["trained_models"]
    documents = list(collection.find({}))
    return JSONResponse(content=json.loads(json_util.dumps(documents)))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
