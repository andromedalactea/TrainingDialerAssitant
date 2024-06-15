import { useEffect, useState } from "react";

const WaitingScreen = ({ callID, onResults }) => {
  const [attempts, setAttempts] = useState(0);
  const [found, setFound] = useState(false);
  const [logs, setLogs] = useState([]);

  const addLog = (message) => {
    setLogs((prevLogs) => [...prevLogs, message]);
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setAttempts(prev => prev + 1);
      addLog(`Attempt ${attempts}: Checking for callID ${callID}`);
      
      fetch('/califications_history.jsonl') // Ajusta esta URL según tu estructura de archivos
        .then(response => {
          addLog(`Fetch response status: ${response.status}`);
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.text();
        })
        .then(data => {
          console.log('Fetched data:', data); 
          setFound(true);
          onResults();
          clearInterval(interval);
          const lines = data.split('\n');
          for (const line of lines) {
            console.log('Line:', line);
            if (line.trim()) {
              addLog(`Parsing line: ${line}`);
              console.log('Parsing line:', line);
              try {
                const json = JSON.parse(line);
                console.log('Parsed JSON:', json);
                console.log('Call ID:', callID);
                addLog(`Parsed JSON: ${JSON.stringify(json)}`);
                if (json.call_id === callID) {
                  addLog(`Call ID found: ${json.call_id}`);
                  console.log('Call ID found:', json.call_id);  
                  setFound(true);
                  onResults('results');
                  
                  break;
                }
              } catch (e) {
                addLog(`Error parsing JSON line: ${e.message}`);
                console.log('Error parsing JSON line:', e.message)
              }
            }
          }
        })
        .catch(error => {
          addLog(`Error fetching the JSON file: ${error.message}`);
        });

      if (found || attempts >= 1000) {
        clearInterval(interval);
      }
    }, 10000); // Cambia el intervalo a 5000 milisegundos (5 segundos)

    return () => clearInterval(interval);
  }, [attempts, callID, found, onResults]);

  return (
    <div>
      <h1>Waiting for Evaluation Results</h1>
      <p>Please wait, retrieving results for call ID: {callID}</p>
      <button onClick={() => onResults('main')}>Back to Home</button>
      <div style={{ marginTop: '20px', width: '80%', height: '200px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px' }}>
        <h3>Logs</h3>
        {logs.map((log, index) => (
          <div key={index}>{log}</div>
        ))}
      </div>
    </div>
  );
};

export default WaitingScreen;
