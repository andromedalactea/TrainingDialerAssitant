import Vapi from "@vapi-ai/web";
import Button from "../components/base/Button";
import ActiveCallDetail from "../components/ActiveCallDetail";
import WaitingScreen from "../components/call/WaitingScreen";
import { useNavigate } from 'react-router-dom';
import { v4 as uuidv4 } from "uuid";
import { useState, useEffect } from "react";

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
  return (
    <>
      {istalking ? (
        <ActiveCallDetail
          assistantIsSpeaking={assistantIsSpeaking}
          volumeLevel={volumeLevel}
          onEndCallClick={endCall}
        />
      ) : (
        <>
          {waiting ? (
            <h1>hola</h1>
            // () => handleRedirect()
            // <WaitingScreen callID={callID} />
          ) : (
            <Button
              label="Call Vapi’s Pizza Front Desk"
              onClick={startCallInline}
              // isLoading={connecting}
            />
          )}
        </>
      )}
    </>
  );
}

export default InitVapi;

const domain = "hugely-cute-sunfish.ngrok-free.app";
const serverUrl = `https://${domain}/calificate_call`;
const assistantOptions = {
  serverUrl: serverUrl,
  name: "Vapi’s Pizza Front Desk",
  firstMessage: "Vappy’s Pizzeria speaking, how can I help you?",
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
