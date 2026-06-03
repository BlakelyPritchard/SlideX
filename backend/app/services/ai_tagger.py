"""
AI Tagging service
Uses OpenAI or Anthropic to automatically tag slides
"""
import json
from typing import List, Dict
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.tag import Tag


class AITagger:
    """Generate tags for slides using AI"""
    
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.anthropic_key = settings.ANTHROPIC_API_KEY
        self.roo_key = settings.ROO_API_KEY
        self.roo_url = settings.ROO_API_URL
        self.watsonx_key = settings.WATSONX_API_KEY
        self.watsonx_project_id = settings.WATSONX_PROJECT_ID
        self.watsonx_url = settings.WATSONX_URL
        self.categories = [
            "client_painpoint",
            "client_type",
            "software_type",
            "software_function"
        ]
    
    async def generate_tags(self, text_content: str, title: str, db=None) -> List[Tag]:
        """
        Generate tags for a slide based on its content
        Returns list of Tag objects
        """
        # Combine title and content for analysis
        full_content = f"Title: {title}\n\nContent: {text_content}"
        
        # Generate tags using AI (priority order)
        if self.openai_key:
            tag_suggestions = await self._generate_with_openai(full_content)
        elif self.anthropic_key:
            tag_suggestions = await self._generate_with_anthropic(full_content)
        elif self.roo_key:
            tag_suggestions = await self._generate_with_roo(full_content)
        elif self.watsonx_key:
            tag_suggestions = await self._generate_with_watsonx(full_content)
        else:
            # Fallback: basic keyword extraction
            tag_suggestions = self._generate_basic_tags(full_content)
        
        # Get or create tags in database
        if db is None:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
            
        tags = []
        
        for category, tag_names in tag_suggestions.items():
            for tag_name in tag_names:
                try:
                    # Check if tag exists
                    tag = db.query(Tag).filter(
                        Tag.name == tag_name,
                        Tag.category == category
                    ).first()
                    
                    # Create if doesn't exist
                    if not tag:
                        tag = Tag(name=tag_name, category=category)
                        db.add(tag)
                        db.commit()
                        db.refresh(tag)
                    
                    tags.append(tag)
                except Exception as e:
                    # If there's a duplicate key error, rollback and try to fetch again
                    db.rollback()
                    tag = db.query(Tag).filter(
                        Tag.name == tag_name,
                        Tag.category == category
                    ).first()
                    if tag:
                        tags.append(tag)
                    else:
                        print(f"Error creating tag {tag_name}: {e}")
        
        if close_db:
            db.close()
        return tags
    
    async def _generate_with_openai(self, content: str) -> Dict[str, List[str]]:
        """Generate tags using OpenAI API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            prompt = f"""Analyze this presentation slide and categorize it with relevant tags.

Slide Content:
{content}

Provide tags in these categories:
1. client_painpoint: What business problems does this address? (e.g., "data security", "scalability", "cost reduction")
2. client_type: What type of organization is this for? (e.g., "enterprise", "SMB", "startup")
3. software_type: What category of software? (e.g., "CRM", "analytics", "automation")
4. software_function: What specific capabilities? (e.g., "reporting", "integration", "dashboard")

Return ONLY a JSON object with these category keys and arrays of tag strings. Keep tags concise (1-3 words).
Example: {{"client_painpoint": ["data security"], "client_type": ["enterprise"], "software_type": ["CRM"], "software_function": ["reporting"]}}
"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that categorizes presentation slides."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._generate_basic_tags(content)
    
    async def _generate_with_anthropic(self, content: str) -> Dict[str, List[str]]:
        """Generate tags using Anthropic API"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            
            prompt = f"""Analyze this presentation slide and categorize it with relevant tags.

Slide Content:
{content}

Provide tags in these categories:
1. client_painpoint: What business problems does this address?
2. client_type: What type of organization is this for?
3. software_type: What category of software?
4. software_function: What specific capabilities?

