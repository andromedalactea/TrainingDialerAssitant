import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './HistoryCalls.css';

function CallList() {
  const [calls, setCalls] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [callsPerPage, setCallsPerPage] = useState(10);
  const [inputPage, setInputPage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredCalls, setFilteredCalls] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCalls = async () => {
      const response = await fetch('/califications_history.json');
      const data = await response.json();
      setCalls(data);
      setFilteredCalls(data);
    };
    fetchCalls();
  }, []);

  useEffect(() => {
    setFilteredCalls(
      calls.filter((call) =>
        call.call_id.replace(/\s+/g, '').toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }, [searchTerm, calls]);

  // Calculate the displayed calls for the current page
  const indexOfLastCall = currentPage * callsPerPage;
  const indexOfFirstCall = indexOfLastCall - callsPerPage;
  const currentCalls = filteredCalls.slice(indexOfFirstCall, indexOfLastCall);

  const handleCallClick = (callId) => {
    navigate(`/result?id=${callId}`);
  };

  const handlePageChange = (event) => {
    setCurrentPage(Number(event.target.id));
  };

  const handleCallsPerPageChange = (event) => {
    setCallsPerPage(Number(event.target.value));
    setCurrentPage(1);
  };

  const handleNextPage = () => {
    if (currentPage < Math.ceil(filteredCalls.length / callsPerPage)) {
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
    if (pageNumber > 0 && pageNumber <= Math.ceil(filteredCalls.length / callsPerPage)) {
      setCurrentPage(pageNumber);
    }
    setInputPage('');
  };

  const handleSearchChange = (event) => {
    const input = event.target.value.replace(/\s+/g, '');
    setSearchTerm(input);
  };

  const pageNumbers = [];
  for (let i = 1; i <= Math.ceil(filteredCalls.length / callsPerPage); i++) {
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
      <h1>Available Calls</h1>
      <div className="controls">
        <div className="search-bar">
          <label htmlFor="search">Search by Call ID: </label>
          <input
            type="text"
            id="search"
            value={searchTerm}
            onChange={handleSearchChange}
            className="styled-input"
          />
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
      {currentCalls.length > 0 ? (
        <ul className="call-list">
          {currentCalls.map((call) => (
            <li
              key={call.call_id}
              className="call-list-item"
              onClick={() => handleCallClick(call.call_id)}
            >
              <span className="call-id">{call.call_id}</span>
              <span className="call-identifier">{call.identifier}</span>
              <span className="call-time">{call.time}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p>No calls found for the given ID.</p>
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
        <button onClick={handleNextPage} disabled={currentPage === Math.ceil(filteredCalls.length / callsPerPage)}>
          Next
        </button>
        <div>
          <label>Go to page: </label>
          <input
            type="number"
            value={inputPage}
            onChange={handleInputPageChange}
            min="1"
            max={Math.ceil(filteredCalls.length / callsPerPage)}
            className="styled-input"
          />
          <button onClick={handleGoToPage}>Go</button>
        </div>
      </div>
    </div>
  );
}

export default CallList;
