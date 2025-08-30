"""
Natural Language Processing service for text analysis and entity extraction
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import spacy
from spacy.matcher import Matcher
from spacy.util import filter_spans

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class NLPProcessingError(Exception):
    """Custom exception for NLP processing errors"""
    pass


class NLPProcessor:
    """Natural Language Processing service for document analysis"""
    
    def __init__(self):
        self.nlp = None
        self.matcher = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize spaCy models and matchers"""
        try:
            # Load English language model
            # Note: In production, you'd want to download this model first:
            # python -m spacy download en_core_web_lg
            self.nlp = spacy.load("en_core_web_sm")  # Using small model for now
            
            # Initialize matcher for custom patterns
            self.matcher = Matcher(self.nlp.vocab)
            self._setup_custom_patterns()
            
            logger.info("NLP models initialized successfully")
            
        except OSError:
            logger.warning("spaCy model not found, using basic processing")
            self.nlp = None
            self.matcher = None
    
    def _setup_custom_patterns(self):
        """Setup custom patterns for business and financial entities"""
        if not self.matcher:
            return
        
        # Financial metrics patterns
        financial_patterns = [
            [{"LOWER": {"IN": ["revenue", "income", "sales"]}},
             {"IS_CURRENCY": True, "OP": "?"},
             {"LIKE_NUM": True, "OP": "?"}],
            [{"LOWER": {"IN": ["profit", "loss", "ebitda"]}},
             {"IS_CURRENCY": True, "OP": "?"},
             {"LIKE_NUM": True, "OP": "?"}],
            [{"LOWER": {"IN": ["valuation", "funding", "investment"]}},
             {"IS_CURRENCY": True, "OP": "?"},
             {"LIKE_NUM": True, "OP": "?"}],
            [{"LOWER": {"IN": ["burn", "runway"]}},
             {"LOWER": "rate", "OP": "?"},
             {"IS_CURRENCY": True, "OP": "?"},
             {"LIKE_NUM": True, "OP": "?"}],
        ]
        
        # Business model patterns
        business_patterns = [
            [{"LOWER": {"IN": ["b2b", "b2c", "b2b2c"]}},
            [{"LOWER": "business"}, {"LOWER": "model"}],
            [{"LOWER": {"IN": ["saas", "marketplace", "platform"]}},
            [{"LOWER": {"IN": ["subscription", "freemium", "transaction"]}}, {"LOWER": "model", "OP": "?"}],
        ]
        
        # Market patterns
        market_patterns = [
            [{"LOWER": {"IN": ["tam", "sam", "som"]}},
            [{"LOWER": "total"}, {"LOWER": "addressable"}, {"LOWER": "market"}],
            [{"LOWER": "market"}, {"LOWER": {"IN": ["size", "opportunity", "share"]}},
            [{"LOWER": {"IN": ["competitor", "competition", "competitive"]}},
        ]
        
        # Add patterns to matcher
        self.matcher.add("FINANCIAL_METRICS", financial_patterns)
        self.matcher.add("BUSINESS_MODEL", business_patterns)
        self.matcher.add("MARKET_INFO", market_patterns)
    
    async def analyze_text(self, text: str, document_type: str = "general") -> Dict[str, Any]:
        """
        Comprehensive text analysis including entities, sentiment, and business insights
        
        Args:
            text: Text content to analyze
            document_type: Type of document (pitch_deck, financial_model, business_plan)
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Starting NLP analysis for {document_type} document")
        
        if not text or len(text.strip()) == 0:
            return self._empty_analysis_result()
        
        try:
            # Basic text preprocessing
            cleaned_text = self._preprocess_text(text)
            
            # Perform different analyses
            entities = await self._extract_entities(cleaned_text)
            financial_metrics = await self._extract_financial_metrics(cleaned_text)
            business_insights = await self._extract_business_insights(cleaned_text)
            market_analysis = await self._extract_market_information(cleaned_text)
            team_information = await self._extract_team_information(cleaned_text)
            risk_factors = await self._identify_risk_factors(cleaned_text)
            sentiment = await self._analyze_sentiment(cleaned_text)
            
            # Document-specific analysis
            document_classification = self._classify_document_type(cleaned_text)
            key_topics = await self._extract_key_topics(cleaned_text)
            
            return {
                'text_analysis': {
                    'original_length': len(text),
                    'processed_length': len(cleaned_text),
                    'word_count': len(cleaned_text.split()),
                    'sentence_count': len(self._split_sentences(cleaned_text)),
                    'language': 'en',  # Could be detected automatically
                    'readability_score': self._calculate_readability(cleaned_text)
                },
                'entities': entities,
                'financial_metrics': financial_metrics,
                'business_insights': business_insights,
                'market_analysis': market_analysis,
                'team_information': team_information,
                'risk_factors': risk_factors,
                'sentiment': sentiment,
                'document_classification': document_classification,
                'key_topics': key_topics,
                'confidence_score': self._calculate_overall_confidence(entities, financial_metrics, business_insights)
            }
            
        except Exception as e:
            logger.error(f"NLP analysis failed: {str(e)}")
            raise NLPProcessingError(f"Text analysis failed: {str(e)}")
    
    async def _extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract named entities from text"""
        entities = {
            'organizations': [],
            'people': [],
            'locations': [],
            'money': [],
            'dates': [],
            'products': [],
            'technologies': []
        }
        
        if not self.nlp:
            return entities
        
        try:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                entity_info = {
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': getattr(ent, 'confidence', 0.8)
                }
                
                # Categorize entities
                if ent.label_ in ['ORG', 'CORP']:
                    entities['organizations'].append(entity_info)
                elif ent.label_ in ['PERSON', 'PER']:
                    entities['people'].append(entity_info)
                elif ent.label_ in ['GPE', 'LOC', 'LOCATION']:
                    entities['locations'].append(entity_info)
                elif ent.label_ in ['MONEY', 'CURRENCY']:
                    entities['money'].append(entity_info)
                elif ent.label_ in ['DATE', 'TIME']:
                    entities['dates'].append(entity_info)
                elif ent.label_ in ['PRODUCT', 'WORK_OF_ART']:
                    entities['products'].append(entity_info)
            
            # Extract technology-related terms
            tech_keywords = ['ai', 'ml', 'blockchain', 'iot', 'saas', 'api', 'cloud', 'mobile', 'web', 'app']
            for keyword in tech_keywords:
                if keyword.lower() in text.lower():
                    entities['technologies'].append({
                        'text': keyword,
                        'label': 'TECHNOLOGY',
                        'confidence': 0.7
                    })
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
            return entities
    
    async def _extract_financial_metrics(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract financial metrics and numbers from text"""
        financial_metrics = {
            'revenue_metrics': [],
            'funding_metrics': [],
            'profitability_metrics': [],
            'growth_metrics': [],
            'valuation_metrics': []
        }
        
        try:
            # Revenue patterns
            revenue_patterns = [
                r'revenue[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)\s*([kmb]?)',
                r'sales[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)\s*([kmb]?)',
                r'income[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)\s*([kmb]?)',
                r'\$([0-9,]+(?:\.[0-9]+)?)\s*([kmb]?)\s+revenue',
            ]
            
            for pattern in revenue_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    amount = match.group(1).replace(',', '')
                    unit = match.group(2).lower() if len(match.groups()) > 1 else ''
                    
                    financial_metrics['revenue_metrics'].append({
                        'type': 'revenue',
                        'amount': float(amount),
                        'unit': unit,
                        'text': match.group(0),
                        'confidence': 0.8
                    })
            
            # Funding patterns
            funding_patterns = [
                r'raised[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)\s*([kmb]?)',
                r'funding[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)\s*([kmb]?)',
                r'investment[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)\s*([kmb]?)',
                r'series\s+[abc][:\s]+\$?([0-9,]+(?:\.[0-9]+)?)\s*([kmb]?)',
            ]
            
            for pattern in funding_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    amount = match.group(1).replace(',', '')
                    unit = match.group(2).lower() if len(match.groups()) > 1 else ''
                    
                    financial_metrics['funding_metrics'].append({
                        'type': 'funding',
                        'amount': float(amount),
                        'unit': unit,
                        'text': match.group(0),
                        'confidence': 0.8
                    })
            
            # Valuation patterns
            valuation_patterns = [
                r'valuation[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)\s*([kmb]?)',
                r'valued\s+at[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)\s*([kmb]?)',
                r'worth[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)\s*([kmb]?)',
            ]
            
            for pattern in valuation_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    amount = match.group(1).replace(',', '')
                    unit = match.group(2).lower() if len(match.groups()) > 1 else ''
                    
                    financial_metrics['valuation_metrics'].append({
                        'type': 'valuation',
                        'amount': float(amount),
                        'unit': unit,
                        'text': match.group(0),
                        'confidence': 0.8
                    })
            
            return financial_metrics
            
        except Exception as e:
            logger.error(f"Financial metrics extraction failed: {str(e)}")
            return financial_metrics
    
    async def _extract_business_insights(self, text: str) -> Dict[str, Any]:
        """Extract business model and strategy insights"""
        insights = {
            'business_model': None,
            'revenue_model': None,
            'target_market': [],
            'value_proposition': [],
            'competitive_advantages': []
        }
        
        try:
            # Business model detection
            business_models = {
                'saas': ['saas', 'software as a service', 'subscription software'],
                'marketplace': ['marketplace', 'platform', 'two-sided market'],
                'e-commerce': ['e-commerce', 'online store', 'retail'],
                'fintech': ['fintech', 'financial technology', 'payments'],
                'healthtech': ['healthtech', 'medical', 'healthcare'],
                'edtech': ['edtech', 'education', 'learning platform']
            }
            
            text_lower = text.lower()
            for model, keywords in business_models.items():
                if any(keyword in text_lower for keyword in keywords):
                    insights['business_model'] = model
                    break
            
            # Revenue model detection
            revenue_models = {
                'subscription': ['subscription', 'monthly fee', 'recurring'],
                'transaction': ['transaction fee', 'commission', 'per transaction'],
                'freemium': ['freemium', 'free tier', 'premium features'],
                'advertising': ['advertising', 'ads', 'sponsored content'],
                'licensing': ['licensing', 'license fee', 'royalty']
            }
            
            for model, keywords in revenue_models.items():
                if any(keyword in text_lower for keyword in keywords):
                    insights['revenue_model'] = model
                    break
            
            # Extract target market mentions
            market_indicators = ['target market', 'customer segment', 'user base', 'audience']
            for indicator in market_indicators:
                if indicator in text_lower:
                    # Extract surrounding context
                    start = text_lower.find(indicator)
                    context = text[max(0, start-50):start+200]
                    insights['target_market'].append(context.strip())
            
            return insights
            
        except Exception as e:
            logger.error(f"Business insights extraction failed: {str(e)}")
            return insights
    
    async def _extract_market_information(self, text: str) -> Dict[str, Any]:
        """Extract market size, competition, and opportunity information"""
        market_info = {
            'market_size': [],
            'competitors': [],
            'market_trends': [],
            'opportunities': []
        }
        
        try:
            # Market size patterns
            market_size_patterns = [
                r'market size[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)\s*([kmb]?)',
                r'tam[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)\s*([kmb]?)',
                r'total addressable market[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)\s*([kmb]?)',
            ]
            
            for pattern in market_size_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    market_info['market_size'].append({
                        'amount': match.group(1),
                        'unit': match.group(2) if len(match.groups()) > 1 else '',
                        'context': match.group(0)
                    })
            
            # Competitor detection
            competitor_indicators = ['competitor', 'competition', 'rival', 'alternative']
            for indicator in competitor_indicators:
                if indicator in text.lower():
                    # Extract surrounding context for competitor names
                    pattern = rf'{indicator}[s]?[:\s]+([A-Z][a-zA-Z\s]+(?:,\s*[A-Z][a-zA-Z\s]+)*)'
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        competitors = [comp.strip() for comp in match.group(1).split(',')]
                        market_info['competitors'].extend(competitors)
            
            return market_info
            
        except Exception as e:
            logger.error(f"Market information extraction failed: {str(e)}")
            return market_info
    
    async def _extract_team_information(self, text: str) -> Dict[str, Any]:
        """Extract information about the founding team and key personnel"""
        team_info = {
            'founders': [],
            'key_personnel': [],
            'team_size': None,
            'experience_highlights': []
        }
        
        try:
            # Founder patterns
            founder_patterns = [
                r'founder[s]?[:\s]+([A-Z][a-zA-Z\s]+)',
                r'co-founder[s]?[:\s]+([A-Z][a-zA-Z\s]+)',
                r'ceo[:\s]+([A-Z][a-zA-Z\s]+)',
                r'founded by[:\s]+([A-Z][a-zA-Z\s]+)',
            ]
            
            for pattern in founder_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    team_info['founders'].append({
                        'name': match.group(1).strip(),
                        'role': 'founder',
                        'context': match.group(0)
                    })
            
            # Team size patterns
            team_size_patterns = [
                r'team of ([0-9]+)',
                r'([0-9]+) employees',
                r'([0-9]+) team members',
            ]
            
            for pattern in team_size_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    team_info['team_size'] = int(match.group(1))
                    break
            
            return team_info
            
        except Exception as e:
            logger.error(f"Team information extraction failed: {str(e)}")
            return team_info
    
    async def _identify_risk_factors(self, text: str) -> List[Dict[str, Any]]:
        """Identify potential risk factors mentioned in the text"""
        risk_factors = []
        
        try:
            # Risk keywords and categories
            risk_categories = {
                'market': ['market risk', 'competition', 'market downturn', 'demand risk'],
                'financial': ['cash flow', 'funding', 'burn rate', 'profitability'],
                'operational': ['scalability', 'operations', 'supply chain', 'execution'],
                'regulatory': ['regulation', 'compliance', 'legal', 'policy'],
                'technology': ['technical risk', 'security', 'platform', 'infrastructure'],
                'team': ['key person', 'talent', 'hiring', 'retention']
            }
            
            text_lower = text.lower()
            for category, keywords in risk_categories.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        # Extract context around the risk mention
                        start = text_lower.find(keyword)
                        context = text[max(0, start-100):start+100]
                        
                        risk_factors.append({
                            'category': category,
                            'keyword': keyword,
                            'context': context.strip(),
                            'severity': 'medium',  # Could be determined by additional analysis
                            'confidence': 0.7
                        })
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"Risk factor identification failed: {str(e)}")
            return risk_factors
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze overall sentiment of the text"""
        # Basic sentiment analysis (in production, you'd use a proper sentiment model)
        positive_words = ['growth', 'success', 'opportunity', 'strong', 'excellent', 'innovative', 'leading']
        negative_words = ['risk', 'challenge', 'problem', 'decline', 'loss', 'difficult', 'concern']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        positive_ratio = positive_count / total_words if total_words > 0 else 0
        negative_ratio = negative_count / total_words if total_words > 0 else 0
        
        if positive_ratio > negative_ratio:
            sentiment = 'positive'
            confidence = min(positive_ratio * 10, 1.0)
        elif negative_ratio > positive_ratio:
            sentiment = 'negative'
            confidence = min(negative_ratio * 10, 1.0)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_indicators': positive_count,
            'negative_indicators': negative_count,
            'positive_ratio': positive_ratio,
            'negative_ratio': negative_ratio
        }
    
    async def _extract_key_topics(self, text: str) -> List[Dict[str, Any]]:
        """Extract key topics and themes from the text"""
        # Simple keyword-based topic extraction
        # In production, you'd use more sophisticated topic modeling
        
        topic_keywords = {
            'technology': ['ai', 'machine learning', 'blockchain', 'iot', 'cloud', 'mobile', 'web'],
            'business': ['revenue', 'profit', 'growth', 'market', 'customer', 'sales'],
            'finance': ['funding', 'investment', 'valuation', 'cash flow', 'burn rate'],
            'product': ['product', 'feature', 'platform', 'solution', 'service'],
            'market': ['market', 'industry', 'sector', 'competition', 'opportunity'],
            'team': ['team', 'founder', 'employee', 'talent', 'experience']
        }
        
        topics = []
        text_lower = text.lower()
        
        for topic, keywords in topic_keywords.items():
            keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
            if keyword_count > 0:
                topics.append({
                    'topic': topic,
                    'relevance_score': keyword_count / len(keywords),
                    'keyword_matches': keyword_count
                })
        
        # Sort by relevance
        topics.sort(key=lambda x: x['relevance_score'], reverse=True)
        return topics[:5]  # Return top 5 topics
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\$\%]', '', text)
        
        return text.strip()
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate basic readability score"""
        words = text.split()
        sentences = self._split_sentences(text)
        
        if len(sentences) == 0 or len(words) == 0:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simple readability score (0-1, higher is more readable)
        readability = max(0, 1 - (avg_sentence_length / 20) - (avg_word_length / 10))
        return min(readability, 1.0)
    
    def _calculate_overall_confidence(self, entities: Dict, financial_metrics: Dict, business_insights: Dict) -> float:
        """Calculate overall confidence score for the analysis"""
        confidence_factors = []
        
        # Entity extraction confidence
        total_entities = sum(len(ent_list) for ent_list in entities.values())
        if total_entities > 0:
            confidence_factors.append(min(total_entities / 10, 1.0))
        
        # Financial metrics confidence
        total_financial = sum(len(metric_list) for metric_list in financial_metrics.values())
        if total_financial > 0:
            confidence_factors.append(min(total_financial / 5, 1.0))
        
        # Business insights confidence
        insights_found = sum(1 for value in business_insights.values() if value)
        if insights_found > 0:
            confidence_factors.append(min(insights_found / 3, 1.0))
        
        if not confidence_factors:
            return 0.3  # Base confidence
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _classify_document_type(self, text: str) -> Dict[str, Any]:
        """Classify the type of document based on content"""
        document_types = {
            'pitch_deck': ['pitch', 'deck', 'presentation', 'slide', 'investment opportunity'],
            'business_plan': ['business plan', 'executive summary', 'strategy', 'operations'],
            'financial_model': ['financial model', 'projections', 'forecast', 'revenue model'],
            'market_analysis': ['market analysis', 'market research', 'competitive analysis'],
            'technical_document': ['technical', 'architecture', 'development', 'api']
        }
        
        text_lower = text.lower()
        scores = {}
        
        for doc_type, keywords in document_types.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[doc_type] = score / len(keywords)
        
        if scores:
            best_type = max(scores.keys(), key=lambda k: scores[k])
            return {
                'document_type': best_type,
                'confidence': scores[best_type],
                'all_scores': scores
            }
        
        return {
            'document_type': 'general',
            'confidence': 0.5,
            'all_scores': {}
        }
    
    def _empty_analysis_result(self) -> Dict[str, Any]:
        """Return empty analysis result structure"""
        return {
            'text_analysis': {
                'original_length': 0,
                'processed_length': 0,
                'word_count': 0,
                'sentence_count': 0,
                'language': 'en',
                'readability_score': 0.0
            },
            'entities': {
                'organizations': [],
                'people': [],
                'locations': [],
                'money': [],
                'dates': [],
                'products': [],
                'technologies': []
            },
            'financial_metrics': {
                'revenue_metrics': [],
                'funding_metrics': [],
                'profitability_metrics': [],
                'growth_metrics': [],
                'valuation_metrics': []
            },
            'business_insights': {
                'business_model': None,
                'revenue_model': None,
                'target_market': [],
                'value_proposition': [],
                'competitive_advantages': []
            },
            'market_analysis': {
                'market_size': [],
                'competitors': [],
                'market_trends': [],
                'opportunities': []
            },
            'team_information': {
                'founders': [],
                'key_personnel': [],
                'team_size': None,
                'experience_highlights': []
            },
            'risk_factors': [],
            'sentiment': {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'positive_indicators': 0,
                'negative_indicators': 0,
                'positive_ratio': 0.0,
                'negative_ratio': 0.0
            },
            'document_classification': {
                'document_type': 'general',
                'confidence': 0.5,
                'all_scores': {}
            },
            'key_topics': [],
            'confidence_score': 0.0
        }


# Global NLP processor instance
nlp_processor = NLPProcessor()
