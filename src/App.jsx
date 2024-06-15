import { useEffect, useState } from "react";
import ActiveCallDetail from "./components/ActiveCallDetail";
import Button from "./components/base/Button";
import Vapi from "@vapi-ai/web";
import { isPublicKeyMissingError } from "./utils";
import { v4 as uuidv4 } from 'uuid';
import WaitingScreen from "./components/call/WaitingScreen";
import ResultScreen from "./components/call/ResultScreen";

// Put your Vapi Public Key below.
const VAPI_PUBLIC_KEY = process.env.REACT_APP_VAPI_PUBLIC_KEY;
const vapi = new Vapi(VAPI_PUBLIC_KEY);

const App = () => {
  const [connecting, setConnecting] = useState(false);
  const [connected, setConnected] = useState(false);
  const [assistantIsSpeaking, setAssistantIsSpeaking] = useState(false);
  const [volumeLevel, setVolumeLevel] = useState(0);
  const [callID, setCallID] = useState(null);
  const [view, setView] = useState('main');
  const [logs, setLogs] = useState([]);
  const { showPublicKeyInvalidMessage, setShowPublicKeyInvalidMessage } = usePublicKeyInvalid();

  const addLog = (message) => {
    setLogs((prevLogs) => [...prevLogs, message]);
  };

  useEffect(() => {
    vapi.on("call-start", () => {
      addLog("Call started");
      setConnecting(false);
      setConnected(true);
      setShowPublicKeyInvalidMessage(false);
    });

    vapi.on("call-end", () => {
      addLog("Call ended");
      setConnecting(false);
      setConnected(false);
      setShowPublicKeyInvalidMessage(false);
      setView('waiting'); // Cambia la vista a 'waiting' después de que la llamada termina
    });

    vapi.on("speech-start", () => {
      setAssistantIsSpeaking(true);
    });

    vapi.on("speech-end", () => {
      setAssistantIsSpeaking(false);
    });

    vapi.on("volume-level", (level) => {
      setVolumeLevel(level);
    });

    vapi.on("error", (error) => {
      addLog(`VAPI Error: ${error}`);
      setConnecting(false);
      if (isPublicKeyMissingError({ vapiError: error })) {
        setShowPublicKeyInvalidMessage(true);
      }
    });
  }, []);

  const startCallInline = () => {
    setConnecting(true);
    const call_secundary_id = uuidv4();
    setCallID(call_secundary_id);
    addLog(`Starting call with ID: ${call_secundary_id}`);

    const assistantOverrides = {
      metadata: { call_secundary_id: call_secundary_id },
    };

    vapi.start(assistantOptions, assistantOverrides);
  };

  const endCall = () => {
    addLog(`Ending call with ID: ${callID}`);
    vapi.stop();
  };

  return (
    <div
      style={{
        display: "flex",
        width: "100vw",
        height: "100vh",
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
      }}
    >
      {console.log('view:', view)}
      {view === 'main' && (
        !connected ? (
          <Button
            label="Call Vapi’s Pizza Front Desk"
            onClick={startCallInline}
            isLoading={connecting}
          />
        ) : (
          <ActiveCallDetail
            assistantIsSpeaking={assistantIsSpeaking}
            volumeLevel={volumeLevel}
            onEndCallClick={endCall}
          />
        )
      )}

    
      {view === 'waiting' && <WaitingScreen callID={callID} onResults={() => setView('results')} />}

      {view === 'results' && <ResultScreen callID={callID} />}
      
      
      
      {showPublicKeyInvalidMessage ? <PleaseSetYourPublicKeyMessage /> : null}
      <ReturnToDocsLink />
      <div style={{ marginTop: '20px', width: '80%', height: '200px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px' }}>
        <h3>Logs</h3>
        {logs.map((log, index) => (
          <div key={index}>{log}</div>
        ))}
      </div>
    </div>
  );
};

// Define the domain and server URL for the API calls.
const domain = "hugely-cute-sunfish.ngrok-free.app";
const serverUrl = `https://${domain}/calificate_call`;

console.log("Server URL:", serverUrl);

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

const usePublicKeyInvalid = () => {
  const [showPublicKeyInvalidMessage, setShowPublicKeyInvalidMessage] = useState(false);

  useEffect(() => {
    if (showPublicKeyInvalidMessage) {
      setTimeout(() => {
        setShowPublicKeyInvalidMessage(false);
      }, 3000);
    }
  }, [showPublicKeyInvalidMessage]);

  return {
    showPublicKeyInvalidMessage,
    setShowPublicKeyInvalidMessage,
  };
};

const PleaseSetYourPublicKeyMessage = () => {
  return (
    <div
      style={{
        position: "fixed",
        bottom: "25px",
        left: "25px",
        padding: "10px",
        color: "#fff",
        backgroundColor: "#f03e3e",
        borderRadius: "5px",
        boxShadow: "0 2px 5px rgba(0,0,0,0.2)",
      }}
    >
      Is your Vapi Public Key missing? (recheck your code)
    </div>
  );
};

const ReturnToDocsLink = () => {
  return (
    <a
      href="https://docs.vapi.ai"
      target="_blank"
      rel="noopener noreferrer"
      style={{
        position: "fixed",
        top: "25px",
        right: "25px",
        padding: "5px 10px",
        color: "#fff",
        textDecoration: "none",
        borderRadius: "5px",
        boxShadow: "0 2px 5px rgba(0,0,0,0.2)",
      }}
    >
      return to docs
    </a>
  );
};

export default App;
