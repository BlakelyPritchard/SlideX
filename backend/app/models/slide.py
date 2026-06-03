"""
Slide database model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


# Association table for many-to-many relationship between slides and tags
slide_tags = Table(
    'slide_tags',
    Base.metadata,
    Column('slide_id', Integer, ForeignKey('slides.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)


class Slide(Base):
    """
    Slide model representing individual presentation slides
    """
    __tablename__ = "slides"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    slide_number = Column(Integer, nullable=False)
    image_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500), nullable=False)
    
    # Content
    text_content = Column(Text, nullable=True)
    title = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tags = relationship("Tag", secondary=slide_tags, back_populates="slides")
    
    def __repr__(self):
        return f"<Slide {self.id}: {self.original_filename} - Slide {self.slide_number}>"

# Made with Bob
