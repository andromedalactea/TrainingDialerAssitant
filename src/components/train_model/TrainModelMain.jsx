import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './TrainModelMain.css';

function TrainedModels() {
  const [models, setModels] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [modelsPerPage, setModelsPerPage] = useState(10);
  const [inputPage, setInputPage] = useState('');

  const navigate = useNavigate();

  const handleMain = () => {
    navigate('/init');
  };

  const handleTrainModel = () => {
    navigate('/train_model');
  };

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch('https://shiny-kings-dance.loca.lt/trained_models');
        console.log('------------------------------------');
        console.log(response);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const text = await response.text();  // Primero obtén el texto de la respuesta
        try {
          const data = JSON.parse(text);  // Intenta parsear el texto como JSON
          setModels(data);
        } catch (e) {
          console.error("No se pudo parsear la respuesta como JSON:", text);
          throw e;
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
    fetchModels();
  }, []);
  

  // Pagination logic
  const indexOfLastModel = currentPage * modelsPerPage;
  const indexOfFirstModel = indexOfLastModel - modelsPerPage;
  const currentModels = models.slice(indexOfFirstModel, indexOfLastModel);

  const handlePageChange = (event) => {
    setCurrentPage(Number(event.target.id));
  };

  const handleInputPageChange = (event) => {
    setInputPage(event.target.value);
  };

  const handleGoToPage = () => {
    const pageNumber = Number(inputPage);
    if (pageNumber > 0 && pageNumber <= Math.ceil(models.length / modelsPerPage)) {
      setCurrentPage(pageNumber);
    }
    setInputPage('');
  };

  const pageNumbers = [];
  for (let i = 1; i <= Math.ceil(models.length / modelsPerPage); i++) {
    pageNumbers.push(i);
  }

  return (
    <div className="train-model-main">
      <h1>Train Model</h1>
      <button onClick={handleMain}>Main</button>
      <button onClick={handleTrainModel}>Train your own model</button>

      <div className="model-list">
        {currentModels.map((model, index) => (
          <div key={index} className="model-item">
            <h3>{model.name}</h3>
            <p>{model.description}</p>
          </div>
        ))}
      </div>

      <div className="pagination">
        <button onClick={() => setCurrentPage(prev => prev - 1)} disabled={currentPage === 1}>Previous</button>
        {pageNumbers.map(number => (
          <button key={number} id={number} onClick={handlePageChange} className={currentPage === number ? 'active' : ''}>
            {number}
          </button>
        ))}
        <button onClick={() => setCurrentPage(prev => prev + 1)} disabled={currentPage === Math.ceil(models.length / modelsPerPage)}>Next</button>

        <label>Go to page:</label>
        <input type="number" value={inputPage} onChange={handleInputPageChange} min="1" max={Math.ceil(models.length / modelsPerPage)} />
        <button onClick={handleGoToPage}>Go</button>
      </div>
    </div>
  );
}

export default TrainedModels;
