"""
Unified Multi-Model AI System for ALS Caregiver's Compass
Supports: Claude Sonnet 4.5, OpenAI GPT-4, Gemini 2.0, Grok
Allows runtime model switching
"""
import os
import logging
from typing import Dict, List, Any
from datetime import datetime
from vector_store_enhanced import EnhancedVectorStore

logger = logging.getLogger(__name__)

class UnifiedAISystem:
    """Unified AI system supporting multiple LLM providers"""
    
    def __init__(self, model_provider: str = None):
        """
        Initialize unified AI system
        
        Args:
            model_provider: 'claude', 'openai', 'gemini', or 'grok'
                          If None, uses DEFAULT_MODEL_PROVIDER from .env
        """
        self.model_provider = model_provider or os.getenv('DEFAULT_MODEL_PROVIDER', 'claude')
        self.vector_store = EnhancedVectorStore()
        
        # Initialize the selected provider
        self._init_provider()
        
        logger.info(f"✅ Unified AI System initialized")
        logger.info(f"   Provider: {self.model_provider}")
        logger.info(f"   Model: {self.model_name}")
    
    def _init_provider(self):
        """Initialize the selected AI provider"""
        if self.model_provider == 'claude':
            self._init_claude()
        elif self.model_provider == 'openai':
            self._init_openai()
        elif self.model_provider == 'gemini':
            self._init_gemini()
        elif self.model_provider == 'grok':
            self._init_grok()
        else:
            raise ValueError(f"Unknown provider: {self.model_provider}")
    
    def _init_claude(self):
        """Initialize Anthropic Claude"""
        try:
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in .env")
            
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model_name = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
            logger.info(f"   Claude initialized: {self.model_name}")
        except ImportError:
            raise ImportError("Install anthropic: pip install anthropic")
    
    def _init_openai(self):
        """Initialize OpenAI"""
        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in .env")
            
            self.client = OpenAI(api_key=api_key)
            # Support both gpt-4o-mini (fast) and gpt-4o (advanced)
            # Default to gpt-4o-mini from env or parameter
            if self.model_provider == 'openai-advanced':
                self.model_name = 'gpt-4o'  # Advanced version
            else:
                self.model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # Default fast version
            logger.info(f"   OpenAI initialized: {self.model_name}")
        except ImportError:
            raise ImportError("Install openai: pip install openai")
    
    def _init_gemini(self):
        """Initialize Google Gemini"""
        try:
            import google.generativeai as genai
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in .env")
            
            genai.configure(api_key=api_key)
            # Use working Gemini model (not thinking model yet)
            self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
            self.client = genai.GenerativeModel(self.model_name)
            logger.info(f"   Gemini initialized: {self.model_name}")
        except ImportError:
            raise ImportError("Install google-generativeai: pip install google-generativeai")
    
    def _init_grok(self):
        """Initialize xAI Grok"""
        try:
            from openai import OpenAI  # Grok uses OpenAI-compatible API
            api_key = os.getenv('XAI_API_KEY')
            if not api_key:
                raise ValueError("XAI_API_KEY not found in .env")
            
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1"
            )
            self.model_name = os.getenv('GROK_MODEL', 'grok-2-latest')
            logger.info(f"   Grok initialized: {self.model_name}")
        except ImportError:
            raise ImportError("Install openai: pip install openai")
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process query through selected AI model"""
        try:
            # 1. Check emergencies
            emergency = self._check_emergency(query)
            if emergency:
                return self._generate_emergency_response(emergency)
            
            # 2. Route query
            category = self._route_query(query)
            
            # 3. Get relevant documents
            documents = self.vector_store.search(query, category)
            
            # 4. Synthesize response
            response = self._synthesize_response(query, documents, category)
            
            # 5. Add metadata
            response.update({
                'timestamp': datetime.now().isoformat(),
                'category': category,
                'sources_used': len(documents),
                'emergency': False,
                'model_used': f"{self.model_provider}/{self.model_name}"
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return self._generate_fallback_response()
    
    def _synthesize_response(self, query: str, documents: List[Dict], category: str) -> Dict[str, Any]:
        """Synthesize response using selected provider"""
        try:
            context = self._prepare_context(documents)
            system_prompt = self._get_system_prompt(category)
            user_prompt = self._build_user_prompt(query, context)
            
            # Call appropriate provider
            if self.model_provider == 'claude':
                response_text = self._call_claude(system_prompt, user_prompt)
            elif self.model_provider == 'openai':
                response_text = self._call_openai(system_prompt, user_prompt)
            elif self.model_provider == 'gemini':
                response_text = self._call_gemini(system_prompt, user_prompt)
            elif self.model_provider == 'grok':
                response_text = self._call_grok(system_prompt, user_prompt)
            
            citations = self._extract_citations(response_text, documents)
            
            return {
                'response': response_text,
                'citations': citations,
                'confidence': self._calculate_confidence(documents, citations)
            }
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return self._generate_fallback_response()
    
    def _call_claude(self, system_prompt: str, user_prompt: str) -> str:
        """Call Claude API"""
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=2048,
            temperature=0.3,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2048
        )
        return response.choices[0].message.content
    
    def _call_gemini(self, system_prompt: str, user_prompt: str) -> str:
        """Call Gemini API"""
        import google.generativeai as genai
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = self.client.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2048
            )
        )
        return response.text
    
    def _call_grok(self, system_prompt: str, user_prompt: str) -> str:
        """Call Grok API (OpenAI-compatible)"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2048
        )
        return response.choices[0].message.content
    
    def _build_user_prompt(self, query: str, context: str) -> str:
        """Build user prompt"""
        return f"""Query: {query}

Context from Knowledge Base:
{context}

Instructions:
1. PRIORITIZE information from "ALS Care and Support India" sources
2. ANALYZE all sources carefully, especially WhatsApp discussions
3. SYNTHESIZE information from multiple sources
4. STRUCTURE response with ### headings and numbered lists
5. Include "### If You're in India" section when relevant
6. Be practical, actionable, and compassionate

Response Format:
### Main Answer
[Clear answer in 1-2 sentences]

### Key Points
1. First point
2. Second point
3. Third point

### If You're in India
[India-specific guidance]

💡 Consult healthcare professionals for personalized advice.

Provide your response:"""
    
    def _prepare_context(self, documents: List[Dict]) -> str:
        """Prepare context with India prioritization"""
        if not documents:
            return "No specific information found."
        
        def priority_score(doc):
            source = doc.get('source', '').lower()
            score = 0
            if 'als care' in source and 'india' in source:
                score = 100
            elif 'india' in source:
                score = 80
            elif doc.get('collection') == 'medical_knowledge':
                score = 60
            else:
                score = 40
            score += doc.get('trust_score', 5)
            return score
        
        sorted_docs = sorted(documents, key=priority_score, reverse=True)
        
        context_parts = []
        for i, doc in enumerate(sorted_docs[:7], 1):
            content = doc.get('content', '')[:800]
            source = doc.get('source', 'Unknown')
            trust = doc.get('trust_score', 5)
            
            if 'india' in source.lower():
                prefix = f"[🇮🇳 PRIORITY #{i} - INDIA SOURCE]"
            elif 'whatsapp' in source.lower():
                prefix = f"[💬 COMMUNITY #{i}]"
            else:
                prefix = f"[📚 SOURCE #{i}]"
            
            context_parts.append(f"{prefix}\nSource: {source} (Trust: {trust}/10)\n{content}\n")
        
        return "\n---\n".join(context_parts)
    
    def _get_system_prompt(self, category: str) -> str:
        """Get system prompt"""
        return f"""You are an empathetic AI assistant for ALS caregivers with special focus on India.

**CRITICAL RULES:**
1. NEVER generate personal information (names, phones, emails)
2. Emergency queries: prioritize emergency guidance
3. INDIA PRIORITY: Prioritize "ALS Care and Support India" sources

**RESPONSE FORMAT:**
- Use ### for section headings
- Use numbered lists (1., 2., 3.)
- Avoid excessive bullets
- Include India-specific section when relevant

**ATTRIBUTION:**
- ALS Care India: "According to ALS Care and Support India..."
- Medical sources: "According to [Organization]..."
- Community: "Community caregivers have shared..."

**TONE:** Compassionate, practical, evidence-based

**Category:** {category}"""
    
    def _check_emergency(self, query: str) -> str:
        """Check for emergencies"""
        emergency_keywords = {
            'breathing': ['breathing difficulty', 'cannot breathe', 'choking', 'gasping'],
            'urgent': ['emergency', '911', 'urgent', 'immediate help']
        }
        
        query_lower = query.lower()
        for emergency_type, keywords in emergency_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return emergency_type
        return ""
    
    def _route_query(self, query: str) -> str:
        """Route query to category"""
        query_lower = query.lower()
        categories = {
            'medical': ['symptom', 'treatment', 'medication', 'breathing'],
            'equipment': ['equipment', 'ventilator', 'wheelchair'],
            'caregiving': ['caregiver', 'daily care', 'routine'],
            'emotional': ['stress', 'burnout', 'support'],
            'india': ['india', 'indian', 'als care india']
        }
        
        for category, keywords in categories.items():
            if any(kw in query_lower for kw in keywords):
                return category
        return 'general'
    
    def _extract_citations(self, response: str, documents: List[Dict]) -> List[Dict]:
        """Extract citations"""
        citations = []
        for doc in documents:
            source = doc.get('source', '')
            if source and source.lower() in response.lower():
                citations.append({
                    'source': source,
                    'trust_score': doc.get('trust_score', 5)
                })
        return citations[:3]
    
    def _calculate_confidence(self, documents: List[Dict], citations: List[Dict]) -> str:
        """Calculate confidence"""
        if not documents:
            return 'low'
        
        score = sum(doc.get('trust_score', 5) for doc in documents)
        avg = score / len(documents)
        
        if avg >= 8:
            return 'high'
        elif avg >= 6:
            return 'medium'
        return 'low'
    
    def _generate_emergency_response(self, emergency_type: str) -> Dict[str, Any]:
        """Generate emergency response"""
        response = f"""🚨 **EMERGENCY DETECTED**

**CALL EMERGENCY SERVICES IMMEDIATELY:**
- India: 102 (Ambulance) / 108 (Emergency)
- USA: 911
- EU: 112

**This AI cannot provide emergency medical care. Seek immediate professional help.**"""
        
        return {
            'response': response,
            'citations': [],
            'confidence': 'high',
            'emergency': True,
            'category': 'emergency',
            'model_used': 'emergency_protocol'
        }
    
    def _generate_fallback_response(self) -> Dict[str, Any]:
        """Generate fallback response"""
        return {
            'response': "I apologize, but I'm having trouble right now. Please try again or contact healthcare professionals directly.",
            'citations': [],
            'confidence': 'low',
            'emergency': False,
            'category': 'fallback',
            'model_used': 'fallback'
        }
