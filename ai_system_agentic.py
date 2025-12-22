"""
Advanced Agentic AI System with Multi-Step Reasoning and Relevance Detection
Supports: Claude, OpenAI, Gemini, Grok
Features: Query analysis, ALS relevance detection, multi-agent review, multi-stage retrieval
"""
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from image_manager import get_image_manager

logger = logging.getLogger(__name__)


# =============================================================================
# RELEVANCE ANALYZER - Detects if query is ALS/MND related
# =============================================================================

class RelevanceAnalyzer:
    """
    Detects if a query is related to ALS/MND caregiving.
    Returns out-of-scope response for unrelated queries.
    """
    
    # Comprehensive ALS/MND keyword categories
    ALS_KEYWORDS = {
        # Disease Terminology
        'disease': [
            'als', 'mnd', 'amyotrophic', 'lateral sclerosis', 'motor neuron',
            'lou gehrig', 'bulbar', 'limb onset', 'progressive muscular atrophy',
            'pals', 'cals', 'umn', 'lmn', 'fvc', 'fasciculation', 'atrophy',
            'neurodegenerative', 'motor neurone', 'kennedy disease'
        ],
        
        # Vital Signs & Monitoring
        'vitals': [
            'spo2', 'oxygen saturation', 'pulse', 'heart rate', 'bp', 'blood pressure',
            'rr', 'respiratory rate', 'temperature', 'fever', 'pulse oximeter',
            'vital signs', 'monitoring', 'abg', 'co2', 'carbon dioxide', 'etco2',
            'saturation', 'vitals', 'heart beat', 'bpm'
        ],
        
        # Respiratory Equipment & Care
        'respiratory': [
            'bipap', 'cpap', 'ventilator', 'oxygen', 'concentrator', 'nebulizer',
            'ambu', 'ambu bag', 'mask', 'nasal cannula', 'avaps', 'ivaps',
            'ipap', 'epap', 'tidal volume', 'respiratory', 'breathing',
            'breathlessness', 'dyspnea', 'gasping', 'choking', 'trilogy',
            'dreamstation', 'resmed', 'philips', 'stellar', 'lumis'
        ],
        
        # Tracheostomy Care
        'tracheostomy': [
            'tracheostomy', 'trach', 'cannula', 'cuff', 'stoma', 'subglottic',
            'inner cannula', 'decannulation', 'speaking valve', 'fenestrated',
            'shiley', 'portex', 'tracheotomy', 'tt tube'
        ],
        
        # Feeding & Nutrition
        'nutrition': [
            'peg', 'peg tube', 'ryles tube', 'ng tube', 'feeding tube', 'gastrostomy',
            'swallowing', 'dysphagia', 'aspiration', 'nutrition', 'weight loss',
            'feeding', 'blended diet', 'ensure', 'protein', 'calorie', 'nasogastric',
            'enteral', 'bolus feeding', 'gravity feeding'
        ],
        
        # Secretion Management
        'secretions': [
            'suction', 'suctioning', 'secretion', 'saliva', 'sialorrhea', 'drooling',
            'mucus', 'phlegm', 'thick secretions', 'foamy saliva', 'mucolytic',
            'mucinac', 'inhalex', 'nebulization', 'cough assist', 'clearance'
        ],
        
        # Equipment & Mobility
        'equipment': [
            'wheelchair', 'hospital bed', 'fowler bed', 'recliner', 'air mattress',
            'bedsore', 'pressure sore', 'hoyer lift', 'patient lift', 'commode',
            'bedridden', 'bed-bound', 'immobile', 'positioning', 'transfer board',
            'slide sheet', 'sling', 'turning', 'egg crate mattress'
        ],
        
        # Power Backup (Critical for Ventilator Patients)
        'power': [
            'ups', 'inverter', 'generator', 'battery backup', 'power cut',
            'electricity', 'power failure', 'kva', 'backup power', 'power outage',
            'battery', 'tubular battery', 'sine wave'
        ],
        
        # Daily Care & Symptoms
        'care': [
            'caregiver', 'caregiving', 'nursing', 'home care', 'home icu',
            'daily routine', 'positioning', 'turning', 'range of motion', 'rom',
            'physiotherapy', 'exercise', 'massage', 'pain', 'discomfort',
            'cramps', 'spasticity', 'stiffness', 'insomnia', 'sleep',
            'fatigue', 'weakness', 'muscle', 'atrophy'
        ],
        
        # Medical Complications
        'medical': [
            'pneumonia', 'infection', 'uti', 'constipation', 'edema', 'swelling',
            'fever', 'tlc', 'cbc', 'antibiotic', 'chest infection',
            'aspiration pneumonia', 'dehydration', 'bedsore', 'pressure ulcer',
            'dvt', 'blood clot', 'sepsis'
        ],
        
        # Medications
        'medications': [
            'riluzole', 'rilutor', 'radicava', 'edaravone', 'nuedexta',
            'baclofen', 'tizanidine', 'glycopyrrolate', 'atropine',
            'botox', 'injection', 'medicine', 'medication', 'dosage',
            'levolin', 'foracort', 'budecort', 'asthalin', 'duolin',
            'emeset', 'ondansetron', 'lactulose', 'cremaffin'
        ],
        
        # Communication
        'communication': [
            'speech', 'speaking', 'dysarthria', 'aac', 'eye tracker', 'tobii',
            'communication board', 'voice banking', 'text to speech',
            'eye gaze', 'grid pad', 'letter board'
        ],
        
        # Emotional & Support
        'emotional': [
            'burnout', 'stress', 'depression', 'anxiety', 'coping', 'support',
            'counseling', 'mental health', 'caregiver fatigue', 'grief',
            'emotional', 'psychological', 'wellbeing', 'self care'
        ],
        
        # Emergency
        'emergency': [
            'emergency', 'crisis', 'urgent', '911', '102', '108',
            'dropping', 'falling', 'unconscious', 'not responding',
            'choking', 'cannot breathe', 'blue lips', 'cyanosis'
        ],
        
        # India-specific terms
        'india': [
            'india', 'indian', 'delhi', 'mumbai', 'bangalore', 'kolkata',
            'chennai', 'hyderabad', 'pune', 'nimhans', 'aiims', '₹', 'rupees',
            'lakh', 'crore', 'als care india', 'alscas'
        ]
    }
    
    # Relevance threshold (0.5 = at least one keyword match is sufficient)
    RELEVANCE_THRESHOLD = 0.5
    
    # Common question patterns in ALS community (to help catch natural questions)
    QUESTION_PATTERNS = [
        'when to', 'right time', 'which machine', 'which bipap', 'what to feed',
        'how to manage', 'how to do', 'when should', 'is it time', 'when does',
        'how much', 'where to buy', 'which brand', 'best machine', 'costs',
        'nurse charges', 'attendant cost', 'how to prepare', 'what equipment'
    ]
    # Common misspellings in ALS community (caregivers type quickly!)
    COMMON_MISSPELLINGS = {
        'trahceostomy': 'tracheostomy',
        'tracostomy': 'tracheostomy',
        'trachestomy': 'tracheostomy',
        'tracheotomy': 'tracheostomy',
        'trachea': 'tracheostomy',
        'biaap': 'bipap',
        'biapap': 'bipap',
        'bi-pap': 'bipap',
        'cpap': 'bipap',
        'peg tube': 'peg',
        'feeding tube': 'peg',
        'ryle': 'ryles',
        'ryels': 'ryles',
        'ng tube': 'ryles',
        'suction': 'suctioning',
        'nebuliser': 'nebulizer',
        'ventilater': 'ventilator',
        'oximeter': 'pulse oximeter',
        'oxigen': 'oxygen',
        'constipaton': 'constipation',
        'bedsore': 'bedsores',
        'bed sore': 'bedsores',
    }
    
    def __init__(self):
        # Flatten all keywords for quick lookup
        self.all_keywords = set()
        for category_keywords in self.ALS_KEYWORDS.values():
            self.all_keywords.update(kw.lower() for kw in category_keywords)
    
    def is_als_relevant(self, query: str) -> Tuple[bool, float, List[str]]:
        """
        Check if query is ALS/MND related.
        Enhanced with fuzzy matching for common misspellings.
        
        Returns:
            Tuple of (is_relevant, confidence_score, matched_keywords)
        """
        query_lower = query.lower()
        matched_keywords = []
        category_matches = {}
        
        # First, fix common misspellings in the query
        corrected_query = query_lower
        for misspelling, correction in self.COMMON_MISSPELLINGS.items():
            if misspelling in corrected_query:
                corrected_query = corrected_query.replace(misspelling, correction)
                matched_keywords.append(f"{misspelling}→{correction}")
        
        # Check each category for keywords
        for category, keywords in self.ALS_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in corrected_query:
                    matched_keywords.append(keyword)
                    category_matches[category] = category_matches.get(category, 0) + 1
        
        # Also check question patterns (common ALS caregiver questions)
        for pattern in self.QUESTION_PATTERNS:
            if pattern in query_lower:
                # Give partial credit for question patterns
                category_matches['question_pattern'] = 0.5
                break
        
        # Calculate relevance score
        # - Each keyword match = 1 point
        # - Multiple categories = bonus 0.5 per additional category
        base_score = len([k for k in matched_keywords if '→' not in k])
        # Misspelling matches also count
        misspelling_bonus = len([k for k in matched_keywords if '→' in k]) * 0.8
        category_bonus = max(0, (len(category_matches) - 1) * 0.5)
        relevance_score = base_score + misspelling_bonus + category_bonus
        
        # Determine if relevant
        is_relevant = relevance_score >= self.RELEVANCE_THRESHOLD
        
        logger.info(f"Relevance check: score={relevance_score:.1f}, relevant={is_relevant}, keywords={matched_keywords[:5]}")
        
        return (is_relevant, relevance_score, matched_keywords)
    
    def get_out_of_scope_response(self, query: str) -> Dict[str, Any]:
        """
        Generate a friendly out-of-scope response for non-ALS queries.
        """
        return {
            'response': """### I Specialize in ALS/MND Caregiving 🩺

I'm an AI assistant specifically designed to help with **ALS (Amyotrophic Lateral Sclerosis)** and **MND (Motor Neuron Disease)** caregiving.

Your question doesn't seem to be related to ALS/MND topics. I'm not able to answer general questions outside my area of expertise.

**I can help you with:**
- 🫁 Respiratory care (BiPAP, ventilators, oxygen)
- 🍽️ Feeding and nutrition (PEG tubes, Ryles tubes)
- 🏥 Home ICU setup and equipment
- 💊 Medications and symptom management
- 👨‍⚕️ Daily caregiving routines
- 🚨 Emergency protocols
- 💰 Costs and resources in India

**Please feel free to ask me anything about ALS/MND caregiving!**

💡 *If you believe your question IS related to ALS care, try rephrasing it with specific terms like "PALS", "caregiver", "BiPAP", "ventilator", etc.*""",
            'citations': [],
            'confidence': 'not_applicable',
            'out_of_scope': True,
            'timestamp': datetime.now().isoformat(),
            'query_type': 'out_of_scope',
            'sources_used': 0,
            'emergency': False,
            'model_used': 'relevance_filter',
            'images': []  # No images for out-of-scope queries
        }


