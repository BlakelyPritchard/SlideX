"""
AI Tagging service
Uses OpenAI or Anthropic to automatically tag slides
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
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
        self.watsonx_iam_key = settings.WATSONX_IAM_API_KEY
        self.watsonx_access_token = settings.WATSONX_ACCESS_TOKEN
        self.watsonx_project_id = settings.WATSONX_PROJECT_ID
        self.watsonx_url = settings.WATSONX_URL
        
        # Ollama settings
        self.use_ollama = settings.USE_OLLAMA
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_MODEL
        self.use_ocr = settings.USE_OCR
        
        self.categories = [
            "client_painpoint",
            "client_type",
            "software_type",
            "software_function",
            "slide_type"
        ]
        # Token caching for WatsonX
        self._cached_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        
        # Initialize OCR if enabled
        self._ocr_engine = None
        if self.use_ocr and self.use_ollama:
            try:
                from paddleocr import PaddleOCR
                self._ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            except Exception as e:
                print(f"Warning: Could not initialize PaddleOCR: {e}")
                self._ocr_engine = None
    
    async def generate_tags(self, text_content: str, title: str, db=None, filename: str = "", slide_number: int = 0, total_slides: int = 0, image_path: str = "") -> List[Tag]:
        """
        Generate tags for a slide based on its content, filename, and position
        Returns list of Tag objects
        """
        # Combine filename, title and content for analysis
        full_content = f"Filename: {filename}\n\nTitle: {title}\n\nContent: {text_content}"
        
        # Determine slide type based on position and content
        slide_type = self._determine_slide_type(slide_number, total_slides, title, text_content)
        
        # Generate tags using AI (priority order: Ollama if enabled, then WatsonX, then others)
        if self.use_ollama:
            tag_suggestions = await self._generate_with_ollama(full_content, image_path)
        elif (self.watsonx_iam_key or self.watsonx_access_token) and self.watsonx_project_id:
            tag_suggestions = await self._generate_with_watsonx(full_content)
        elif self.openai_key:
            tag_suggestions = await self._generate_with_openai(full_content)
        elif self.anthropic_key:
            tag_suggestions = await self._generate_with_anthropic(full_content)
        elif self.roo_key:
            tag_suggestions = await self._generate_with_roo(full_content)
        else:
            # Fallback: basic keyword extraction
            tag_suggestions = self._generate_basic_tags(full_content)
        
        # Always add slide type tag based on position
        if slide_type and "slide_type" not in tag_suggestions:
            tag_suggestions["slide_type"] = []
        if slide_type:
            tag_suggestions["slide_type"].append(slide_type)
        
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
3. software_type: What category of software? Use these IBM product names when relevant:
   - Maximo (for asset management, maintenance, monitoring, mobile, visual inspection, service)
   - Tririga (for space management, capital planning, lease management)
   - Verify (for IAM, authentication, risk, delegation, consent, continuous audit)
   - Other: CRM, ERP, analytics, automation
4. software_function: What specific capabilities? Match to products:
   - Maximo: asset_management, mobile, maintenance, monitoring, visual_inspection, service
   - Verify: IAM, authentication, risk, delegation, consent, continuous_audit
   - Tririga: space_management, capital_planning, lease_management
   - General: reporting, integration, dashboard, analysis

Return ONLY a JSON object with these category keys and arrays of tag strings. Keep tags concise (1-3 words).
Example: {{"client_painpoint": ["data security"], "client_type": ["enterprise"], "software_type": ["Maximo"], "software_function": ["asset_management", "monitoring"]}}
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
3. software_type: What category of software? Use these IBM product names when relevant:
   - Maximo (for asset management, maintenance, monitoring, mobile, visual inspection, service)
   - Tririga (for space management, capital planning, lease management)
   - Verify (for IAM, authentication, risk, delegation, consent, continuous audit)
   - Other: CRM, ERP, analytics, automation
4. software_function: What specific capabilities? Match to products:
   - Maximo: asset_management, mobile, maintenance, monitoring, visual_inspection, service
   - Verify: IAM, authentication, risk, delegation, consent, continuous_audit
   - Tririga: space_management, capital_planning, lease_management
   - General: reporting, integration, dashboard, analysis

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
3. software_type: What category of software? Use these IBM product names when relevant:
   - Maximo (for asset management, maintenance, monitoring, mobile, visual inspection, service)
   - Tririga (for space management, capital planning, lease management)
   - Verify (for IAM, authentication, risk, delegation, consent, continuous audit)
   - Other: CRM, ERP, analytics, automation
4. software_function: What specific capabilities? Match to products:
   - Maximo: asset_management, mobile, maintenance, monitoring, visual_inspection, service
   - Verify: IAM, authentication, risk, delegation, consent, continuous_audit
   - Tririga: space_management, capital_planning, lease_management
   - General: reporting, integration, dashboard, analysis

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
    
    async def _get_watsonx_token(self) -> str:
        """
        Get WatsonX access token using IAM API key.
        Implements token caching and automatic refresh as per IBM documentation:
        https://www.ibm.com/docs/en/watsonx/saas?topic=code-coding-deploying-ai-services-manually
        """
        # If we have a manual access token, use it
        if self.watsonx_access_token:
            return self.watsonx_access_token
        
        # Check if cached token is still valid (with 5 min buffer)
        if self._cached_token and self._token_expiry:
            if datetime.now() < self._token_expiry - timedelta(minutes=5):
                return self._cached_token
        
        # Get new token from IAM
        import requests
        
        iam_url = "https://iam.cloud.ibm.com/identity/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.watsonx_iam_key
        }
        
        response = requests.post(iam_url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        
        token_data = response.json()
        self._cached_token = token_data["access_token"]
        # Tokens expire in 1 hour (3600 seconds)
        self._token_expiry = datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600))
        
        return self._cached_token
    
    
    async def _generate_with_watsonx(self, content: str) -> Dict[str, List[str]]:
        """Generate tags using IBM WatsonX.ai API with Llama-3.3-70B"""
        try:
            import requests
            
            # Get access token (automatically refreshes if needed)
            access_token = await self._get_watsonx_token()
            
            # Optimized prompt for Llama-3.3-70B with product-specific keywords
            system_prompt = """You are an expert at categorizing presentation slides for a sales team. Analyze slides and assign specific, relevant tags in 5 categories:

