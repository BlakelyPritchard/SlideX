"""
Deck Generator Service for SlideX
Handles intelligent deck generation from natural language requests
"""

import os
import logging
import json
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.slide import Slide
from app.models.tag import Tag
from app.services.embedding_service import get_embedding_service
from app.services.ai_tagger import get_ai_provider

logger = logging.getLogger(__name__)


class DeckGenerator:
    """Service for generating presentation decks from natural language requests"""
    
    def __init__(self):
        """Initialize the deck generator"""
        self.embedding_service = get_embedding_service()
        self.ai_provider = get_ai_provider()
    
    def parse_request(self, user_request: str) -> Dict:
        """
        Parse natural language request to extract structured information
        
        Args:
            user_request: Natural language description of desired deck
            
        Returns:
            Dictionary with parsed request details
        """
        try:
            # Create prompt for AI to parse the request
            prompt = f"""Parse this presentation request and extract key information.
Return a JSON object with these fields:
- audience: target audience (e.g., "manufacturing", "healthcare", "enterprise")
- products: list of IBM products mentioned (e.g., ["Maximo", "Verify", "Tririga"])
- features: list of specific features or capabilities (e.g., ["predictive maintenance", "asset management"])
- pain_points: list of client pain points (e.g., ["cost reduction", "efficiency", "compliance"])
- duration_minutes: estimated presentation duration in minutes (default 15 if not specified)
- presentation_type: type of presentation (e.g., "demo", "overview", "technical", "executive")
- key_themes: main themes or topics to cover

Request: "{user_request}"

Return only valid JSON, no other text."""

            # Use AI to parse the request
            response = self.ai_provider.generate_text(prompt, max_tokens=500)
            
            # Try to extract JSON from response
            try:
                # Find JSON in response (might have extra text)
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    parsed = json.loads(json_str)
                else:
                    parsed = json.loads(response)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON: {response}")
                # Fallback to basic parsing
                parsed = self._fallback_parse(user_request)
            
            # Ensure required fields exist
            parsed.setdefault('audience', 'general')
            parsed.setdefault('products', [])
            parsed.setdefault('features', [])
            parsed.setdefault('pain_points', [])
            parsed.setdefault('duration_minutes', 15)
            parsed.setdefault('presentation_type', 'demo')
            parsed.setdefault('key_themes', [])
            
            logger.info(f"Parsed request: {parsed}")
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing request: {e}")
            return self._fallback_parse(user_request)
    
    def _fallback_parse(self, user_request: str) -> Dict:
        """
        Fallback parsing using simple keyword matching
        
        Args:
            user_request: User's request text
            
        Returns:
            Dictionary with basic parsed information
        """
        request_lower = user_request.lower()
        
        # Extract products
        products = []
        if 'maximo' in request_lower:
            products.append('Maximo')
        if 'verify' in request_lower:
            products.append('Verify')
        if 'tririga' in request_lower:
            products.append('Tririga')
        
        # Extract audience
        audience = 'general'
        if 'manufacturing' in request_lower:
            audience = 'manufacturing'
        elif 'healthcare' in request_lower:
            audience = 'healthcare'
        elif 'enterprise' in request_lower:
            audience = 'enterprise'
        elif 'government' in request_lower:
            audience = 'government'
        
        # Extract duration
        duration = 15
        if 'minute' in request_lower:
            import re
            match = re.search(r'(\d+)\s*minute', request_lower)
            if match:
                duration = int(match.group(1))
        
        return {
            'audience': audience,
            'products': products,
            'features': [],
            'pain_points': [],
            'duration_minutes': duration,
            'presentation_type': 'demo',
            'key_themes': [],
            'raw_request': user_request
        }
    
    def select_slides(
        self,
        db: Session,
        parsed_request: Dict,
        max_slides: Optional[int] = None
    ) -> List[Tuple[Slide, float]]:
        """
        Select slides based on parsed request using semantic search and tag filtering
        
        Args:
            db: Database session
            parsed_request: Parsed request dictionary
            max_slides: Maximum number of slides to return (calculated from duration if None)
            
        Returns:
            List of tuples (Slide, relevance_score)
        """
        try:
            # Minimum relevance threshold
            MIN_RELEVANCE_SCORE = 0.3
            MIN_SLIDES = 5
            MAX_SLIDES = 15
            
            # Calculate target slides from duration if not specified
            if max_slides is None:
                duration = parsed_request.get('duration_minutes', 15)
                # Rough estimate: 1-2 minutes per slide
                target_slides = min(int(duration * 0.8), MAX_SLIDES)
            else:
                target_slides = min(max_slides, MAX_SLIDES)
            
            # Build search query from parsed request
            query_parts = []
            
            if parsed_request.get('products'):
                query_parts.append(f"Products: {', '.join(parsed_request['products'])}")
            
            if parsed_request.get('features'):
                query_parts.append(f"Features: {', '.join(parsed_request['features'])}")
            
            if parsed_request.get('pain_points'):
                query_parts.append(f"Pain points: {', '.join(parsed_request['pain_points'])}")
            
            if parsed_request.get('key_themes'):
                query_parts.append(f"Themes: {', '.join(parsed_request['key_themes'])}")
            
            if parsed_request.get('audience'):
                query_parts.append(f"Audience: {parsed_request['audience']}")
            
            # Fallback to raw request if no structured data
            if not query_parts and parsed_request.get('raw_request'):
                query_parts.append(parsed_request['raw_request'])
            
            search_query = " | ".join(query_parts)
            logger.info(f"Search query: {search_query}")
            
            # Perform semantic search - get more candidates for filtering
            similar_slides = self.embedding_service.search_similar_slides(
                query=search_query,
                top_k=50  # Get many candidates to filter
            )
            
            # Get slide objects with scores and apply relevance threshold
            slides_with_scores = []
            for slide_id, similarity_score in similar_slides:
                slide = db.query(Slide).filter(Slide.id == slide_id).first()
                if slide:
                    # Apply tag-based boosting
                    boosted_score = self._apply_tag_boost(
                        slide,
                        parsed_request,
                        similarity_score
                    )
                    
                    # Only include slides above minimum relevance threshold
                    if boosted_score >= MIN_RELEVANCE_SCORE:
                        slides_with_scores.append((slide, boosted_score))
            
            logger.info(f"Found {len(slides_with_scores)} slides above {MIN_RELEVANCE_SCORE} relevance threshold")
            
            # Sort by boosted score
            slides_with_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Apply diversity filter to avoid too similar slides
            # Use dynamic count: between MIN_SLIDES and target_slides based on quality
            actual_max = min(len(slides_with_scores), target_slides)
            actual_max = max(actual_max, MIN_SLIDES) if len(slides_with_scores) >= MIN_SLIDES else len(slides_with_scores)
            
            diverse_slides = self._apply_diversity_filter(
                slides_with_scores,
                actual_max
            )
            
            logger.info(f"Selected {len(diverse_slides)} slides (target was {target_slides}, min is {MIN_SLIDES})")
            return diverse_slides
            
        except Exception as e:
            logger.error(f"Error selecting slides: {e}")
            return []
    
    def _apply_tag_boost(
        self,
        slide: Slide,
        parsed_request: Dict,
        base_score: float
    ) -> float:
        """
        Boost slide score based on tag matches
        
        Args:
            slide: Slide object
            parsed_request: Parsed request dictionary
            base_score: Base similarity score
            
        Returns:
            Boosted score
        """
        boost = 0.0
        slide_tag_names = [tag.name.lower() for tag in slide.tags]
        
        # Boost for product matches
        for product in parsed_request.get('products', []):
            if product.lower() in slide_tag_names:
                boost += 0.15
        
        # Boost for feature matches
        for feature in parsed_request.get('features', []):
            feature_normalized = feature.lower().replace(' ', '_')
            if feature_normalized in slide_tag_names:
                boost += 0.10
        
        # Boost for pain point matches
        for pain_point in parsed_request.get('pain_points', []):
            pain_point_normalized = pain_point.lower().replace(' ', '_')
            if pain_point_normalized in slide_tag_names:
                boost += 0.10
        
        # Boost for audience matches
        audience = parsed_request.get('audience', '').lower()
        if audience in slide_tag_names:
            boost += 0.05
        
        return min(base_score + boost, 1.0)  # Cap at 1.0
    
    def _apply_diversity_filter(
        self,
        slides_with_scores: List[Tuple[Slide, float]],
        max_slides: int
    ) -> List[Tuple[Slide, float]]:
        """
        Filter slides to ensure diversity (avoid too similar content)
        
        Args:
            slides_with_scores: List of (Slide, score) tuples
            max_slides: Maximum number of slides to return
            
        Returns:
            Filtered list of (Slide, score) tuples
        """
        if len(slides_with_scores) <= max_slides:
            return slides_with_scores
        
        selected = []
        selected_texts = []
        
        for slide, score in slides_with_scores:
            if len(selected) >= max_slides:
                break
            
            # Check if this slide is too similar to already selected ones
            slide_text = (slide.text_content or '').lower()
            is_diverse = True
            
            for selected_text in selected_texts:
                # Simple similarity check based on word overlap
                slide_words = set(slide_text.split())
                selected_words = set(selected_text.split())
                
                if len(slide_words) > 0 and len(selected_words) > 0:
                    overlap = len(slide_words & selected_words)
                    similarity = overlap / min(len(slide_words), len(selected_words))
                    
                    if similarity > 0.7:  # Too similar
                        is_diverse = False
                        break
            
            if is_diverse:
                selected.append((slide, score))
                selected_texts.append(slide_text)
        
        return selected
    
    def categorize_slides(
        self,
        slides_with_scores: List[Tuple[Slide, float]]
    ) -> Dict[str, List[Tuple[Slide, float]]]:
        """
        Categorize slides by their purpose in the presentation
        
        Args:
            slides_with_scores: List of (Slide, score) tuples
            
        Returns:
            Dictionary mapping categories to slides
        """
        categories = {
            'intro': [],
            'problem': [],
            'solution': [],
            'demo': [],
            'value': [],
            'closing': []
        }
        
        for slide, score in slides_with_scores:
            # Analyze slide content and tags to determine category
            slide_text = (slide.text_content or '').lower()
            slide_tags = [tag.name.lower() for tag in slide.tags]
            
            # Intro slides
            if any(word in slide_text for word in ['agenda', 'overview', 'introduction', 'welcome']):
                categories['intro'].append((slide, score))
            
            # Problem slides
            elif any(word in slide_text for word in ['challenge', 'problem', 'pain', 'issue', 'struggle']):
                categories['problem'].append((slide, score))
            
            # Solution slides
            elif any(word in slide_text for word in ['solution', 'approach', 'how we', 'our platform']):
                categories['solution'].append((slide, score))
            
            # Demo/feature slides
            elif any(word in slide_text for word in ['feature', 'capability', 'function', 'demo', 'example']):
                categories['demo'].append((slide, score))
            
            # Value/ROI slides
            elif any(word in slide_text for word in ['roi', 'benefit', 'value', 'savings', 'reduction', 'improvement']):
                categories['value'].append((slide, score))
            
            # Closing slides
            elif any(word in slide_text for word in ['next steps', 'contact', 'questions', 'thank you', 'summary']):
                categories['closing'].append((slide, score))
            
            # Default to demo if unclear
            else:
                categories['demo'].append((slide, score))
        
        return categories
    
    def order_slides(
        self,
        slides_with_scores: List[Tuple[Slide, float]],
        presentation_type: str = 'demo'
    ) -> List[Slide]:
        """
        Order slides in a logical narrative flow
        
        Args:
            slides_with_scores: List of (Slide, score) tuples
            presentation_type: Type of presentation
            
        Returns:
            Ordered list of Slide objects
        """
        # Categorize slides
        categorized = self.categorize_slides(slides_with_scores)
        
        # Define presentation structure based on type
        if presentation_type == 'executive':
            structure = ['intro', 'value', 'solution', 'closing']
        elif presentation_type == 'technical':
            structure = ['intro', 'solution', 'demo', 'value', 'closing']
        else:  # demo or default
            structure = ['intro', 'problem', 'solution', 'demo', 'value', 'closing']
        
        # Build ordered slide list
        ordered_slides = []
        
        for category in structure:
            category_slides = categorized.get(category, [])
            # Sort by score within category
            category_slides.sort(key=lambda x: x[1], reverse=True)
            # Add slides (without scores)
            ordered_slides.extend([slide for slide, score in category_slides])
        
        logger.info(f"Ordered {len(ordered_slides)} slides in narrative flow")
        return ordered_slides
    
    def generate_deck(
        self,
        db: Session,
        user_request: str,
        max_slides: Optional[int] = None
    ) -> Dict:
        """
        Main method to generate a complete deck from user request
        
        Args:
            db: Database session
            user_request: Natural language request
            max_slides: Optional maximum number of slides
            
        Returns:
            Dictionary with generation results
        """
        try:
            logger.info(f"Generating deck for request: {user_request}")
            
            # Step 1: Parse request
            parsed_request = self.parse_request(user_request)
            
            # Step 2: Select slides
            slides_with_scores = self.select_slides(db, parsed_request, max_slides)
            
            if not slides_with_scores:
                return {
                    'success': False,
                    'error': 'No relevant slides found',
                    'parsed_request': parsed_request
                }
            
            # Step 3: Order slides
            presentation_type = parsed_request.get('presentation_type', 'demo')
            ordered_slides = self.order_slides(slides_with_scores, presentation_type)
            
            # Step 4: Calculate estimated duration
            estimated_duration = len(ordered_slides) * 1.5  # 1.5 min per slide
            
            return {
                'success': True,
                'slides': ordered_slides,
                'slide_count': len(ordered_slides),
                'estimated_duration_minutes': int(estimated_duration),
                'parsed_request': parsed_request,
                'slide_scores': {slide.id: score for slide, score in slides_with_scores}
            }
            
        except Exception as e:
            logger.error(f"Error generating deck: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Global instance
_deck_generator: Optional[DeckGenerator] = None


def get_deck_generator() -> DeckGenerator:
    """
    Get or create the global deck generator instance
    
    Returns:
        DeckGenerator instance
    """
    global _deck_generator
    if _deck_generator is None:
        _deck_generator = DeckGenerator()
    return _deck_generator

# Made with Bob