# =============================================================================
# MULTI-AGENT SYSTEM - Dedicated agents for each source type
# =============================================================================

class WhatsAppAgent:
    """
    Agent for WhatsApp Community content.
    Retrieves and synthesizes practical solutions from caregiver discussions.
    """
    
    SOURCE_LABEL = "💬 WhatsApp Community Discussion"
    SOURCE_PRIORITY = 1  # Highest priority
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    def retrieve(self, query: str, plan, max_docs: int = 5) -> List[Dict]:
        """Retrieve relevant WhatsApp community content"""
        try:
            # Use hybrid_search with India priority (WhatsApp is India-focused)
            all_docs = self.vector_store.hybrid_search(
                query=query,
                category='india',  # Prioritize community collections
                india_priority=True,
                emergency_mode=getattr(plan, 'emergency_mode', False),
                n_results=max_docs * 2  # Get more then filter
            )
            
            # Filter for WhatsApp sources only
            whatsapp_docs = []
            for doc in all_docs:
                source = doc.get('source', '').lower()
                collection = doc.get('collection', '').lower()
                
                # Check if it's from WhatsApp/community sources
                if ('whatsapp' in source or 
                    'community' in collection or 
                    'als care' in source and 'india' in source):
                    whatsapp_docs.append(doc)
            
            logger.info(f"WhatsAppAgent: Found {len(whatsapp_docs)} community docs from {len(all_docs)} total")
            return whatsapp_docs[:max_docs]
            
        except Exception as e:
            logger.error(f"WhatsAppAgent retrieval error: {e}")
            return []
    
    def format_for_prompt(self, docs: List[Dict]) -> str:
        """Format WhatsApp content for LLM prompt"""
        if not docs:
            return ""
        
        sections = [
            "\n" + "=" * 60,
            f"🥇 {self.SOURCE_LABEL} (HIGHEST PRIORITY)",
            "Real experiences from 650+ Indian ALS caregiving families",
            "=" * 60
        ]
        
        for i, doc in enumerate(docs, 1):
            chunk_type = doc.get('chunk_type', 'discussion')
            source = doc.get('source', 'Community')
            symptoms = doc.get('symptoms', '')
            
            sections.append(f"\n[COMMUNITY INSIGHT #{i}]")
            sections.append(f"Source: {source}")
            if chunk_type == 'qa_pair':
                sections.append("⭐ This is a Q&A Solution from the community")
            if symptoms and symptoms != '[]':
                sections.append(f"Related to: {symptoms}")
            
            content = doc.get('content', '')[:800]
            sections.append(content)
            sections.append("-" * 40)
        
        return "\n".join(sections)


