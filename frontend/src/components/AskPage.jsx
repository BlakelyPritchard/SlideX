import { useState } from 'react';
import axios from 'axios';

const AskPage = () => {
  const [request, setRequest] = useState('');
  const [clientName, setClientName] = useState('');
  const [customTitle, setCustomTitle] = useState('');
  const [addAgenda, setAddAgenda] = useState(true);
  const [addNotes, setAddNotes] = useState(true);
  const [loading, setLoading] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [previewSlides, setPreviewSlides] = useState([]);
  const [selectedSlideOrder, setSelectedSlideOrder] = useState([]); // Array of slide IDs in order
  const [manualMode, setManualMode] = useState(false);

  const handlePreview = async () => {
    if (!request.trim()) {
      setError('Please enter a request');
      return;
    }

    setPreviewing(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post('http://localhost:8000/api/deck-generation/preview', {
        request: request,
        add_agenda: addAgenda,
        add_notes: addNotes,
        client_name: clientName || null,
        custom_title: customTitle || null
      });

      if (response.data.success) {
        setPreviewSlides(response.data.slides);
        setSelectedSlideOrder([]); // Start with no selection in manual mode
        setResult({
          type: 'preview',
          slideCount: response.data.slide_count,
          estimatedDuration: response.data.estimated_duration_minutes,
          parsedRequest: response.data.parsed_request,
          suggestedTitle: response.data.suggested_title
        });
      } else {
        setError(response.data.message || 'Failed to preview deck');
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to preview deck');
    } finally {
      setPreviewing(false);
    }
  };

  const handleSlideClick = (slideId) => {
    if (!manualMode) return; // Only work in manual mode

    setSelectedSlideOrder(prev => {
      const index = prev.indexOf(slideId);
      if (index > -1) {
        // Already selected - remove it
        return prev.filter(id => id !== slideId);
      } else {
        // Not selected - add to end
        return [...prev, slideId];
      }
    });
  };

  const getSlidePosition = (slideId) => {
    const index = selectedSlideOrder.indexOf(slideId);
    return index > -1 ? index + 1 : null;
  };

  const handleGenerate = async () => {
    if (!request.trim()) {
      setError('Please enter a request');
      return;
    }

    // In manual mode, use only selected slides in user's order
    if (manualMode && selectedSlideOrder.length === 0) {
      setError('Please select at least one slide by clicking on them in order');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const requestData = {
        request: request,
        add_agenda: addAgenda,
        add_notes: addNotes,
        client_name: clientName || null,
        custom_title: customTitle || null
      };

      // Add manual slide selection if in manual mode (already in correct order)
      if (manualMode) {
        requestData.slide_ids = selectedSlideOrder;
      }

      const response = await axios.post('http://localhost:8000/api/deck-generation/generate', requestData);

      if (response.data.success) {
        setResult({
          type: 'generated',
          deckId: response.data.deck_id,
          downloadUrl: `http://localhost:8000${response.data.download_url}`,
          slideCount: response.data.slide_count,
          estimatedDuration: response.data.estimated_duration_minutes,
          parsedRequest: response.data.parsed_request,
          slides: response.data.slides
        });
        setPreviewSlides(response.data.slides);
      } else {
        setError(response.data.message || 'Failed to generate deck');
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate deck');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (result && result.downloadUrl) {
      window.open(result.downloadUrl, '_blank');
    }
  };

  const handleReset = () => {
    setRequest('');
    setClientName('');
    setCustomTitle('');
    setResult(null);
    setError(null);
    setPreviewSlides([]);
  };

  return (
    <div className="ask-page">
      <div className="ask-container">
        <div className="ask-header">
          <h1>AI Deck Generator</h1>
          <p>Describe your presentation needs and let AI create it for you</p>
        </div>

        <div className="ask-form">
          {/* Main Request Input */}
          <div className="form-group">
            <label htmlFor="request">What presentation do you need?</label>
            <textarea
              id="request"
              value={request}
              onChange={(e) => setRequest(e.target.value)}
              placeholder="Example: Create a 15-minute Maximo demo for manufacturing clients focusing on predictive maintenance and cost reduction"
              rows="4"
              disabled={loading || previewing}
            />
          </div>

          {/* Optional Fields */}
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="clientName">Client Name (Optional)</label>
              <input
                type="text"
                id="clientName"
                value={clientName}
                onChange={(e) => setClientName(e.target.value)}
                placeholder="Acme Manufacturing"
                disabled={loading || previewing}
              />
            </div>

            <div className="form-group">
              <label htmlFor="customTitle">Custom Title (Optional)</label>
              <input
                type="text"
                id="customTitle"
                value={customTitle}
                onChange={(e) => setCustomTitle(e.target.value)}
                placeholder="Leave blank for AI-generated title"
                disabled={loading || previewing}
              />
            </div>
          </div>

          {/* Checkboxes */}
          <div className="form-checkboxes">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={addAgenda}
                onChange={(e) => setAddAgenda(e.target.checked)}
                disabled={loading || previewing}
              />
              <span>Add agenda slide</span>
            </label>

            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={addNotes}
                onChange={(e) => setAddNotes(e.target.checked)}
                disabled={loading || previewing}
              />
              <span>Generate presenter notes</span>
            </label>
          </div>

          {/* Action Buttons */}
          <div className="form-actions">
            <button
              onClick={handlePreview}
              disabled={loading || previewing || !request.trim()}
              className="btn-secondary"
            >
              {previewing ? 'Previewing...' : 'Preview Slides'}
            </button>

            <button
              onClick={handleGenerate}
              disabled={loading || previewing || !request.trim()}
              className="btn-primary"
            >
              {loading ? 'Generating...' : 'Generate Deck'}
            </button>

            {(result || error) && (
              <button
                onClick={handleReset}
                className="btn-reset"
              >
                Start Over
              </button>
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Result Summary */}
        {result && (
          <div className="result-summary">
            <h2>
              {result.type === 'preview' ? '📋 Preview' : '✅ Deck Generated!'}
            </h2>
            
            <div className="result-stats">
              <div className="stat">
                <span className="stat-label">Slides:</span>
                <span className="stat-value">{result.slideCount}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Duration:</span>
                <span className="stat-value">~{result.estimatedDuration} min</span>
              </div>
            </div>

            {result.parsedRequest && (
              <div className="parsed-request">
                <h3>AI Understanding:</h3>
                <div className="parsed-details">
                  {result.parsedRequest.audience && (
                    <span className="badge">Audience: {result.parsedRequest.audience}</span>
                  )}
                  {result.parsedRequest.products && result.parsedRequest.products.length > 0 && (
                    <span className="badge">Products: {result.parsedRequest.products.join(', ')}</span>
                  )}
                  {result.parsedRequest.presentation_type && (
                    <span className="badge">Type: {result.parsedRequest.presentation_type}</span>
                  )}
                </div>
              </div>
            )}

            {result.type === 'generated' && (
              <button onClick={handleDownload} className="btn-download">
                📥 Download PowerPoint
              </button>
            )}
          </div>
        )}

        {/* Preview Slides */}
        {previewSlides.length > 0 && (
          <div className="preview-slides">
            <div className="preview-header">
              <h2>
                {manualMode
                  ? `Selected Slides (${selectedSlideOrder.length})`
                  : `AI Selected Slides (${previewSlides.length})`
                }
              </h2>
              <div className="preview-controls">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={manualMode}
                    onChange={(e) => {
                      setManualMode(e.target.checked);
                      if (!e.target.checked) {
                        setSelectedSlideOrder([]); // Clear selection when turning off manual mode
                      }
                    }}
                  />
                  <span>Manual Selection & Ordering</span>
                </label>
              </div>
            </div>
            
            {manualMode && (
              <div className="manual-mode-hint">
                <p>💡 <strong>Click slides in order:</strong> 1st click = Slide 1, 2nd click = Slide 2, etc. Click again to deselect.</p>
              </div>
            )}

            <div className="slides-grid">
              {previewSlides.map((slide, index) => {
                const position = getSlidePosition(slide.id);
                const isSelected = position !== null;
                
                return (
                  <div
                    key={slide.id}
                    className={`preview-slide-card ${isSelected ? 'selected' : ''} ${manualMode ? 'manual-mode clickable' : ''}`}
                    onClick={() => handleSlideClick(slide.id)}
                    style={{ cursor: manualMode ? 'pointer' : 'default' }}
                  >
                    {manualMode && isSelected && (
                      <div className="selection-badge">{position}</div>
                    )}
                    {!manualMode && (
                      <div className="slide-number">{index + 1}</div>
                    )}
                    <img
                      src={`http://localhost:8000/api/slides/${slide.id}/image`}
                      alt={slide.title || 'Slide'}
                      className="slide-preview-image"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                    <div style={{ display: 'none', alignItems: 'center', justifyContent: 'center', height: '200px', backgroundColor: '#f4f4f4', color: '#525252' }}>
                      Image not available
                    </div>
                    <div className="slide-info">
                      <h4>{slide.title || 'Untitled'}</h4>
                      <p className="slide-meta">
                        Relevance: {(slide.relevance_score * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AskPage;

// Made with Bob
