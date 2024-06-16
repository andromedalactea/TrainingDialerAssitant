import { useEffect, useState } from "react";

const WaitingScreen = ({ callID,}) => {
  const [attempts, setAttempts] = useState(0);
  const [found, setFound] = useState(false);
  const [logs, setLogs] = useState([]);

  const addLog = (message) => {
    setLogs((prevLogs) => [...prevLogs, message]);
  };

  useEffect(() => {

    const interval = setInterval(async () => {
      setAttempts(prev => prev + 1);
      addLog(`Attempt ${attempts}: Checking for callID ${callID}`);
    localStorage.setItem('results',true);
      
      const respones = await fetch('/califications_history.json');
      // Ajusta esta URL según tu estructura de archivos
        const data = await respones.json();
        console.log(data)
        const findData = data.filter((item) => item.call_id === callID);
        console.log(findData)
        // for (const i in data) {
        //         try {
        //           console.log(data[i].call_id, callID)
        //           if (data[i].call_id === callID) {
        //             console.log('Call ID found:', data[i].call_id );  
        //             // setFound(true);
        //             // onResults('results');
        // clearInterval(interval)
                    
        //             break;
        //           }
        //         } catch (e) {
        //           console.log('Error parsing JSON line:', e.message)
        //         }
        //       }


        
        // .then(data => {
        //   console.log('Fetched data:', data); 
        //   setFound(true);
        //   clearInterval(interval);
        //   const lines = data.split('\n');
        //  
        //   }
        // })
        // .catch(error => {
        //   addLog(`Error fetching the JSON file: ${error.message}`);
        // });
  
  
    }, 100); // Cambia el intervalo a 5000 milisegundos (5 segundos)
  //   return () => clearInterval(interval);
  }, [callID]);


  return (
    <div>
      <h1>Waiting for Evaluation Results</h1>
      <p>Please wait, retrieving results for call ID: {callID}</p>
      {/* <button onClick={() => onResults('main')}>Back to Home</button> */}
      <div style={{ marginTop: '20px', width: '80%', height: '200px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px' }}>
        <h3>Logs</h3>
        {logs.map((log, index) => (
          <div key={index}>{log}</div>
        ))}
      </div>

      <div>
        <h1>Evaluation Results for Customer Interaction</h1>
        <p>There was an error fetching the results.</p>
        <div style={{ marginTop: '20px', width: '80%', height: '200px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px' }}>
          <h3>Logs</h3>
          {/* <ResultScreen callID={callID} /> */}
        </div>
      </div>
    </div>
  );
};

export default WaitingScreen;