class ALSCASAgent:
    """
    Agent for ALS Care And Support India website content.
    Retrieves structured guidance from ALSCAS.
    """
    
    SOURCE_LABEL = "🇮🇳 ALS Care & Support India"
    SOURCE_PRIORITY = 2
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    def retrieve(self, query: str, plan, max_docs: int = 4) -> List[Dict]:
        """Retrieve ALSCAS website content (non-WhatsApp India sources)"""
        try:
            # Get India-specific content
            all_docs = self.vector_store.hybrid_search(
                query=query,
                india_priority=True,
                n_results=max_docs * 2
            )
            
            # Filter for ALSCAS (non-WhatsApp India sources)
            alscas_docs = []
            for doc in all_docs:
                source = doc.get('source', '').lower()
                is_india = doc.get('india_specific', False)
                
                # ALSCAS = India sources that are NOT WhatsApp
                if is_india and 'whatsapp' not in source:
                    alscas_docs.append(doc)
            
            logger.info(f"ALSCASAgent: Found {len(alscas_docs)} ALSCAS docs")
            return alscas_docs[:max_docs]
            
        except Exception as e:
            logger.error(f"ALSCASAgent retrieval error: {e}")
            return []
    
    def format_for_prompt(self, docs: List[Dict]) -> str:
        """Format ALSCAS content for LLM prompt"""
        if not docs:
            return ""
        
        sections = [
            "\n" + "=" * 60,
            f"🥈 {self.SOURCE_LABEL}",
            "Structured guidance from Indian ALS support organization",
            "=" * 60
        ]
        
        for i, doc in enumerate(docs, 1):
            source = doc.get('source', 'ALSCAS')
            sections.append(f"\n[ALSCAS GUIDANCE #{i}]")
            sections.append(f"Source: {source}")
            content = doc.get('content', '')[:700]
            sections.append(content)
            sections.append("-" * 40)
        
        return "\n".join(sections)


class MedicalSourcesAgent:
    """
    Agent for medical authority sources.
    Retrieves evidence-based medical guidance.
    """
    
    SOURCE_LABEL = "📚 Medical Authority Sources"
    SOURCE_PRIORITY = 3
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    def retrieve(self, query: str, plan, max_docs: int = 3) -> List[Dict]:
        """Retrieve medical authority content"""
        try:
            # Search with medical category priority
            all_docs = self.vector_store.hybrid_search(
                query=query,
                category='medical',
                india_priority=False,  # Global medical sources
                n_results=max_docs * 2
            )
            
            # Filter for medical sources (not community)
            medical_docs = []
            for doc in all_docs:
                collection = doc.get('collection', '').lower()
                source = doc.get('source', '').lower()
                
                # Medical = from medical collections or medical-sounding sources
                if ('medical' in collection or 
                    any(term in source for term in ['mayo', 'nih', 'mnd assoc', 'als assoc', 'clinic', 'hospital'])):
                    medical_docs.append(doc)
            
            logger.info(f"MedicalAgent: Found {len(medical_docs)} medical docs")
            return medical_docs[:max_docs]
            
        except Exception as e:
            logger.error(f"MedicalSourcesAgent retrieval error: {e}")
            return []
    
    def format_for_prompt(self, docs: List[Dict]) -> str:
        """Format medical content for LLM prompt"""
        if not docs:
            return ""
        
        sections = [
            "\n" + "=" * 60,
            f"🥉 {self.SOURCE_LABEL}",
            "Evidence-based medical guidance from trusted organizations",
            "=" * 60
        ]
        
        for i, doc in enumerate(docs, 1):
            source = doc.get('source', 'Medical Source')
            sections.append(f"\n[MEDICAL SOURCE #{i}]: {source}")
            content = doc.get('content', '')[:600]
            sections.append(content)
            sections.append("-" * 40)
        
        return "\n".join(sections)


# =============================================================================
# QUERY PLAN - Data structure for query execution
# =============================================================================

@dataclass
class QueryPlan:
    """Query execution plan with relevance tracking"""
    query_type: str  # 'simple', 'complex', 'emergency', 'comparison', 'out_of_scope'
    categories: List[str]  # Relevant categories
    search_strategy: str  # 'focused', 'broad', 'multi-stage'
    india_priority: bool
    emergency_mode: bool
    needs_cost_info: bool
    needs_technical_details: bool
    requires_multi_source: bool
    # New relevance fields
    is_als_relevant: bool = True
    relevance_score: float = 0.0
    relevance_keywords: List[str] = field(default_factory=list)


class QueryAnalyzer:
    """Intelligent query analysis and planning"""
    
    def __init__(self):
        self.emergency_keywords = [
            'emergency', 'urgent', 'immediate', 'cannot breathe', 'choking',
            'spo2 drop', 'crisis', 'gasping', 'blue lips', 'unconscious',
            'spo2', 'oxygen dropping', 'not breathing'
        ]
        
        self.cost_keywords = [
            'cost', 'price', 'expensive', 'affordable', '₹', 'rupees',
            'budget', 'cheap', 'how much', 'lakh', 'thousand'
        ]
        
        self.comparison_keywords = [
            'vs', 'versus', 'compare', 'difference between', 'which is better',
            'or', 'better option', 'choose between'
        ]
        
        self.technical_keywords = [
            'how to', 'procedure', 'steps', 'protocol', 'settings',
            'dosage', 'frequency', 'technical', 'setup'
        ]
        
        self.category_patterns = {
            'breathing': ['breath', 'bipap', 'ventilator', 'oxygen', 'spo2', 'respiratory', 'cpap'],
            'feeding': ['peg', 'ryles', 'feed', 'swallow', 'nutrition', 'tube', 'eating'],
            'secretions': ['saliva', 'secretion', 'mucus', 'suction', 'phlegm', 'foamy', 'drooling'],
            'tracheostomy': ['trach', 'cannula', 'stoma', 'cuff', 'tracheostomy'],
            'equipment': ['machine', 'device', 'equipment', 'purchase', 'buy', 'rent'],
            'medication': ['medicine', 'drug', 'dose', 'prescription', 'medication', 'tablet'],
            'caregiving': ['caregiver', 'care', 'routine', 'daily', 'schedule', 'help'],
            'mobility': ['walk', 'wheelchair', 'movement', 'physiotherapy', 'exercise'],
            'communication': ['speak', 'communication', 'aac', 'voice', 'talk'],
            'emotional': ['stress', 'burnout', 'depression', 'support', 'cope', 'mental']
        }
    
    def analyze_query(self, query: str) -> QueryPlan:
        """Analyze query and create execution plan"""
        query_lower = query.lower()
        
        # Detect emergency
        emergency_mode = any(kw in query_lower for kw in self.emergency_keywords)
        
        # Detect India priority
        india_priority = any(term in query_lower for term in [
            'india', 'indian', 'delhi', 'mumbai', 'bangalore', '₹', 'rupees'
        ])
        
        # Detect cost inquiry
        needs_cost_info = any(kw in query_lower for kw in self.cost_keywords)
        
        # Detect comparison
        is_comparison = any(kw in query_lower for kw in self.comparison_keywords)
        
        # Detect technical details needed
        needs_technical = any(kw in query_lower for kw in self.technical_keywords)
        
        # Detect categories
        categories = []
        for category, patterns in self.category_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                categories.append(category)
        
        # Determine query type
        if emergency_mode:
            query_type = 'emergency'
        elif is_comparison:
            query_type = 'comparison'
        elif len(categories) > 2 or ('?' in query and len(query.split()) > 15):
            query_type = 'complex'
        else:
            query_type = 'simple'
        
        # Determine search strategy
        if emergency_mode:
            search_strategy = 'focused'
        elif is_comparison or len(categories) > 2:
            search_strategy = 'multi-stage'
        else:
            search_strategy = 'broad'
        
        # Requires multi-source?
        requires_multi_source = is_comparison or query_type == 'complex'
        
        return QueryPlan(
            query_type=query_type,
            categories=categories or ['general'],
            search_strategy=search_strategy,
            india_priority=india_priority,
            emergency_mode=emergency_mode,
            needs_cost_info=needs_cost_info,
            needs_technical_details=needs_technical,
            requires_multi_source=requires_multi_source
        )


