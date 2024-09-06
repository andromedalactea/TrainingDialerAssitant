# Import Python Libraries
import os
import json
import codecs

# Third-party libraries
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from bson import json_util, ObjectId
from pymongo import MongoClient


# Local imports
from components.call_calification import calificate_call, get_current_time_ny, save_calification_mongo

# Load environment variables from the .env file
load_dotenv(override=True)

# Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/calificate_call", methods=["POST"])
def main_call():
    """Webhook endpoint that receives POST requests and processes call transcriptions."""
    try:
        data = request.json
        
        message_vapi = data.get("message")
        print(data)
        if  message_vapi.get("type") == "end-of-call-report":

            # Extract call id of vapi
            call_info = message_vapi.get("call")
            vapi_call_id = call_info.get("id")

            # Extract call id
            call_data = message_vapi.get("call", {})
            call_id = data["message"]["call"]["assistantOverrides"]["metadata"]["call_secundary_id"]
            reference = data["message"]["call"]["assistantOverrides"]["metadata"]["reference"]
            
            
            # Extract the transcript from the message
            transcript = message_vapi.get("transcript")
            
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

            return jsonify({"status": "success", "calification": calification}), 200
        else:
            return jsonify({"status": "ignored"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/call_info", methods=["GET"])
def get_call():

    # create the connection to the MongoDB
    call_id = request.args.get("call_id")
    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    db = client['TrainingDialer']
    collection = db['performanceCalification']

    # Exclude the '_id' field from the results
    call = collection.find_one({"call_id": call_id}, {'_id': 0})
    
    if call:
        return jsonify(call), 200
    else:
        return jsonify({"error": "Call not found"}), 404
    

@app.route("/trained_models", methods=["GET"])
def get_data():
    # Configura la conexión a MongoDB
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client["TrainingDialerDB"]  
    collection = db["trained_models"]  

    try:
        documents = list(collection.find({}))
        # Utiliza json_util de bson para convertir los documentos a un formato JSON adecuado
        json_docs = json.loads(json_util.dumps(documents))
        return jsonify(json_docs), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    
    # Define the port of your choice, by default Flask uses port 5000
    port = 8080


    # Run the Flask server, making sure it is publicly accessible and on the correct port
    app.run(host="0.0.0.0", port=port)

    # Disconnect the ngrok tunnel when you are ready to end the session 
    # ngrok.disconnect(ngrok_tunnel.public_url)