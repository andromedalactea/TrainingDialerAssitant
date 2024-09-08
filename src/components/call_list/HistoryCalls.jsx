import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './HistoryCalls.css';

function CallList() {
  const [calls, setCalls] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [callsPerPage, setCallsPerPage] = useState(10);
  const [totalCalls, setTotalCalls] = useState(0); // Número total de llamadas
  const [inputPage, setInputPage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  const handleMain = () => {
    navigate('/init');
  };

  // Fetch paginated or searched calls from API
  const fetchCalls = async (page, limit, searchQuery = '') => {
    let url = searchQuery
      ? `https://x.butlercrm.com/api/search_calls?query=${searchQuery}&page=${page}&limit=${limit}`
      : `https://x.butlercrm.com/api/call_info_paginated?page=${page}&limit=${limit}`;
    
    const response = await fetch(url);
    const data = await response.json();
    setCalls(data.calls);
    setTotalCalls(data.total_calls); // Actualiza el número total de llamadas
  };

  useEffect(() => {
    fetchCalls(currentPage, callsPerPage);
  }, [currentPage, callsPerPage]);

  // Función para manejar el cambio en el campo de búsqueda
  const handleSearchChange = (event) => {
    const input = event.target.value;
    setSearchTerm(input); // Actualiza el estado de búsqueda
  };

  // Función para realizar la búsqueda al hacer clic en el botón
  const handleSearchClick = () => {
    setCurrentPage(1); // Reiniciar la paginación a la página 1
    fetchCalls(1, callsPerPage, searchTerm); // Realiza la búsqueda con el término ingresado
  };

  // Función para redirigir a la página de resultados al hacer clic en una llamada
  const handleCallClick = (callId) => {
    navigate(`/result?id=${callId}`);
  };

  // Change page
  const handlePageChange = (event) => {
    setCurrentPage(Number(event.target.id));
  };

  const handleCallsPerPageChange = (event) => {
    setCallsPerPage(Number(event.target.value));
    setCurrentPage(1); // Reinicia a la primera página cuando cambias el límite de llamadas por página
  };

  const handleNextPage = () => {
    if (currentPage < Math.ceil(totalCalls / callsPerPage)) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleInputPageChange = (event) => {
    setInputPage(event.target.value);
  };

  const handleGoToPage = () => {
    const pageNumber = Number(inputPage);
    if (pageNumber > 0 && pageNumber <= Math.ceil(totalCalls / callsPerPage)) {
      setCurrentPage(pageNumber);
    }
    setInputPage('');
  };

  const pageNumbers = [];
  for (let i = 1; i <= Math.ceil(totalCalls / callsPerPage); i++) {
    pageNumbers.push(i);
  }

  // Determine the page numbers to display
  const maxPageNumbers = 5;
  const startPage = Math.max(1, currentPage - Math.floor(maxPageNumbers / 2));
  const endPage = Math.min(
    startPage + maxPageNumbers - 1,
    pageNumbers.length
  );
  const visiblePageNumbers = pageNumbers.slice(startPage - 1, endPage);

  return (
    <div className="call-list-container">
      <div className="header">
        <h1>Available Calls</h1>
        <div className="do-a-new-call">
          <button onClick={handleMain}>Do a new call</button>
        </div>
      </div>
      <div className="controls">
        <div className="search-bar">
          <label htmlFor="search">Search by Call ID or Reference: </label>
          <input
            type="text"
            id="search"
            value={searchTerm}
            onChange={handleSearchChange}
            className="styled-input"
          />
          <button onClick={handleSearchClick} className="search-button">
            Search
          </button>
        </div>
        <div className="per-page">
          <label>Calls per page: </label>
          <select value={callsPerPage} onChange={handleCallsPerPageChange} className="styled-select">
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="30">30</option>
            <option value="40">40</option>
            <option value="50">50</option> 
          </select>
        </div>
      </div>
      {calls.length > 0 ? (
        <ul className="call-list">
          {calls.map((call) => (
            <li
              key={call.call_id}
              className="call-list-item"
              onClick={() => handleCallClick(call.call_id)}
            >
              <span className="call-id">{call.call_id}</span>
              <span className="call-identifier">{call.reference}</span>
              <span className="call-time">{call.time}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p>No calls found for the given ID or Reference.</p>
      )}
      <div className="pagination">
        <button onClick={handlePrevPage} disabled={currentPage === 1}>
          Previous
        </button>
        {visiblePageNumbers.map((number) => (
          <button
            key={number}
            id={number}
            onClick={handlePageChange}
            className={currentPage === number ? 'active' : ''}
          >
            {number}
          </button>
        ))}
        <button onClick={handleNextPage} disabled={currentPage === Math.ceil(totalCalls / callsPerPage)}>
          Next
        </button>
        <div>
          <label>Go to page: </label>
          <input
            type="number"
            value={inputPage}
            onChange={handleInputPageChange}
            min="1"
            max={Math.ceil(totalCalls / callsPerPage)}
            className="styled-input"
          />
          <button onClick={handleGoToPage}>Go</button>
        </div>
      </div>
    </div>
  );
}

export default CallList;
