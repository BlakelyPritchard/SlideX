import { useState } from 'react';

const API_URL = 'http://localhost:8000';

function SlideCard({ slide, isSelected, onSelect, onDelete }) {
  const [showPreview, setShowPreview] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const getThumbnailUrl = () => {
    // Backend serves static files from the thumbnails directory
    // Remove ./ prefix if present
    const path = slide.thumbnail_path?.replace('./', '') || '';
    const url = `${API_URL}/${path}`;
    console.log('Thumbnail URL:', url, 'from path:', slide.thumbnail_path);
    return url;
  };

  const getFullImageUrl = () => {
    // Backend serves static files from the slides directory
    // Remove ./ prefix if present
    const path = slide.image_path?.replace('./', '') || '';
    const url = `${API_URL}/${path}`;
    console.log('Full image URL:', url, 'from path:', slide.image_path);
    return url;
  };

  const groupTagsByCategory = () => {
    const grouped = {};
    slide.tags?.forEach(tag => {
      if (!grouped[tag.category]) {
        grouped[tag.category] = [];
      }
      grouped[tag.category].push(tag.name);
    });
    return grouped;
  };

  const tagsByCategory = groupTagsByCategory();

  return (
    <>
      <div className={`slide-card ${isSelected ? 'selected' : ''}`}>
        {/* Checkbox */}
        <div className="slide-checkbox">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={() => onSelect(slide.id)}
            onClick={(e) => e.stopPropagation()}
          />
        </div>

        {/* Delete Button */}
        <button
          className="slide-delete-button"
          onClick={(e) => {
            e.stopPropagation();
            setShowDeleteConfirm(true);
          }}
          title="Delete slide"
        >
          🗑️
        </button>

        {/* Thumbnail */}
        <div 
          className="slide-thumbnail"
          onClick={() => setShowPreview(true)}
        >
          <img 
            src={getThumbnailUrl()} 
            alt={slide.title || `Slide ${slide.slide_number}`}
            onError={(e) => {
              e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150"><rect width="200" height="150" fill="%23f0f0f0"/><text x="50%" y="50%" text-anchor="middle" fill="%23999">No Image</text></svg>';
            }}
          />
          <div className="slide-overlay">
            <span>Click to preview</span>
          </div>
        </div>

        {/* Slide Info */}
        <div className="slide-info">
          <h4 className="slide-title">
            {slide.title || `Slide ${slide.slide_number}`}
          </h4>
          <p className="slide-filename">
            {slide.original_filename} - Slide {slide.slide_number}
          </p>

          {/* Tags */}
          {slide.tags && slide.tags.length > 0 && (
            <div className="slide-tags">
              {Object.entries(tagsByCategory).map(([category, tags]) => (
                <div key={category} className="tag-group">
                  <span className="tag-category-label">
                    {category.replace('_', ' ')}:
                  </span>
                  {tags.map((tagName, idx) => (
                    <span key={idx} className={`tag tag-${category}`}>
                      {tagName}
                    </span>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && (
        <div className="modal-overlay" onClick={() => setShowPreview(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button 
              className="modal-close"
              onClick={() => setShowPreview(false)}
            >
              ✕
            </button>
            
            <div className="modal-body">
              <img 
                src={getFullImageUrl()} 
                alt={slide.title || `Slide ${slide.slide_number}`}
                className="preview-image"
                onError={(e) => {
                  e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><rect width="800" height="600" fill="%23f0f0f0"/><text x="50%" y="50%" text-anchor="middle" fill="%23999" font-size="24">Image not available</text></svg>';
                }}
              />
              
              <div className="modal-info">
                <h3>{slide.title || `Slide ${slide.slide_number}`}</h3>
                <p className="modal-filename">
                  {slide.original_filename} - Slide {slide.slide_number}
                </p>
                
                {slide.text_content && (
                  <div className="slide-content">
                    <h4>Content:</h4>
                    <p>{slide.text_content}</p>
                  </div>
                )}

                {slide.tags && slide.tags.length > 0 && (
                  <div className="modal-tags">
                    <h4>Tags:</h4>
                    {Object.entries(tagsByCategory).map(([category, tags]) => (
                      <div key={category} className="tag-group">
                        <strong>{category.replace('_', ' ')}:</strong>
                        {tags.map((tagName, idx) => (
                          <span key={idx} className={`tag tag-${category}`}>
                            {tagName}
                          </span>
                        ))}
                      </div>
                    ))}
                  </div>
                )}

                <button 
                  className="select-button"
                  onClick={() => {
                    onSelect(slide.id);
                    setShowPreview(false);
                  }}
                >
                  {isSelected ? 'Deselect' : 'Select'} this slide
                </button>

                <button
                  className="delete-button-modal"
                  onClick={() => {
                    setShowPreview(false);
                    setShowDeleteConfirm(true);
                  }}
                >
                  Delete this slide
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="modal-overlay" onClick={() => setShowDeleteConfirm(false)}>
          <div className="modal-content delete-confirm-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Delete Slide?</h3>
            <p>Are you sure you want to delete this slide?</p>
            <p className="delete-warning">
              <strong>{slide.title || `Slide ${slide.slide_number}`}</strong>
              <br />
              {slide.original_filename}
            </p>
            <p className="delete-note">This action cannot be undone.</p>
            
            <div className="modal-actions">
              <button
                className="cancel-button"
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancel
              </button>
              <button
                className="confirm-delete-button"
                onClick={() => {
                  onDelete(slide.id);
                  setShowDeleteConfirm(false);
                }}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default SlideCard;

// Made with Bob
