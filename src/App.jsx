import React from 'react';
import ReactDOM from 'react-dom';
import InitiVapi from './vapi/initVapi'
import Result from './vapi/results';
import { BrowserRouter as Router, Route, Switch, Routes } from 'react-router-dom';

function App() {
  return (
    <Routes>
        <Route  path="/init" element={<InitiVapi />} />
        <Route  path="/result" element={<Result />} />
    </Routes>
  );
}

export default App;