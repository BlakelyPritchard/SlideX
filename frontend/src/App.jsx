import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { useState } from 'react';
import UploadPage from './components/UploadPage';
import SearchPage from './components/SearchPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-container">
            <h1 className="logo">SlideX</h1>
            <div className="nav-links">
              <Link to="/" className="nav-link">Search</Link>
              <Link to="/upload" className="nav-link">Upload</Link>
            </div>
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<SearchPage />} />
            <Route path="/upload" element={<UploadPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

// Made with Bob
