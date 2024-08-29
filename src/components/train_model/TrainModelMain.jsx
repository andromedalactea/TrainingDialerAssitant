import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './TrainModelMain.css';

function TrainedModels() {
  const navigate = useNavigate();

  const handleMain = () => {
    navigate('/init');
  };

  const handleTrainModel = () => {
    navigate('/train_model');
  }

  return (
    <div className="train-model-main">
      <h1>Train Model</h1>
      <p>Train your model here</p>
      <button onClick={handleMain}>Main</button>
      <button onClick={handleTrainModel}>Train your own model</button>
    </div>
  );
}

export default TrainedModels;