class AgenticAISystem:
    """Advanced agentic AI system with multi-agent architecture"""
    
    def __init__(self, model_provider: str = None):
        self.model_provider = model_provider or os.getenv('DEFAULT_MODEL_PROVIDER', 'openai')
        
        # Import enhanced vector store
        from vector_store_enhanced import EnhancedVectorStore
        self.vector_store = EnhancedVectorStore()
        self.query_analyzer = QueryAnalyzer()
        self.relevance_analyzer = RelevanceAnalyzer()  # For topic gating
        
        # Initialize 3 dedicated source agents
        self.whatsapp_agent = WhatsAppAgent(self.vector_store)
        self.alscas_agent = ALSCASAgent(self.vector_store)
        self.medical_agent = MedicalSourcesAgent(self.vector_store)
        
        # Initialize image manager
        try:
            self.image_manager = get_image_manager()
            logger.info(f"   Image Manager initialized")
        except Exception as e:
            logger.warning(f"Image manager initialization failed: {e}")
            self.image_manager = None
        
        # Initialize provider
        self._init_provider()
        
        logger.info("✅ Multi-Agent AI System initialized")
        logger.info(f"   Provider: {self.model_provider}")
        logger.info(f"   Model: {self.model_name}")
        logger.info(f"   Agents: WhatsApp 🥇 | ALSCAS 🥈 | Medical 🥉")
    
    def _init_provider(self):
        """Initialize AI provider"""
        # Handle OpenAI variants
        if self.model_provider in ['openai', 'openai-advanced', 'openai-gpt4o', 'openai-o1-mini', 'openai-o1']:
            self._init_openai()
        elif self.model_provider == 'claude':
            self._init_claude()
        elif self.model_provider in ['gemini', 'gemini-thinking']:
            self._init_gemini()
        elif self.model_provider == 'grok':
            self._init_grok()
        else:
            raise ValueError(f"Unknown provider: {self.model_provider}")
    
    def _init_claude(self):
        """Initialize Claude"""
        try:
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model_name = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
        except ImportError:
            raise ImportError("Install: pip install anthropic")
    
    def _init_openai(self):
        """Initialize OpenAI with model selection based on provider"""
        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found")
            self.client = OpenAI(api_key=api_key)
            
            # Select model based on provider string
            model_map = {
                'openai': 'gpt-4o-mini',           # Default - fast & affordable
                'openai-gpt4o': 'gpt-4o',          # Advanced - more capable
                'openai-o1-mini': 'o1-mini',       # Reasoning - smarter
                'openai-o1': 'o1'                  # Best reasoning - deep analysis
            }
            self.model_name = model_map.get(self.model_provider, 'gpt-4o-mini')
            self.is_reasoning_model = self.model_provider in ['openai-o1-mini', 'openai-o1']
            
        except ImportError:
            raise ImportError("Install: pip install openai")
    
    def _init_gemini(self):
        """Initialize Gemini"""
        try:
            import google.generativeai as genai
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found")
            genai.configure(api_key=api_key)
            
            # Handle thinking mode variant
            if self.model_provider == 'gemini-thinking':
                self.model_name = 'gemini-2.0-flash-thinking-exp-01-21'
            else:
                self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
            
            self.client = genai.GenerativeModel(self.model_name)
        except ImportError:
            raise ImportError("Install: pip install google-generativeai")
    
    def _init_grok(self):
        """Initialize Grok"""
        try:
            from openai import OpenAI
            api_key = os.getenv('XAI_API_KEY')
            if not api_key:
                raise ValueError("XAI_API_KEY not found")
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1"
            )
            self.model_name = os.getenv('GROK_MODEL', 'grok-2-latest')
        except ImportError:
            raise ImportError("Install: pip install openai")
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Main agentic processing pipeline with multi-agent retrieval"""
        try:
            # Step 0: CHECK RELEVANCE FIRST (Topic Gating)
            is_relevant, relevance_score, matched_keywords = self.relevance_analyzer.is_als_relevant(query)
            
            if not is_relevant:
                logger.info(f"❌ Query not ALS-relevant (score={relevance_score:.1f}): {query[:50]}...")
                return self.relevance_analyzer.get_out_of_scope_response(query)
            
            logger.info(f"✅ Query is ALS-relevant (score={relevance_score:.1f}): {matched_keywords[:5]}")
            
            # Step 1: Analyze and plan (with relevance info)
            plan = self.query_analyzer.analyze_query(query)
            plan.is_als_relevant = is_relevant
            plan.relevance_score = relevance_score
            plan.relevance_keywords = matched_keywords
            
            logger.info(f"Query Plan: {plan.query_type}, Categories: {plan.categories}")
            
            # Step 2: Handle emergency immediately
            if plan.emergency_mode:
                return self._handle_emergency(query, plan)
            
            # Step 3: Execute MULTI-AGENT retrieval (3 agents)
            agent_results = self._execute_multi_agent_retrieval(query, plan)
            
            # Also get documents via traditional method for backward compatibility
            documents = agent_results['all_docs']
            
            # Step 4: Synthesize response using multi-agent context
            multi_agent_context = self._prepare_multi_agent_context(agent_results, plan)
            response = self._synthesize_with_multi_agent(query, multi_agent_context, agent_results, plan)
            
            # Step 4.5: Suggest relevant images
            images = []
            if self.image_manager and plan.is_als_relevant:
                try:
                    images = self.image_manager.suggest_images(
                        query, 
                        multi_agent_context[:500], 
                        max_images=3,
                        als_relevant=True
                    )
                    if images:
                        logger.info(f"✅ Selected {len(images)} images for query: {query[:50]}...")
                except Exception as e:
                    logger.error(f"❌ Error suggesting images: {e}")
            
            # Step 5: Add comprehensive metadata
            response.update({
                'timestamp': datetime.now().isoformat(),
                'query_type': plan.query_type,
                'categories': plan.categories,
                'sources_used': agent_results['total_count'],
                'source_breakdown': {
                    'whatsapp': agent_results['whatsapp']['count'],
                    'alscas': agent_results['alscas']['count'],
                    'medical': agent_results['medical']['count']
                },
                'emergency': False,
                'model_used': f"{self.model_provider}/{self.model_name}",
                'india_prioritized': plan.india_priority,
                'search_strategy': 'multi_agent',
                'images': images,
                'relevance_score': relevance_score,
                'relevance_keywords': matched_keywords[:10]
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return self._generate_fallback_response(str(e))
    
    def _execute_retrieval(self, query: str, plan: QueryPlan) -> List[Dict]:
        """Execute intelligent retrieval based on plan"""
        if plan.search_strategy == 'focused':
            # Single focused search for emergencies
            documents = self.vector_store.hybrid_search(
                query=query,
                category=plan.categories[0] if plan.categories else None,
                india_priority=plan.india_priority,
                emergency_mode=plan.emergency_mode,
                n_results=15
            )
            
        elif plan.search_strategy == 'multi-stage':
            # Multi-stage retrieval for complex/comparison queries
            documents = []
            
            # Stage 1: Primary categories
            if plan.categories:
                for category in plan.categories[:2]:
                    results = self.vector_store.hybrid_search(
                        query=query,
                        category=category,
                        india_priority=plan.india_priority,
                        n_results=8
                    )
                    documents.extend(results)
            
            # Stage 2: Cost information if needed
            if plan.needs_cost_info:
                cost_results = self.vector_store.hybrid_search(
                    query=f"{query} cost price india",
                    india_priority=True,
                    n_results=5
                )
                documents.extend(cost_results)
            
            # Remove duplicates
            seen_ids = set()
            unique_docs = []
            for doc in documents:
                doc_id = doc.get('content', '')[:100]
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    unique_docs.append(doc)
            documents = unique_docs
            
        else:
            # Broad search for general queries
            documents = self.vector_store.hybrid_search(
                query=query,
                category=plan.categories[0] if plan.categories else None,
                india_priority=plan.india_priority,
                n_results=12
            )
        
        logger.info(f"Retrieved {len(documents)} documents")
        return documents
    
    def _execute_multi_agent_retrieval(self, query: str, plan: QueryPlan) -> Dict[str, Any]:
        """
        Execute retrieval using 3 dedicated agents.
        Returns structured results from each source with explicit attribution.
        """
        logger.info("🤖 Running Multi-Agent Retrieval...")
        
        # Agent 1: WhatsApp Community (HIGHEST PRIORITY)
        logger.info("   🥇 WhatsApp Agent retrieving community content...")
        whatsapp_docs = self.whatsapp_agent.retrieve(query, plan, max_docs=5)
        whatsapp_context = self.whatsapp_agent.format_for_prompt(whatsapp_docs)
        logger.info(f"      Found {len(whatsapp_docs)} WhatsApp discussions")
        
        # Agent 2: ALSCAS Website
        logger.info("   🥈 ALSCAS Agent retrieving website content...")
        alscas_docs = self.alscas_agent.retrieve(query, plan, max_docs=4)
        alscas_context = self.alscas_agent.format_for_prompt(alscas_docs)
        logger.info(f"      Found {len(alscas_docs)} ALSCAS documents")
        
        # Agent 3: Medical Sources
        logger.info("   🥉 Medical Agent retrieving authority content...")
        medical_docs = self.medical_agent.retrieve(query, plan, max_docs=3)
        medical_context = self.medical_agent.format_for_prompt(medical_docs)
        logger.info(f"      Found {len(medical_docs)} medical sources")
        
        # Combine all documents for metadata
        all_docs = whatsapp_docs + alscas_docs + medical_docs
        
        return {
            'whatsapp': {
                'docs': whatsapp_docs,
                'context': whatsapp_context,
                'count': len(whatsapp_docs),
                'label': self.whatsapp_agent.SOURCE_LABEL
            },
            'alscas': {
                'docs': alscas_docs,
                'context': alscas_context,
                'count': len(alscas_docs),
                'label': self.alscas_agent.SOURCE_LABEL
            },
            'medical': {
                'docs': medical_docs,
                'context': medical_context,
                'count': len(medical_docs),
                'label': self.medical_agent.SOURCE_LABEL
            },
            'all_docs': all_docs,
            'total_count': len(all_docs)
        }
    
    def _prepare_multi_agent_context(self, agent_results: Dict[str, Any], plan: QueryPlan) -> str:
        """
        Prepare context from multi-agent retrieval with clear source sections.
        """
        sections = []
        
        # Header
        sections.append("=" * 70)
        sections.append("KNOWLEDGE BASE CONTEXT (Multi-Agent Retrieval)")
        sections.append("Sources prioritized: WhatsApp 🥇 > ALSCAS 🥈 > Medical 🥉")
        sections.append("=" * 70)
        
        # WhatsApp Section (HIGHEST PRIORITY)
        if agent_results['whatsapp']['context']:
            sections.append(agent_results['whatsapp']['context'])
        else:
            sections.append("\n[No WhatsApp community discussions found for this topic]")
        
        # ALSCAS Section
        if agent_results['alscas']['context']:
            sections.append(agent_results['alscas']['context'])
        else:
            sections.append("\n[No ALSCAS website content found for this topic]")
        
        # Medical Section
        if agent_results['medical']['context']:
            sections.append(agent_results['medical']['context'])
        else:
            sections.append("\n[No medical authority sources found for this topic]")
        
        # Footer with instructions
        sections.append("\n" + "=" * 70)
        sections.append("RESPONSE FORMAT INSTRUCTIONS:")
        sections.append("Your response MUST have these 3 sections with explicit source labels:")
        sections.append("1. 💬 From WhatsApp Community - [community experiences]")
        sections.append("2. 🇮🇳 From ALS Care India - [structured guidance]")
        sections.append("3. 📚 From Medical Sources - [evidence-based info]")
        sections.append("4. ✅ Combined Recommendation - [synthesized answer]")
        sections.append("=" * 70)
        
        return "\n".join(sections)

    def _synthesize_with_multi_agent(
        self,
        query: str,
        multi_agent_context: str,
        agent_results: Dict[str, Any],
        plan: QueryPlan
    ) -> Dict[str, Any]:
        """Synthesize response using multi-agent context with explicit source sections"""
        
        # Build system prompt for multi-agent response
        system_prompt = self._get_multi_agent_system_prompt(plan, agent_results)
        
        # Build user prompt with multi-agent context
        user_prompt = self._build_multi_agent_user_prompt(query, multi_agent_context, plan)
        
        # Call LLM
        try:
            if self.model_provider == 'claude':
                response_text = self._call_claude(system_prompt, user_prompt)
            elif self.model_provider in ['openai', 'openai-advanced', 'openai-gpt4o', 'openai-o1-mini', 'openai-o1']:
                response_text = self._call_openai(system_prompt, user_prompt)
            elif self.model_provider in ['gemini', 'gemini-thinking']:
                response_text = self._call_gemini(system_prompt, user_prompt)
            elif self.model_provider == 'grok':
                response_text = self._call_grok(system_prompt, user_prompt)
            else:
                response_text = self._call_openai(system_prompt, user_prompt)
            
            # Calculate confidence based on source coverage
            has_whatsapp = agent_results['whatsapp']['count'] > 0
            has_alscas = agent_results['alscas']['count'] > 0
            has_medical = agent_results['medical']['count'] > 0
            
            source_coverage = sum([has_whatsapp, has_alscas, has_medical])
            if source_coverage >= 2:
                confidence = 'high'
            elif source_coverage == 1:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            return {
                'response': response_text,
                'citations': [],  # TODO: Extract citations from response
                'confidence': confidence,
                'source_coverage': {
                    'whatsapp': has_whatsapp,
                    'alscas': has_alscas,
                    'medical': has_medical
                }
            }
            
        except Exception as e:
            logger.error(f"Multi-agent synthesis error: {e}")
            return self._generate_fallback_response(str(e))
    
    def _get_multi_agent_system_prompt(self, plan: QueryPlan, agent_results: Dict[str, Any]) -> str:
        """System prompt for multi-agent response generation with flowchart-based answers"""
        prompt = """You are an AI assistant SPECIALIZED in ALS/MND caregiving for Indian families.
