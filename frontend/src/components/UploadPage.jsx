import { useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function UploadPage() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.pptx') || droppedFile.name.endsWith('.ppt')) {
        setFile(droppedFile);
        setMessage('');
      } else {
        setMessage('Please upload a PowerPoint file (.pptx or .ppt)');
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.name.endsWith('.pptx') || selectedFile.name.endsWith('.ppt')) {
        setFile(selectedFile);
        setMessage('');
      } else {
        setMessage('Please upload a PowerPoint file (.pptx or .ppt)');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select a file first');
      return;
    }

    setUploading(true);
    setMessage('Uploading and processing slides...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/api/slides/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setMessage(`Success! Uploaded ${response.data.slides_created} slides with AI-generated tags.`);
      setFile(null);
    } catch (error) {
      console.error('Upload error:', error);
      setMessage(`Error: ${error.response?.data?.detail || 'Failed to upload file'}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="upload-container">
        <h2>Upload PowerPoint Presentation</h2>
        <p className="subtitle">Upload your slides and let AI automatically tag them</p>

        <div
          className={`drop-zone ${dragActive ? 'drag-active' : ''} ${file ? 'has-file' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="file-input"
            accept=".pptx,.ppt"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          
          {!file ? (
            <>
              <div className="upload-icon">📁</div>
              <p className="drop-text">Drag and drop your PowerPoint file here</p>
              <p className="or-text">or</p>
              <label htmlFor="file-input" className="browse-button">
                Browse Files
              </label>
              <p className="file-types">Supports .pptx and .ppt files</p>
            </>
          ) : (
            <>
              <div className="file-icon">📄</div>
              <p className="file-name">{file.name}</p>
              <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              <button 
                className="remove-button"
                onClick={() => setFile(null)}
              >
                Remove
              </button>
            </>
          )}
        </div>

        {file && !uploading && (
          <button className="upload-button" onClick={handleUpload}>
            Upload and Process
          </button>
        )}

        {uploading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Processing slides and generating AI tags...</p>
          </div>
        )}

        {message && (
          <div className={`message ${message.includes('Success') ? 'success' : message.includes('Error') ? 'error' : 'info'}`}>
            {message}
          </div>
        )}

        <div className="info-box">
          <h3>What happens after upload?</h3>
          <ul>
            <li>✓ Slides are extracted from your presentation</li>
            <li>✓ AI analyzes each slide's content</li>
            <li>✓ Automatic tags are generated (painpoints, client type, software, etc.)</li>
            <li>✓ Slides become searchable immediately</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default UploadPage;

// Made with Bob
