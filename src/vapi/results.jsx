import React, {useState, useEffect} from 'react';
import { useLocation } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';

function Result() {
  const location = useLocation();

  // Obtener parámetro de URL
  const searchParams = new URLSearchParams(location.search);
  const id = searchParams.get('id');
  let callID = id

    const [results, setResults] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
  
      const interval = setInterval(async () => {
        
        const respones = await fetch('/califications_history.json');
        // Ajusta esta URL según tu estructura de archivos
          const data = await respones.json();
          const findData = data.filter((item) => item.call_id === callID);
        let arr = []
          for (const i in findData){
            findData[i].calification = JSON.parse(findData[i].calification );
            arr.push(findData[i])
          }

          if (findData.length > 0){
            setResults(arr)
            clearInterval(interval)
          }
      }, 500); // Cambia el intervalo a 5000 milisegundos (5 segundos)
    }, [callID]);

  
    const handleMain = () => {
        navigate('/init');
    }
    return (
      <div>
        <h1>Waiting for Evaluation Results</h1>
        <div>
          <h1>Evaluation Results for Customer Interaction</h1>
          <p>There was an error fetching the results.</p>
          <div style={{ marginTop: '20px', width: '80%', height: '200px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px' }}>
            <h3>Logs</h3>
            { results.map(item => (
                <>
                <h1>{item.calification.Notes} </h1>
                <p> {item.calification['Communication Clarity']}</p>
                <p>{item.calification['Empathy Expression']}</p>
                <p>{item.calification['Resolution Efficiency']}</p>
                <p>{item.calification['Rebuttal Appropriateness']}</p>
                <p>{item.calification['Overall Interaction Quality']}</p>
                </>
            ))} 
          </div>
        </div>
        <button onClick={handleMain}>come back to home</button>
      </div>
    );
}

export default Result;