You provide answers in a FLOWCHART/DECISION-TREE style, helping caregivers understand "IF this situation, THEN do that."

**CRITICAL RESPONSE FORMAT:**
Your response MUST have these 5 sections. Use the EXACT section headers with emojis:

### 💬 From WhatsApp Community (650+ Indian ALS Families)
[MANDATORY: State clearly that this is from real experiences shared in the ALS Care & Support India WhatsApp community]
[Include practical solutions, costs in ₹, stories, and hindsight perspectives]
[Example opening: "Based on discussions among 650+ Indian ALS caregiving families in the WhatsApp community..."]
[If no WhatsApp content available, write: "No specific community discussions found for this topic in the WhatsApp archive."]

### 🇮🇳 From ALS Care & Support India (ALSCAS)
[Structured guidance from ALSCAS website - alslifemanagement.weebly.com]
[If no ALSCAS content available, write: "No specific ALSCAS website guidance found for this topic."]

### 📚 From Medical Sources
[Evidence-based medical guidance from trusted organizations]
[If no medical content available, write: "No specific medical authority guidance found for this topic."]

### 🔀 Decision Matrix (IF → THEN)
[CRITICAL: Use this flowchart format for situational guidance]

**IF** [condition/situation] **→ THEN** [action to take]
**ELSE IF** [alternative condition] **→ THEN** [alternative action]
**OTHERWISE** → [default action]