1. client_painpoint: Business problems addressed (e.g., cost_reduction, data_security, identity_management, compliance, scalability, integration_challenges)
2. client_type: Target organization type (e.g., enterprise, SMB, government, healthcare, financial_services, manufacturing)
3. software_type: Software category - Use these IBM product names when relevant:
   - Maximo (for asset management, maintenance, monitoring, mobile, visual inspection, service)
   - Tririga (for space management, capital planning, lease management)
   - Verify (for IAM, authentication, risk, delegation, consent, continuous audit)
   - Other: CRM, ERP, analytics, automation
4. software_function: Specific capabilities - Match to products:
   - Maximo: asset_management, mobile, maintenance, monitoring, visual_inspection, service
   - Verify: IAM, authentication, risk, delegation, consent, continuous_audit
   - Tririga: space_management, capital_planning, lease_management
   - General: reporting, integration, dashboard, analysis
5. slide_type: Presentation structure (e.g., title_slide, agenda, content, feature_highlight, demo, case_study, closing_slide)

Return ONLY valid JSON with these exact category keys and arrays of concise tag strings (1-3 words each)."""

            user_prompt = f"""Analyze this slide and provide tags:

{content}

Return JSON format:
{{"client_painpoint": ["tag1", "tag2"], "client_type": ["tag1"], "software_type": ["tag1"], "software_function": ["tag1", "tag2"], "slide_type": ["tag1"]}}"""
            
            # WatsonX authentication with access token
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Use Llama-3.3-70B model
            payload = {
                "input": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
                "model_id": "meta-llama/llama-3-3-70b-instruct",
                "project_id": self.watsonx_project_id,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.2,
                    "top_p": 0.95,
                    "top_k": 50,
                    "repetition_penalty": 1.1
                }
            }
            
            response = requests.post(
                f"{self.watsonx_url}/ml/v1/text/generation?version=2023-05-29",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result_text = response.json()["results"][0]["generated_text"].strip()
            
            # Extract JSON from response (handle potential markdown formatting)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            # Validate all required categories are present
            required_categories = ["client_painpoint", "client_type", "software_type", "software_function", "slide_type"]
            for category in required_categories:
                if category not in result:
                    result[category] = []
            
            return result
            
        except Exception as e:
            print(f"WatsonX API error: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_basic_tags(content)
    
    async def _generate_with_ollama(self, content: str, image_path: str = "") -> Dict[str, List[str]]:
        """
        Generate tags using Ollama with LLaVA model + PaddleOCR
        Combines OCR text extraction with vision model for best results
        """
        try:
            import ollama
            import base64
            
            # Step 1: Extract text using PaddleOCR if available and image exists
            ocr_text = ""
            if self._ocr_engine and image_path and os.path.exists(image_path):
                try:
                    result = self._ocr_engine.ocr(image_path, cls=True)
                    if result and result[0]:
                        ocr_text = "\n".join([line[1][0] for line in result[0]])
                        print(f"OCR extracted {len(ocr_text)} characters from slide")
                except Exception as e:
                    print(f"OCR extraction failed: {e}")
            
            # Step 2: Combine OCR text with existing content
            enhanced_content = content
            if ocr_text:
                enhanced_content = f"{content}\n\nOCR Extracted Text:\n{ocr_text}"
            
            # Step 3: Prepare prompt for LLaVA with product-specific keywords
            system_prompt = """You are an expert at categorizing presentation slides for a sales team. Analyze slides and assign specific, relevant tags in 5 categories:

1. client_painpoint: Business problems addressed (e.g., cost_reduction, data_security, identity_management, compliance, scalability, integration_challenges)
2. client_type: Target organization type (e.g., enterprise, SMB, government, healthcare, financial_services, manufacturing)
3. software_type: Software category - Use these IBM product names when relevant:
   - Maximo (for asset management, maintenance, monitoring, mobile, visual inspection, service)
   - Tririga (for space management, capital planning, lease management)
   - Verify (for IAM, authentication, risk, delegation, consent, continuous audit)
   - Other: CRM, ERP, analytics, automation