Return ONLY a JSON object with these category keys and arrays of tag strings.
"""
            
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(message.content[0].text)
            return result
            
        except Exception as e:
            print(f"Anthropic error: {e}")
            return self._generate_basic_tags(content)
    
    async def _generate_with_roo(self, content: str) -> Dict[str, List[str]]:
        """Generate tags using Roo (Bob) API"""
        try:
            import requests
            
            prompt = f"""Analyze this presentation slide and categorize it with relevant tags.

Slide Content:
{content}

Provide tags in these categories:
1. client_painpoint: What business problems does this address?
2. client_type: What type of organization is this for?
3. software_type: What category of software?
4. software_function: What specific capabilities?

Return ONLY a JSON object with these category keys and arrays of tag strings.
"""
            
            headers = {
                "Authorization": f"Bearer {self.roo_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "roo-chat",  # Adjust based on Roo's model naming
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that categorizes presentation slides."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            
            response = requests.post(
                f"{self.roo_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result_text = response.json()["choices"][0]["message"]["content"]
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            print(f"Roo API error: {e}")
            return self._generate_basic_tags(content)
    
    async def _generate_with_watsonx(self, content: str) -> Dict[str, List[str]]:
        """Generate tags using IBM WatsonX.ai API"""
        try:
            import requests
            
            prompt = f"""Analyze this presentation slide and categorize it with relevant tags.

Slide Content:
{content}

Provide tags in these categories:
1. client_painpoint: What business problems does this address?
2. client_type: What type of organization is this for?
3. software_type: What category of software?
4. software_function: What specific capabilities?

Return ONLY a JSON object with these category keys and arrays of tag strings.
Example: {{"client_painpoint": ["data security"], "client_type": ["enterprise"], "software_type": ["CRM"], "software_function": ["reporting"]}}
"""
            
            # WatsonX authentication
            headers = {
                "Authorization": f"Bearer {self.watsonx_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = {
                "input": prompt,
                "model_id": "ibm/granite-13b-chat-v2",  # Or another WatsonX model
                "project_id": self.watsonx_project_id,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.3,
                    "top_p": 1,
                    "top_k": 50
                }
            }
            
            response = requests.post(
                f"{self.watsonx_url}/ml/v1/text/generation?version=2023-05-29",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result_text = response.json()["results"][0]["generated_text"]
            # Extract JSON from response
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            print(f"WatsonX API error: {e}")
            return self._generate_basic_tags(content)
    
    def _generate_basic_tags(self, content: str) -> Dict[str, List[str]]:
        """
        Fallback: Generate basic tags using keyword matching
        Used when no AI API is configured
        """
        content_lower = content.lower()
        
        tags = {
            "client_painpoint": [],
            "client_type": [],
            "software_type": [],
            "software_function": []
        }
        
        # Simple keyword matching
        painpoint_keywords = {
            "security": "data security",
            "scale": "scalability",
            "cost": "cost reduction",
            "efficiency": "efficiency",
            "integration": "integration challenges"
        }
        
        type_keywords = {
            "enterprise": "enterprise",
            "small business": "SMB",
            "startup": "startup"
        }
        
        software_keywords = {
            "crm": "CRM",
            "analytics": "analytics",
            "automation": "automation",
            "dashboard": "dashboard"
        }
        
        function_keywords = {
            "report": "reporting",
            "integrate": "integration",
            "dashboard": "dashboard",
            "analyze": "analysis"
        }
        
        # Match keywords
        for keyword, tag in painpoint_keywords.items():
            if keyword in content_lower:
                tags["client_painpoint"].append(tag)
        
        for keyword, tag in type_keywords.items():
            if keyword in content_lower:
                tags["client_type"].append(tag)
        
        for keyword, tag in software_keywords.items():
            if keyword in content_lower:
                tags["software_type"].append(tag)
        
        for keyword, tag in function_keywords.items():
            if keyword in content_lower:
                tags["software_function"].append(tag)
        
        # Ensure at least one tag per category
        if not tags["client_painpoint"]:
            tags["client_painpoint"] = ["general"]
        if not tags["client_type"]:
            tags["client_type"] = ["general"]
        if not tags["software_type"]:
            tags["software_type"] = ["general"]
        if not tags["software_function"]:
            tags["software_function"] = ["general"]
        
        return tags

# Made with Bob