Examples:
• **IF** SpO₂ is 96%+ BUT morning headaches present **→ THEN** Start BiPAP immediately (CO₂ retention likely)
• **IF** PALS takes >45 min per meal OR choking frequently **→ THEN** Discuss feeding tube with doctor NOW
• **IF** on BiPAP 24x7 + frequent infections **→ THEN** Plan tracheostomy proactively (don't wait for emergency)

### ✅ Stage-Based Recommendation (Ready Reckoner)
[Map the user's situation to the appropriate ALS journey stage]

**ALS JOURNEY STAGES (from ALSCAS Ready Reckoner):**
1. **Just Diagnosed** → Confirm with 3-4 neurologists, join support group, focus on nutrition
2. **Mobility Issues** → Prevent falls, use walker/wheelchair, consider airbed early
3. **Breathing Concern** → THIS IS YOUR TIME TO ACT: Get BiPAP before SpO₂ drops, never use plain oxygen alone
4. **Nutrition Issues** → If taking 30+ min to eat, consider feeding tube EARLY
5. **Speech/Swallowing** → Voice banking NOW while speech is clear, use eye trackers
6. **Assistive Breathing** → Increase BiPAP gradually, plan tracheostomy if BiPAP becomes 24x7
7. **Home ICU Setup** → Backups for ALL devices, trained caregivers, emergency protocols
8. **Advanced Care** → Daily procedures: oral suction 80-120x/day, trach suction 2-12x/day
9. **Caregiver Breaks** → MANDATORY breaks to prevent burnout, have backup caregivers

[Based on user's situation, recommend which stage they're at and what actions to take NOW]

**HINDSIGHT WISDOM - THE HARD LESSON:**
[Include quotes showing what experienced caregivers wish they had known]
- "We were too hopeful to be practical"
- "Early BiPAP ≠ giving up, it = muscle preservation"
- "ALS progression punishes delay, not preparedness"
- "Support early, not in crisis"

**CRITICAL SOURCE ATTRIBUTION RULES:**
1. **WhatsApp Content = HIGHEST VALUE** - Real stories from caregivers who lived through it
2. ALWAYS explicitly state: "According to WhatsApp community discussions..." or "Community members shared..."
3. Emphasize the practical/hindsight nature of community wisdom
4. For costs, cite WhatsApp community: "Community members report costs of ₹..."
5. NEVER present WhatsApp content as if it came from medical sources

**FLOWCHART PHRASING STYLE (from ALSCAS):**
- Use "THIS IS YOUR TIME TO ACT" for urgent situations
- Use "Your motto should be..." for guiding principles
- Use "The less fatigue we give to the body, the better we are dealing with ALS"
- Frame BiPAP as "gym rest for the diaphragm" - preserves muscle strength
- Emphasize: "In ALS, using support DOES NOT make you dependent - it's the REVERSE"

**OTHER IMPORTANT RULES:**
1. ONLY use information from the provided KNOWLEDGE BASE CONTEXT
2. Do NOT generate information from general knowledge
3. Always use ₹ for costs when discussing India
4. Be compassionate and practical
5. Acknowledge emotional challenges caregivers face

**TONE:** Compassionate, action-oriented, with urgency where appropriate. Voice of "we understand what you're going through - here's what works" """

        # Add source availability info
        prompt += f"\n\n**AVAILABLE SOURCES FOR THIS QUERY:**\n"
        prompt += f"- WhatsApp Community: {agent_results['whatsapp']['count']} discussions found\n"
        prompt += f"- ALSCAS Website: {agent_results['alscas']['count']} documents found\n"
        prompt += f"- Medical Sources: {agent_results['medical']['count']} sources found\n"
        
        return prompt
    
    def _build_multi_agent_user_prompt(self, query: str, context: str, plan: QueryPlan) -> str:
        """Build user prompt for multi-agent synthesis"""
        prompt = f"""**USER QUESTION:**
{query}

**KNOWLEDGE BASE CONTEXT:**
{context}

**INSTRUCTIONS:**
Please provide a comprehensive answer using ONLY the information from the knowledge base context above.
Format your response with the 4 required sections (WhatsApp, ALSCAS, Medical, Combined).
Prioritize practical, actionable advice from community experience."""

        return prompt
    
    def _synthesize_with_reasoning(
        self,
        query: str,
        documents: List[Dict],
        plan: QueryPlan
    ) -> Dict[str, Any]:
        """Synthesize response with agentic reasoning"""
        # Prepare context with intelligent organization
        context = self._prepare_context_intelligent(documents, plan)
        
        # Build prompts
        system_prompt = self._get_system_prompt_agentic(plan)
        user_prompt = self._build_user_prompt_agentic(query, context, plan)
        
        # Call LLM
        try:
            if self.model_provider == 'claude':
                response_text = self._call_claude(system_prompt, user_prompt)
            elif self.model_provider in ['openai', 'openai-advanced', 'opensai-gpt4o', 'openai-o1-mini', 'openai-o1']:
                response_text = self._call_openai(system_prompt, user_prompt)
            elif self.model_provider in ['gemini', 'gemini-thinking']:
                response_text = self._call_gemini(system_prompt, user_prompt)
            elif self.model_provider == 'grok':
                response_text = self._call_grok(system_prompt, user_prompt)
            else:
                # Fallback to OpenAI
                response_text = self._call_openai(system_prompt, user_prompt)
            
            # Extract citations and calculate confidence
            citations = self._extract_citations(response_text, documents)
            confidence = self._calculate_confidence_advanced(documents, citations, plan)
            
            return {
                'response': response_text,
                'citations': citations,
                'confidence': confidence['level'],
                'confidence_factors': confidence['factors']
            }
            
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return self._generate_fallback_response(str(e))
    
    def _prepare_context_intelligent(
        self,
        documents: List[Dict],
        plan: QueryPlan
    ) -> str:
        """Intelligently prepare context based on query plan"""
        if not documents:
            return "⚠️ No specific information found in knowledge base."
        
        # Organize documents by type
        qa_pairs = [d for d in documents if d.get('chunk_type') == 'qa_pair']
        emergency_docs = [d for d in documents if d.get('emergency')]
        india_docs = [d for d in documents if d.get('india_specific')]
        medical_docs = [d for d in documents if 'medical' in d.get('collection', '')]
        
        context_sections = []
        
        # Emergency content first
        if plan.emergency_mode and emergency_docs:
            context_sections.append("=" * 60)
            context_sections.append("🚨 EMERGENCY EXPERIENCES FROM COMMUNITY")
            context_sections.append("=" * 60)
            for i, doc in enumerate(emergency_docs[:3], 1):
                context_sections.append(f"\n[EMERGENCY CASE #{i}]")
                context_sections.append(f"Source: {doc.get('source')}")
                context_sections.append(f"Relevance: {doc.get('relevance_score', 0):.2f}")
                context_sections.append(f"\n{doc.get('content', '')[:600]}")
                context_sections.append("-" * 40)
        
        # Q&A pairs (highest value)
        if qa_pairs:
            context_sections.append("\n" + "=" * 60)
            context_sections.append("💬 COMMUNITY Q&A - REAL SOLUTIONS")
            context_sections.append("=" * 60)
            for i, doc in enumerate(qa_pairs[:4], 1):
                india_marker = "🇮🇳" if doc.get('india_specific') else ""
                context_sections.append(f"\n[Q&A #{i}] {india_marker}")
                context_sections.append(f"Trust Score: {doc.get('trust_score')}/10")
                
                # Show costs if mentioned
                costs = doc.get('costs', [])
                if costs and costs != '[]':
                    try:
                        if isinstance(costs, str):
                            import ast
                            costs = ast.literal_eval(costs)
                        if costs:
                            avg_cost = sum(costs) / len(costs)
                            context_sections.append(f"💰 Costs mentioned: ₹{int(avg_cost):,} (avg)")
                    except:
                        pass
                
                context_sections.append(f"\n{doc.get('content', '')[:700]}")
                context_sections.append("-" * 40)
        
        # India-specific content
        if plan.india_priority and india_docs:
            context_sections.append("\n" + "=" * 60)
            context_sections.append("🇮🇳 INDIA-SPECIFIC GUIDANCE")
            context_sections.append("=" * 60)
            for i, doc in enumerate(india_docs[:3], 1):
                context_sections.append(f"\n[INDIA SOURCE #{i}]")
                context_sections.append(f"Source: {doc.get('source')}")
                context_sections.append(f"\n{doc.get('content', '')[:600]}")
                context_sections.append("-" * 40)
        
        # Medical authority content
        if medical_docs:
            context_sections.append("\n" + "=" * 60)
            context_sections.append("📚 MEDICAL AUTHORITY SOURCES")
            context_sections.append("=" * 60)
            for i, doc in enumerate(medical_docs[:3], 1):
                context_sections.append(f"\n[MEDICAL SOURCE #{i}]")
                context_sections.append(f"Organization: {doc.get('source')}")
                context_sections.append(f"\n{doc.get('content', '')[:500]}")
                context_sections.append("-" * 40)
        
        return "\n".join(context_sections)
    
    def _get_system_prompt_agentic(self, plan: QueryPlan) -> str:
        """Advanced system prompt with source prioritization and attribution"""
        base_prompt = """You are an AI assistant EXCLUSIVELY specialized in ALS/MND caregiving.

**YOUR ROLE:**
- Primary: Support ALS/MND caregivers with evidence-based, practical guidance
- Advocacy: Empower caregivers to question protocols and advocate for home care based on community experience
- Context: Focused on Indian caregivers but with global medical knowledge
- Approach: Multi-step reasoning, synthesis from the KNOWLEDGE BASE ONLY

**CRITICAL RESTRICTIONS:**
1. ❌ ONLY answer from the provided KNOWLEDGE BASE CONTEXT
2. ❌ Do NOT generate information from general knowledge
3. ❌ If no relevant information found in context, say: "I don't have specific information about this in my ALS knowledge base."
4. ❌ NEVER make up facts, statistics, or medical information

**SOURCE PRIORITIZATION (Highest to Lowest):**
1. 🥇 ALS Care & Support India - HIGHEST priority (real experience from 650+ Indian families)
2. 🥈 WhatsApp Community Discussions - Label explicitly as community source
3. 🥉 Medical Authority Sources (Mayo Clinic, MND Association, etc.)

**MANDATORY SOURCE ATTRIBUTION:**
For EVERY answer, you MUST cite sources:
- From WhatsApp/Community: "According to discussions in the ALS Care & Support India WhatsApp community..."
- From Medical: "According to [Source Name]..."
- Mixed sources: Clearly indicate which part comes from which source

**EMERGENCY RULES:**
🚨 If query involves breathing difficulty, choking, or urgent crisis:
   - IMMEDIATELY advise calling emergency services (India: 102/108, USA: 911)
   - Provide first-aid guidance if applicable
   - Do NOT delay with extensive information

**🇮🇳 INDIA PRIORITY:**
- Prioritize information from "ALS Care and Support India"
- Cost information in ₹ is highly valuable
- Local context (hospitals, equipment brands) matters

**NEVER GENERATE:**
- Personal information (names, phones, emails)
- Medical diagnoses or prescriptions
- False hope or unverified claims
- Information not present in the knowledge base context

**RESPONSE STRUCTURE:**
- Use ### for main section headings
- Use numbered lists (1., 2., 3.) for steps
- Use **bold** for emphasis (sparingly)
- Include 🚨 for warnings, 🇮🇳 for India-specific, 💰 for costs, 💬 for community insights

**TONE:** Compassionate, practical, evidence-based, with clear source attribution"""

        # Add query-specific instructions
        if plan.query_type == 'emergency':
            base_prompt += """

**EMERGENCY MODE ACTIVE:**
- Lead with immediate action steps
- Be concise and directive
- Include emergency contacts prominently"""

        elif plan.query_type == 'comparison':
            base_prompt += """

**COMPARISON MODE:**
- Create clear comparison structure
- Include pros/cons
- Include costs for Indian context"""

        if plan.needs_cost_info:
            base_prompt += """

**COST INFORMATION:**
- Provide ranges (budget/mid/premium)
- Include one-time vs recurring costs
- Mention government/charity options if known"""

        return base_prompt
    
    def _build_user_prompt_agentic(
        self,
        query: str,
        context: str,
        plan: QueryPlan
    ) -> str:
        """Build user prompt with reasoning framework"""
        prompt_parts = []
        
        prompt_parts.append(f"**USER QUERY:**\n{query}")
        prompt_parts.append(f"\n**KNOWLEDGE BASE CONTEXT:**\n{context}")
        
        # Add reasoning instructions
        prompt_parts.append("\n" + "=" * 60)
        prompt_parts.append("**YOUR REASONING PROCESS:**")
        prompt_parts.append("=" * 60)
        prompt_parts.append("""
Step 1: ANALYZE THE QUERY
- What is the caregiver really asking?
- What is their level of urgency?
- What context am I missing?

Step 2: EVALUATE SOURCES
- Which sources are most relevant?
- Do community experiences align with medical guidance?
- Are there any contradictions?
- Is India-specific information available?

Step 3: SYNTHESIZE ANSWER
- What is the core answer?
- What supporting details are needed?
- What warnings or cautions should I include?
- Are there cost implications (for India)?

Step 4: STRUCTURE RESPONSE
- How should I organize this for clarity?
- What format serves the caregiver best?
- Should I include examples or specific cases?""")
        
        prompt_parts.append("\n" + "=" * 60)
        prompt_parts.append("**PROVIDE YOUR RESPONSE:**")
        prompt_parts.append("=" * 60)
        
        if plan.emergency_mode:
            prompt_parts.append("""
Format:
🚨 EMERGENCY ACTION REQUIRED

**IMMEDIATE STEPS:**
1. [First action]
2. [Second action]
3. [When to call emergency]

**EMERGENCY CONTACTS:**
- India: 102 (Ambulance) / 108 (Emergency)
- USA: 911

**CRITICAL:** Do not delay seeking professional help.""")

        elif plan.query_type == 'comparison':
            prompt_parts.append("""
Format:
### Comparison: [Topic A] vs [Topic B]

**Quick Answer:**
[One sentence recommendation based on community consensus]

**Detailed Comparison:**

| Aspect | Option A | Option B |
|--------|----------|----------|
| [aspect] | [details] | [details] |

**Community Consensus:**
[What families have found works best]

**Cost Comparison (India):**
- Option A: ₹[amount]
- Option B: ₹[amount]

**Recommendation:**
[Clear guidance based on context]""")

        else:
            prompt_parts.append("""
Format:
### [Main Topic]

**Direct Answer:** [1-2 sentences]

**Key Points:**
1. [First point]
2. [Second point]
3. [Third point]

### 🇮🇳 For Indian Caregivers
[India-specific guidance including costs, availability]

**When to Seek Help:**
[Warning signs requiring medical attention]

💡 *Consult healthcare professionals for personalized advice.*""")
        
        prompt_parts.append("\n**Now provide your complete response:**")
        
        return "\n".join(prompt_parts)
    
    def _call_claude(self, system_prompt: str, user_prompt: str) -> str:
        """Call Claude API"""
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=3000,
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.content[0].text
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API - handles both standard and reasoning models"""
        
        # Check if using reasoning model (o1 series)
        is_reasoning = getattr(self, 'is_reasoning_model', False)
        
        if is_reasoning:
            # o1 models: No system message, no temperature, use max_completion_tokens
            # Combine system and user prompts for reasoning models
            combined_prompt = f"""INSTRUCTIONS:
{system_prompt}

USER QUERY:
{user_prompt}"""
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": combined_prompt}
                ],
                max_completion_tokens=4000  # Reasoning models need more tokens
            )
        else:
            # Standard models: GPT-4o-mini, GPT-4o
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=3000
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
                max_output_tokens=3000
            )
        )
        return response.text
    
    def _call_grok(self, system_prompt: str, user_prompt: str) -> str:
        """Call Grok API"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=3000
        )
        return response.choices[0].message.content
    
    def _handle_emergency(self, query: str, plan: QueryPlan) -> Dict[str, Any]:
        """Handle emergency queries immediately"""
        # Get emergency-specific documents
        documents = self.vector_store.hybrid_search(
            query=query,
            emergency_mode=True,
            n_results=10
        )
        
        emergency_prompt = f"""🚨 EMERGENCY QUERY: {query}

