import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import './Result.css'; // Asegúrate de crear y ajustar este archivo CSS

function Result() {
  const location = useLocation();

  // Obtener parámetro de URL
  const searchParams = new URLSearchParams(location.search);
  const id = searchParams.get('id');
  let callID = id;

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showJSON, setShowJSON] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const interval = setInterval(async () => {
      const response = await fetch('/califications_history.json');
      // Ajusta esta URL según tu estructura de archivos
      const data = await response.json();
      const findData = data.filter((item) => item.call_id === callID);

      let arr = [];
      for (const i in findData) {
        findData[i].calification = JSON.parse(findData[i].calification);
        arr.push(findData[i]);
      }

      if (findData.length > 0) {
        setResults(arr);
        setLoading(false);
        clearInterval(interval);
      }
    }, 500); // Cambia el intervalo a 5000 milisegundos (5 segundos)
  }, [callID]);

  const handleMain = () => {
    navigate('/init');
  };

  const handleHistory = () => {
    navigate('/history_calls');
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      alert('Call ID copied to clipboard!');
    });
  };

  const toggleJSON = () => {
    setShowJSON(!showJSON);
  };

  const handleCopyJSON = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      alert('JSON copied to clipboard!');
    });
  };

  return (
    <div className="page-container">
      <div className="result-container">
        <h1>Evaluation Results for Customer Interaction</h1>
        {loading ? (
          <div className="loading-container">
            <p>Processing the evaluation, please wait a moment...</p>
            <div className="loading-animation"></div>
          </div>
        ) : (
          <div className="results-content">
            {results.map((item) => (
              <div key={item.call_id} className="result-item">
                <div className="call-id-container">
                  <h2>Call ID: {item.call_id}</h2>
                  <button onClick={() => handleCopy(item.call_id)} className="copy-button">Copy</button>
                </div>
                <h3>Metrics of evaluation (0-10):</h3>
                <div className="metrics">
                  <div className="metric-item">
                    <p className="metric-title"><strong>Communication Clarity:</strong></p>
                    <p className="metric-value">{item.calification['Communication Clarity']}</p>
                  </div>
                  <div className="metric-item">
                    <p className="metric-title"><strong>Empathy Expression:</strong></p>
                    <p className="metric-value">{item.calification['Empathy Expression']}</p>
                  </div>
                  <div className="metric-item">
                    <p className="metric-title"><strong>Resolution Efficiency:</strong></p>
                    <p className="metric-value">{item.calification['Resolution Efficiency']}</p>
                  </div>
                  <div className="metric-item">
                    <p className="metric-title"><strong>Rebuttal Appropriateness:</strong></p>
                    <p className="metric-value">{item.calification['Rebuttal Appropriateness']}</p>
                  </div>
                  <div className="metric-item">
                    <p className="metric-title"><strong>Overall Interaction Quality:</strong></p>
                    <p className="metric-value">{item.calification['Overall Interaction Quality']}</p>
                  </div>
                </div>
                <h3>Detailed Notes:</h3>
                <p>{item.calification.Notes}</p>
                <h3>
                  <span className="json-toggle" onClick={toggleJSON}>
                    {showJSON ? '▼' : '▶'} JSON Complete:
                  </span>
                  {showJSON && (
                    <span className="copy-json-icon" onClick={() => handleCopyJSON(JSON.stringify(item.calification, null, 2))}>
                      📋
                    </span>
                  )}
                </h3>
                {showJSON && <pre>{JSON.stringify(item.calification, null, 2)}</pre>}
              </div>
            ))}
          </div>
        )}
        <div className="button-group">
          <button onClick={handleMain}>Do a new call</button>
          <button onClick={handleHistory}>History Calls</button>
        </div>
      </div>
    </div>
  );
}

export default Result;
