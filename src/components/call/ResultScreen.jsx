import { useState, useEffect } from "react";
import axios from 'axios';

const ResultScreen = ({ callID }) => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(false);
  const [logs, setLogs] = useState([]);

  const addLog = (message) => {
    setLogs((prevLogs) => [...prevLogs, message]);
  };

  useEffect(() => {
    addLog(`Fetching results for callID: ${callID}`);
    console.log(`Fetching results for callID: ${callID}`);
    axios.get('/califications_history.jsonl') // Ajusta esta URL según tu estructura de archivos
      .then(response => {
        addLog(`Fetch response status: ${response.status}`);
        return response.data;
      })
      .then(resultData => {
        addLog(`Fetched data: ${resultData}`);
        const lines = resultData.split('\n');
        for (const line of lines) {
          if (line.trim()) {
            try {
              const json = JSON.parse(line);
              if (json.call_id === callID) {
                addLog(`Result data found: ${json.call_id}`);
                setData(json);
                break;
              }
            } catch (e) {
              addLog(`Error parsing JSON line: ${e.message}`);
            }
          }
        }
      })
      .catch(error => {
        addLog(`Error fetching the JSON file: ${error.message}`);
        setError(true);
      });
  }, [callID]);

  if (!data && !error) {
    return <div>Loading...</div>;
  }

  if (error) {
    return (
      <div>
        <h1>Evaluation Results for Customer Interaction</h1>
        <p>There was an error fetching the results.</p>
        <div style={{ marginTop: '20px', width: '80%', height: '200px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px' }}>
          <h3>Logs</h3>
          {logs.map((log, index) => (
            <div key={index}>{log}</div>
          ))}
        </div>
      </div>
    );
  }

  let calification;
  try {
    calification = JSON.parse(data.calification);
  } catch (e) {
    addLog(`Error parsing calification JSON: ${e.message}`);
    return (
      <div>
        <h1>Evaluation Results for Customer Interaction</h1>
        <p>Error parsing calification data. Raw calification data:</p>
        <pre>{data.calification}</pre>
        <div style={{ marginTop: '20px', width: '80%', height: '200px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px' }}>
          <h3>Logs</h3>
          {logs.map((log, index) => (
            <div key={index}>{log}</div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div>
      <h1>Evaluation Results for Customer Interaction</h1>
      <button onClick={() => window.location.reload()}>Back to Home</button>
      {calification ? (
        <div>
          <h2>Metrics of evaluation (0-10):</h2>
          {Object.keys(calification).map(key => (
            key !== "Notes" && key !== "call_id" && (
              <div key={key}>
                <strong>{key}: </strong>{calification[key]}
              </div>
            )
          ))}
          {calification.Notes && (
            <>
              <h2>Detailed Notes:</h2>
              <p>{calification.Notes}</p>
            </>
          )}
        </div>
      ) : (
        <p>Calification data not found in the response.</p>
      )}
      <h2>JSON Complete:</h2>
      <pre>{JSON.stringify(calification, null, 2)}</pre>
      <div style={{ marginTop: '20px', width: '80%', height: '200px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px' }}>
        <h3>Logs</h3>
        {logs.map((log, index) => (
          <div key={index}>{log}</div>
        ))}
      </div>
    </div>
  );
};

export default ResultScreen;
