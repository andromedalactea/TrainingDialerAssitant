import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import './Result.css'; // Asegúrate de tener el archivo CSS ajustado

function Result() {
  const location = useLocation();

  // Obtener parámetro de URL
  const searchParams = new URLSearchParams(location.search);
  const id = searchParams.get('id');
  let callID = id;

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showJSON, setShowJSON] = useState(false);
  const navigate = useNavigate();
  const MAX_RETRIES = 40; // 40 intentos de 3 segundos = 2 minutos

  useEffect(() => {
    let retries = 0;

    const fetchData = async () => {
      try {
        const response = await fetch(`https://x.butlercrm.com/api/call_info?call_id=${callID}`);
        if (response.ok) {
          const data = await response.json();
          if (data && Object.keys(data).length > 0) {
            setResults(data);
            setLoading(false);
          } else {
            // Si no se encuentra la información, vuelve a intentar hasta los 2 minutos
            if (retries < MAX_RETRIES) {
              retries++;
              setTimeout(fetchData, 3000); // Reintenta cada 3 segundos
            } else {
              setError('No se encontró la llamada después de 2 minutos.');
              setLoading(false);
            }
          }
        } else {
          // Ignorar errores y seguir reintentando hasta que pase el tiempo máximo
          if (retries < MAX_RETRIES) {
            retries++;
            setTimeout(fetchData, 3000); // Reintenta cada 3 segundos
          } else {
            setError('No se encontró la llamada después de 2 minutos.');
            setLoading(false);
          }
        }
      } catch (err) {
        // Ignorar errores de red y seguir reintentando hasta que pase el tiempo máximo
        if (retries < MAX_RETRIES) {
          retries++;
          setTimeout(fetchData, 3000); // Reintenta cada 3 segundos
        } else {
          setError('No se encontró la llamada después de 2 minutos.');
          setLoading(false);
        }
      }
    };

    fetchData();
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

  return (
    <div className="page-container">
      <div className="result-container">
        <h1>Evaluation Results for Customer Interaction</h1>
        {loading ? (
          <div className="loading-container">
            <p>Processing the evaluation, please wait a moment...</p>
            <div className="loading-animation"></div>
          </div>
        ) : error ? (
          <p className="error-message">{error}</p>
        ) : (
          <div className="results-content">
            {results && (
              <div key={results.call_id} className="result-item">
                <div className="call-id-container">
                  <h2>Call ID: {results.call_id}</h2>
                  <button onClick={() => handleCopy(results.call_id)} className="copy-button">Copy</button>
                </div>
                <h3>Performance Evaluation:</h3>
                <ReactMarkdown>{results.calification}</ReactMarkdown>
                <h3>Transcript:</h3>
                <pre>{results.transcript}</pre>
                <h3>Time:</h3>
                <p>{results.time}</p>
                <h3>Reference:</h3>
                <p>{results.reference}</p>
                <h3>
                  <span className="json-toggle" onClick={toggleJSON}>
                    {showJSON ? '▼' : '▶'} Raw JSON:
                  </span>
                </h3>
                {showJSON && <pre>{JSON.stringify(results, null, 2)}</pre>}
              </div>
            )}
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