Relevant emergency cases from community:
{self._prepare_context_intelligent(documents[:5], plan)}

Provide IMMEDIATE actionable guidance:
1. What to do RIGHT NOW
2. When to call emergency services
3. What information to have ready

Be direct, clear, and prioritize safety."""

        try:
            system = "You are an emergency medical guidance AI. Prioritize immediate safety and action."
            
            if self.model_provider == 'claude':
                response_text = self._call_claude(system, emergency_prompt)
            elif self.model_provider == 'openai':
                response_text = self._call_openai(system, emergency_prompt)
            elif self.model_provider == 'gemini':
                response_text = self._call_gemini(system, emergency_prompt)
            else:
                response_text = self._call_grok(system, emergency_prompt)
            
            # Select relevant images for emergency queries too
            images = []
            if self.image_manager:
                try:
                    context = self._prepare_context_intelligent(documents[:5], plan)
                    images = self.image_manager.suggest_images(query, context, max_images=3)
                    if images:
                        logger.info(f"✅ Selected {len(images)} images for emergency query")
                    else:
                        logger.info("ℹ️  No matching images found for emergency query")
                except Exception as e:
                    logger.error(f"Error suggesting images for emergency: {e}")
            
            return {
                'response': response_text,
                'citations': self._extract_citations(response_text, documents),
                'confidence': 'high',
                'confidence_factors': {
                    'emergency_mode': True,
                    'sources': len(documents)
                },
                'emergency': True,
                'timestamp': datetime.now().isoformat(),
                'query_type': 'emergency',
                'model_used': f"{self.model_provider}/{self.model_name}",
                'images': images
            }
            
        except Exception as e:
            # Fallback emergency response
            return {
                'response': """🚨 EMERGENCY SITUATION DETECTED

