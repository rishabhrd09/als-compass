"""
Advanced Agentic AI System with Multi-Step Reasoning
Supports: Claude, OpenAI, Gemini, Grok
Features: Query analysis, multi-stage retrieval, intelligent context preparation
"""
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QueryPlan:
    """Query execution plan"""
    query_type: str  # 'simple', 'complex', 'emergency', 'comparison'
    categories: List[str]  # Relevant categories
    search_strategy: str  # 'focused', 'broad', 'multi-stage'
    india_priority: bool
    emergency_mode: bool
    needs_cost_info: bool
    needs_technical_details: bool
    requires_multi_source: bool


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
    """Advanced agentic AI system with planning and execution"""
    
    def __init__(self, model_provider: str = None):
        self.model_provider = model_provider or os.getenv('DEFAULT_MODEL_PROVIDER', 'openai')
        
        # Import enhanced vector store
        from vector_store_enhanced import EnhancedVectorStore
        self.vector_store = EnhancedVectorStore()
        self.query_analyzer = QueryAnalyzer()
        
        # Initialize provider
        self._init_provider()
        
        logger.info("✅ Agentic AI System initialized")
        logger.info(f"   Provider: {self.model_provider}")
        logger.info(f"   Model: {self.model_name}")
    
    def _init_provider(self):
        """Initialize AI provider"""
        # Handle OpenAI variants
        if self.model_provider in ['openai', 'openai-gpt4o', 'openai-o1-mini', 'openai-o1']:
            self._init_openai()
        elif self.model_provider == 'claude':
            self._init_claude()
        elif self.model_provider == 'gemini':
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
            self.model_name = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
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
        """Main agentic processing pipeline"""
        try:
            # Step 1: Analyze and plan
            plan = self.query_analyzer.analyze_query(query)
            logger.info(f"Query Plan: {plan.query_type}, Categories: {plan.categories}")
            
            # Step 2: Handle emergency immediately
            if plan.emergency_mode:
                return self._handle_emergency(query, plan)
            
            # Step 3: Execute multi-stage retrieval
            documents = self._execute_retrieval(query, plan)
            
            # Step 4: Synthesize response with agent reasoning
            response = self._synthesize_with_reasoning(query, documents, plan)
            
            # Step 5: Add comprehensive metadata
            response.update({
                'timestamp': datetime.now().isoformat(),
                'query_type': plan.query_type,
                'categories': plan.categories,
                'sources_used': len(documents),
                'emergency': False,
                'model_used': f"{self.model_provider}/{self.model_name}",
                'india_prioritized': plan.india_priority,
                'search_strategy': plan.search_strategy
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
            elif self.model_provider in ['openai', 'openai-gpt4o', 'openai-o1-mini', 'openai-o1']:
                response_text = self._call_openai(system_prompt, user_prompt)
            elif self.model_provider == 'gemini':
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
        """Advanced system prompt with reasoning framework"""
        base_prompt = """You are an empathetic, intelligent AI assistant specialized in ALS caregiving.

**YOUR ROLE:**
- Primary: Support ALS caregivers with evidence-based, practical guidance
- Context: Focused on Indian caregivers but with global medical knowledge
- Approach: Multi-step reasoning, synthesis from diverse sources

**CRITICAL RULES:**
1. 🚨 EMERGENCIES: If query involves breathing difficulty, choking, or urgent crisis:
   - Immediately advise calling emergency services (India: 102/108, USA: 911)
   - Provide first-aid guidance if applicable
   - Do NOT delay with extensive information

2. 🇮🇳 INDIA PRIORITY: Prioritize information from "ALS Care and Support India" community
   - This is REAL experience from 650+ Indian families
   - Cost information in ₹ is highly valuable
   - Local context matters

3. 📊 EVIDENCE-BASED: Synthesize from multiple sources
   - Compare community experience with medical guidelines
   - Be transparent about confidence level

4. ❌ NEVER GENERATE:
   - Personal information (names, phones, emails)
   - Medical diagnoses or prescriptions
   - False hope or unverified claims

**RESPONSE STRUCTURE:**
- Use ### for main section headings
- Use numbered lists (1., 2., 3.) for steps
- Use **bold** for emphasis (sparingly)
- Include 🚨 for warnings, 🇮🇳 for India-specific, 💰 for costs

**ATTRIBUTION FORMAT:**
- Community: "According to ALS Care & Support India community..."
- Medical: "According to [Organization]..."

**TONE:** Compassionate, practical, evidence-based"""

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
                'model_used': f"{self.model_provider}/{self.model_name}"
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
