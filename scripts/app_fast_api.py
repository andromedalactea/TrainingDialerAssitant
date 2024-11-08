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
from components.call_calification import calificate_call, calificate_call_from_direct_audio, get_current_time_ny, save_calification_mongo
from components.auxiliar_functions import absolute_path, convert_timestamp_to_date
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

        # Extract call data
        call_data = message.get("call", {})
        call_id = message["call"]["assistantOverrides"]["metadata"]["call_secundary_id"]
        reference = message["call"]["assistantOverrides"]["metadata"]["reference"]
        
        
        # Extract the transcript from the message
        transcript = message.get("transcript")
        
        # Extract audio url
        audio_url = message.get("recordingUrl")
        print(f"Audio URL: {audio_url}")

        # Extract the context of the call
        context_call = f"""This is some context for the call (For executive summary but is possible to use for other parts of the report as well):
            Date of the call: {convert_timestamp_to_date(message.get('timestamp'))}
            Duration of the call: {message.get('durationSeconds')} seconds
            Lead Name/ID: Agent Sales Trainer\n\n"
            """

        # Generate the calification direct from the AI audio or transcript
        try:
            transcript_from_audio, calification = calificate_call_from_direct_audio(audio_url, context_call)

            # Verificar si transcript_from_audio o calification son nulos
            if transcript_from_audio is None or calification is None:
                raise ValueError("One or both values are None")  # Forzar ir a la alternativa

        except Exception as e:
            print(f"Error: {e}")
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

@app.get("/api/email_calls")
async def get_call(call_id: list):
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
