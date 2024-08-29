import React from 'react';
import ReactDOM from 'react-dom';
import InitiVapi from './vapi/initVapi'
import Result from './vapi/results';
import CallList from './components/call_list/HistoryCalls';
import TrainedModels from './components/train_model/TrainModelMain';
import { BrowserRouter as Router, Route, Switch, Routes } from 'react-router-dom';

function App() {
  return (
    <Routes>
        <Route  path="/init" element={<InitiVapi />} />
        <Route  path="/result" element={<Result />} />
        <Route  path="/history_calls" element={<CallList />} />
        <Route  path="/trained_models" element={<TrainedModels />} />
    </Routes>
  ); 
}

export default App;