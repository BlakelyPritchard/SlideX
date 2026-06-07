import { useState, useEffect } from 'react';
import axios from 'axios';
import SlideCard from './SlideCard';

const API_URL = 'http://localhost:8000';

function SearchPage() {
  const [slides, setSlides] = useState([]);
  const [filteredSlides, setFilteredSlides] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState({});
  const [availableTags, setAvailableTags] = useState({});
  const [selectedSlides, setSelectedSlides] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [exportFilename, setExportFilename] = useState('');

  // Fetch all slides on component mount
  useEffect(() => {
    fetchSlides();
    fetchTags();
  }, []);

  // Filter slides when search query or tags change
  useEffect(() => {
    filterSlides();
  }, [searchQuery, selectedTags, slides]);

  const fetchSlides = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/slides/`);
      setSlides(response.data.slides || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching slides:', error);
      setMessage('Error loading slides');
      setLoading(false);
    }
  };

  const fetchTags = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/tags/`);
      // Backend returns { tags: { category: [tags] } }
      const tagsByCategory = response.data.tags || {};
      
      // Transform to include category in each tag object for easier filtering
      const transformedTags = {};
      Object.keys(tagsByCategory).forEach(category => {
        transformedTags[category] = tagsByCategory[category].map(tag => ({
          ...tag,
          category: category
        }));
      });
      
      setAvailableTags(transformedTags);
    } catch (error) {
      console.error('Error fetching tags:', error);
    }
  };

  const filterSlides = () => {
    let filtered = [...slides];

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(slide =>
        slide.title?.toLowerCase().includes(query) ||
        slide.text_content?.toLowerCase().includes(query) ||
        slide.original_filename?.toLowerCase().includes(query)
      );
    }

    // Filter by selected tags
    Object.entries(selectedTags).forEach(([category, tagNames]) => {
      if (tagNames.length > 0) {
        filtered = filtered.filter(slide =>
          slide.tags?.some(tag =>
            tag.category === category && tagNames.includes(tag.name)
          )
        );
      }
    });

    setFilteredSlides(filtered);
  };

  const handleTagToggle = (category, tagName) => {
    setSelectedTags(prev => {
      const categoryTags = prev[category] || [];
      const newCategoryTags = categoryTags.includes(tagName)
        ? categoryTags.filter(t => t !== tagName)
        : [...categoryTags, tagName];
      
      return {
        ...prev,
        [category]: newCategoryTags
      };
    });
  };

  const handleSlideSelect = (slideId) => {
    setSelectedSlides(prev => {
      const newSet = new Set(prev);
      if (newSet.has(slideId)) {
        newSet.delete(slideId);
      } else {
        newSet.add(slideId);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (selectedSlides.size === filteredSlides.length) {
      setSelectedSlides(new Set());
    } else {
      setSelectedSlides(new Set(filteredSlides.map(s => s.id)));
    }
  };

  const handleExport = async () => {
    if (selectedSlides.size === 0) {
      setMessage('Please select at least one slide to export');
      return;
    }

    try {
      const requestBody = {
        slide_ids: Array.from(selectedSlides)
      };
      
      // Determine filename
      let filename = 'selected_slides.pptx';
      if (exportFilename.trim()) {
        requestBody.filename = exportFilename.trim();
        // Use the custom filename directly
        filename = exportFilename.trim();
        // Add .pptx extension if not present
        if (!filename.toLowerCase().endsWith('.pptx')) {
          filename += '.pptx';
        }
      } else {
        // Use timestamped default
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        filename = `slidex_export_${timestamp}.pptx`;
      }

      const response = await axios.post(
        `${API_URL}/api/search/export`,
        requestBody,
        { responseType: 'blob' }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setMessage(`Exported ${selectedSlides.size} slides successfully!`);
      setSelectedSlides(new Set());
      setExportFilename(''); // Clear filename after export
    } catch (error) {
      console.error('Export error:', error);
      setMessage('Error exporting slides');
    }
  };

  const handleDelete = async (slideId) => {
    try {
      await axios.delete(`${API_URL}/api/slides/${slideId}`);
      
      // Remove from selected slides if it was selected
      setSelectedSlides(prev => {
        const newSet = new Set(prev);
        newSet.delete(slideId);
        return newSet;
      });
      
      // Refresh slides list
      await fetchSlides();
      
      setMessage('Slide deleted successfully');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Delete error:', error);
      setMessage('Error deleting slide');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const [showBatchDeleteConfirm, setShowBatchDeleteConfirm] = useState(false);

  const handleBatchDelete = async () => {
    try {
      const slideIds = Array.from(selectedSlides);
      await axios({
        method: 'delete',
        url: `${API_URL}/api/slides/batch`,
        data: { slide_ids: slideIds }
      });
      
      // Clear selected slides
      setSelectedSlides(new Set());
      
      // Refresh slides list
      await fetchSlides();
      
      setMessage(`${slideIds.length} slide(s) deleted successfully`);
      setTimeout(() => setMessage(''), 3000);
      setShowBatchDeleteConfirm(false);
    } catch (error) {
      console.error('Batch delete error:', error);
      setMessage('Error deleting slides');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedTags({});
    setSelectedSlides(new Set());
    setExportFilename('');
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading slides...</p>
      </div>
    );
  }

  return (
    <div className="search-page">
      <div className="search-header">
        <h2>Search Slides</h2>
        <p className="subtitle">Find and export slides for your next presentation</p>
      </div>

      {/* Search Bar */}
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search by title, content, or filename..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
        {(searchQuery || Object.values(selectedTags).some(t => t.length > 0)) && (
          <button onClick={clearFilters} className="clear-button">
            Clear Filters
          </button>
        )}
      </div>

      {/* Tag Filters */}
      <div className="filters-section">
        <h3>Filter by Tags</h3>
        <div className="tag-filters">
          {Object.entries(availableTags).map(([category, tags]) => (
            <div key={category} className="filter-category">
              <h4>{category.replace('_', ' ')}</h4>
              <div className="tag-buttons">
                {tags.map(tag => (
                  <button
                    key={tag.id}
                    className={`tag-button ${selectedTags[category]?.includes(tag.name) ? 'active' : ''}`}
                    onClick={() => handleTagToggle(category, tag.name)}
                  >
                    {tag.name}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Results Header */}
      <div className="results-header">
        <div className="results-info">
          <p>{filteredSlides.length} slides found</p>
          {selectedSlides.size > 0 && (
            <p className="selected-count">{selectedSlides.size} selected</p>
          )}
        </div>
        <div className="results-actions">
          {filteredSlides.length > 0 && (
            <button onClick={handleSelectAll} className="select-all-button">
              {selectedSlides.size === filteredSlides.length ? 'Deselect All' : 'Select All'}
            </button>
          )}
          {selectedSlides.size > 0 && (
            <>
              <button
                onClick={() => setShowBatchDeleteConfirm(true)}
                className="delete-selected-button"
              >
                Delete Selected ({selectedSlides.size})
              </button>
              <input
                type="text"
                placeholder="Filename (optional)"
                value={exportFilename}
                onChange={(e) => setExportFilename(e.target.value)}
                className="filename-input"
              />
              <button onClick={handleExport} className="export-button">
                Export Selected ({selectedSlides.size})
              </button>
            </>
          )}
        </div>
      </div>

      {/* Message */}
      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      {/* Slides Grid */}
      {filteredSlides.length === 0 ? (
        <div className="no-results">
          <p>No slides found</p>
          <p className="hint">Try adjusting your search or filters</p>
        </div>
      ) : (
        <div className="slides-grid">
          {filteredSlides.map(slide => (
            <SlideCard
              key={slide.id}
              slide={slide}
              isSelected={selectedSlides.has(slide.id)}
              onSelect={handleSlideSelect}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {/* Batch Delete Confirmation Modal */}
      {showBatchDeleteConfirm && (
        <div className="delete-confirm-modal" onClick={() => setShowBatchDeleteConfirm(false)}>
          <div className="delete-confirm-content" onClick={(e) => e.stopPropagation()}>
            <h3>Delete Selected Slides?</h3>
            <p className="delete-warning">
              You are about to delete <strong>{selectedSlides.size}</strong> slide(s).
            </p>
            <p className="delete-note">
              This action cannot be undone. The slides will be permanently removed from the database and file system.
            </p>
            <div className="delete-actions">
              <button
                onClick={() => setShowBatchDeleteConfirm(false)}
                className="cancel-button"
              >
                Cancel
              </button>
              <button
                onClick={handleBatchDelete}
                className="confirm-delete-button"
              >
                Delete {selectedSlides.size} Slide(s)
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchPage;

// Made with Bob