4. software_function: Specific capabilities - Match to products:
   - Maximo: asset_management, mobile, maintenance, monitoring, visual_inspection, service
   - Verify: IAM, authentication, risk, delegation, consent, continuous_audit
   - Tririga: space_management, capital_planning, lease_management
   - General: reporting, integration, dashboard, analysis
5. slide_type: Presentation structure (e.g., title_slide, agenda, content, feature_highlight, demo, case_study, closing_slide)

Return ONLY valid JSON with these exact category keys and arrays of concise tag strings (1-3 words each)."""

            user_prompt = f"""Analyze this slide and provide tags:

{enhanced_content}

Return JSON format:
{{"client_painpoint": ["tag1", "tag2"], "client_type": ["tag1"], "software_type": ["tag1"], "software_function": ["tag1", "tag2"], "slide_type": ["tag1"]}}"""
            
            # Step 4: Call Ollama with image if available
            if image_path and os.path.exists(image_path):
                # Read and encode image
                with open(image_path, 'rb') as img_file:
                    image_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                response = ollama.chat(
                    model=self.ollama_model,
                    messages=[
                        {
                            'role': 'system',
                            'content': system_prompt
                        },
                        {
                            'role': 'user',
                            'content': user_prompt,
                            'images': [image_data]
                        }
                    ]
                )
            else:
                # Text-only mode (fallback)
                response = ollama.chat(
                    model=self.ollama_model,
                    messages=[
                        {
                            'role': 'system',
                            'content': system_prompt
                        },
                        {
                            'role': 'user',
                            'content': user_prompt
                        }
                    ]
                )
            
            result_text = response['message']['content'].strip()
            
            # Extract JSON from response (handle potential markdown formatting)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            # Validate all required categories are present
            required_categories = ["client_painpoint", "client_type", "software_type", "software_function", "slide_type"]
            for category in required_categories:
                if category not in result:
                    result[category] = []
            
            return result
            
        except Exception as e:
            print(f"Ollama error: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_basic_tags(content)
    
    def _determine_slide_type(self, slide_number: int, total_slides: int, title: str, text_content: str) -> str:
        """
        Determine the type of slide based on position and content
        """
        title_lower = title.lower()
        content_lower = text_content.lower()
        
        # First slide is always title slide
        if slide_number == 1:
            return "title_slide"
        
        # Last slide is usually closing/thank you
        if slide_number == total_slides:
            return "closing_slide"
        
        # Check for agenda slide
        if "agenda" in title_lower or "outline" in title_lower or "overview" in title_lower:
            return "agenda"
        
        # Default to content slide
        return "content"
    
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
            "software_function": [],
            "slide_type": []
        }
        
        # Simple keyword matching
        painpoint_keywords = {
            "security": "data security",
            "identity": "identity",
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
        
        # IBM Software Products with specific keywords
        software_keywords = {
            "maximo": "Maximo",
            "tririga": "Tririga",
            "verify": "Verify",
            "value360": "Value360",
            "crm": "CRM",
            "analytics": "analytics",
            "automation": "automation",
            "dashboard": "dashboard",
            # Maximo-specific
            "asset": "Maximo",
            "maintenance": "Maximo",
            "mobile": "Maximo",
            "visual inspection": "Maximo",
            # Tririga-specific
            "space management": "Tririga",
            "capital planning": "Tririga",
            "lease": "Tririga",
            # Verify-specific
            "iam": "Verify",
            "authentication": "Verify",
            "identity": "Verify"
        }
        
        function_keywords = {
            "report": "reporting",
            "integrate": "integration",
            "dashboard": "dashboard",
            "analyze": "analysis",
            "monitor": "monitoring",
            # Maximo functions
            "asset management": "asset_management",
            "asset_management": "asset_management",
            "mobile": "mobile",
            "maintenance": "maintenance",
            "visual inspection": "visual_inspection",
            "visual_inspection": "visual_inspection",
            "service": "service",
            # Verify functions
            "iam": "IAM",
            "authentication": "authentication",
            "risk": "risk",
            "delegation": "delegation",
            "consent": "consent",
            "continuous audit": "continuous_audit",
            "continuous_audit": "continuous_audit",
            # Tririga functions
            "space management": "space_management",
            "space_management": "space_management",
            "capital planning": "capital_planning",
            "capital_planning": "capital_planning",
            "lease management": "lease_management",
            "lease_management": "lease_management"
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
        
        # Ensure at least one tag per category (except slide_type which is set separately)
        if not tags["client_painpoint"]:
            tags["client_painpoint"] = ["general"]
        if not tags["client_type"]:
            tags["client_type"] = ["general"]
        if not tags["software_type"]:
            tags["software_type"] = ["general"]
        if not tags["software_function"]:
            tags["software_function"] = ["general"]
        # slide_type is determined by position, not content, so don't add "general"
        
        return tags

# Made with Bob