**IMMEDIATE ACTION:**
1. Call emergency services NOW:
   - India: 102 (Ambulance) / 108 (Emergency)
   - USA: 911
   - EU: 112

2. Stay with the patient
3. If breathing difficulty: Position upright at 45° angle
4. If choking: Attempt back blows if trained

**This AI cannot provide emergency medical care.**
**Professional help is required immediately.**

Do not delay seeking help.""",
                'citations': [],
                'confidence': 'protocol',
                'emergency': True,
                'error': str(e)
            }
    
    def _extract_citations(self, response: str, documents: List[Dict]) -> List[Dict]:
        """Extract and format citations"""
        citations = []
        response_lower = response.lower()
        
        for doc in documents[:10]:
            source = doc.get('source', '')
            if source and (
                source.lower() in response_lower or
                any(word in response_lower for word in source.lower().split()[:3])
            ):
                citations.append({
                    'source': source,
                    'trust_score': doc.get('trust_score', 5),
                    'collection': doc.get('collection', 'unknown'),
                    'india_specific': doc.get('india_specific', False)
                })
        
        # Remove duplicates
        seen = set()
        unique_citations = []
        for c in citations:
            if c['source'] not in seen:
                seen.add(c['source'])
                unique_citations.append(c)
        
        return unique_citations[:5]
    
    def _calculate_confidence_advanced(
        self,
        documents: List[Dict],
        citations: List[Dict],
        plan: QueryPlan
    ) -> Dict[str, Any]:
        """Advanced confidence calculation"""
        if not documents:
            return {
                'level': 'low',
                'score': 0.2,
                'factors': {'reason': 'No relevant documents found'}
            }
        
        factors = {}
        score = 0.5  # Base score
        
        # Factor 1: Source quality
        avg_trust = sum(d.get('trust_score', 5) for d in documents[:5]) / 5
        trust_boost = (avg_trust - 5) / 5
        score += trust_boost * 0.2
        factors['source_quality'] = f"{avg_trust:.1f}/10"
        
        # Factor 2: India-specific match
        if plan.india_priority:
            india_docs = sum(1 for d in documents[:5] if d.get('india_specific'))
            if india_docs >= 2:
                score += 0.15
            factors['india_match'] = f"{india_docs}/5 docs"
        
        # Factor 3: Q&A pairs found
        qa_count = sum(1 for d in documents[:5] if d.get('chunk_type') == 'qa_pair')
        if qa_count >= 2:
            score += 0.15
        factors['qa_pairs_found'] = qa_count
        
        # Factor 4: Citations used
        if len(citations) >= 3:
            score += 0.1
        factors['citations'] = len(citations)
        
        # Determine level
        if score >= 0.8:
            level = 'high'
        elif score >= 0.6:
            level = 'medium'
        else:
            level = 'low'
        
        factors['final_score'] = f"{score:.2f}"
        
        return {
            'level': level,
            'score': score,
            'factors': factors
        }
    
    def _generate_fallback_response(self, error_msg: str = "") -> Dict[str, Any]:
        """Generate fallback response"""
        return {
            'response': """I apologize, but I'm experiencing technical difficulties.

**For immediate ALS caregiving support:**
- contact your primary support group 


Please try your question again, or contact healthcare professionals directly.""",
            'citations': [],
            'confidence': 'system_error',
            'confidence_factors': {'error': error_msg},
            'emergency': False,
            'timestamp': datetime.now().isoformat()
        }
