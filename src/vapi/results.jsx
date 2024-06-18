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
        <div>
          <h1>Evaluation Results for Customer Interaction</h1>
          
          <div style={{ marginTop: '20px', width: '80%', height: '600px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px' }}>
            { results.map(item => (
                <>
                <h1>Call ID: {item.call_id}</h1>
                <p>General Notes:  </p><br/>
                <p>{item.calification.Notes}</p><br/>
                <p>Communication Clarity: {item.calification['Communication Clarity']}</p><br/>
                <p>Empathy Expression: {item.calification['Empathy Expression']}</p><br/>
                <p>Resolution Efficiency: {item.calification['Resolution Efficiency']}</p><br/>
                <p>Rebuttal Appropriateness: {item.calification['Rebuttal Appropriateness']}</p><br/>
                <p>Overall Interaction Quality {item.calification['Overall Interaction Quality']}</p><br/>
                </>
            ))} 
          </div>
        </div>
        <button onClick={handleMain}>come back to home</button>
      </div>
    );
}

export default Result;