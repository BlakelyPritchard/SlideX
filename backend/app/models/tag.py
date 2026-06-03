"""
Tag database model
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.slide import slide_tags


class Tag(Base):
    """
    Tag model for categorizing slides
    Categories: client_painpoint, client_type, software_type, software_function
    """
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Tag information
    name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=False, index=True)  # client_painpoint, client_type, etc.
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    slides = relationship("Slide", secondary=slide_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag {self.id}: {self.category} - {self.name}>"

# Made with Bob
