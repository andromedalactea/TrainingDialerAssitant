import Vapi from "@vapi-ai/web";
import Button from "../components/base/Button";
import ActiveCallDetail from "../components/ActiveCallDetail";
import WaitingScreen from "../components/call/WaitingScreen";
import { useNavigate } from 'react-router-dom';
import { v4 as uuidv4 } from "uuid";
import { useState, useEffect } from "react";
import './InitVapi.css';

const VAPI_PUBLIC_KEY = process.env.REACT_APP_VAPI_PUBLIC_KEY;
const vapi = new Vapi(VAPI_PUBLIC_KEY);

function InitVapi() {
  const [istalking, setTalking] = useState(false);
  const [assistantIsSpeaking, setAssistantIsSpeaking] = useState(false);
  const [volumeLevel, setVolumeLevel] = useState(0);
  const [callID, setCallID] = useState(null);
  const [waiting, setWaiting] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    if (waiting) {
      navigate('/result?id='+callID+'');
    }
    vapi.on("volume-level", (level) => {
      setVolumeLevel(level);
    });
    vapi.on("speech-start", () => {
      setAssistantIsSpeaking(true);
    });
    vapi.on("speech-end", () => {
      setAssistantIsSpeaking(false);
    });
  }, [waiting, navigate]);


  const startCallInline = () => {
    const call_secundary_id = uuidv4();
    setCallID(call_secundary_id);

    const assistantOverrides = {
      metadata: { call_secundary_id: call_secundary_id },
    };

    vapi.start(assistantOptions, assistantOverrides);
    setTalking(true);
  };

  const endCall = () => {
    vapi.stop();
    setTalking(false);
    setWaiting(true);
  };

  const handleRedirect = () => {
    navigate('/about');
  };

  const handleHistory = () => {
    navigate('/history_calls');
  };

  return (
    <div className="init-container">
      {istalking ? (
        <ActiveCallDetail
          assistantIsSpeaking={assistantIsSpeaking}
          volumeLevel={volumeLevel}
          onEndCallClick={endCall}
        />
      ) : (
        <div className="center-content">
          {waiting ? (
            <h1></h1>
            // () => handleRedirect()
            // <WaitingScreen callID={callID} />
          ) : (
            <>
              <h2>Press the button to start the evaluation</h2>
              <Button
                label="Training Dialer"
                onClick={startCallInline}
                // isLoading={connecting}
              />
            </>
          )}
        </div>
      )}
      {!istalking && (
        <div className="bottom-right">
          <Button
            label="View call history"
            onClick={handleHistory}
          />
        </div>
      )}
    </div>
  );
}

export default InitVapi;

// Generate the Initial message
const moment = require('moment-timezone');

let firstMessage;

try {
    // Establecer la zona horaria deseada
    const timezone = 'America/New_York';

    // Obtener la hora actual en la zona horaria deseada
    const time = moment.tz(timezone);

    // Determinar el mensaje apropiado según la hora
    if (time.hour() < 12) {
        firstMessage = "Good morning";
    } else if (time.hour() < 18) {
        firstMessage = "Good afternoon";
    } else {
        firstMessage = "Good night";
    }
} catch (error) {
    firstMessage = "Hello";
}

console.log(firstMessage);

const domain = "hugely-cute-sunfish.ngrok-free.app";
const serverUrl = `https://${domain}/calificate_call`;
const assistantOptions = {
  serverUrl: serverUrl,
  name: "Training Dialer",
  firstMessage: firstMessage,
  transcriber: {
    provider: "deepgram",
    model: "nova-2",
    language: "en-US",
  },
  voice: {
    provider: "playht",
    voiceId: "michael",
    styleGuidance: 15,
    textGuidance: 1,
  },
  model: {
    urlRequestMetadataEnabled: false,
    provider: "custom-llm",
    url: "https://api.openai.com/v1/chat/completions",
    model: "ft:gpt-3.5-turbo-0125:igd::9PXt2D06",
    messages: [
      {
        role: "system",
        content: "Try to have a behavior like a user",
      },
    ],
  },
};
