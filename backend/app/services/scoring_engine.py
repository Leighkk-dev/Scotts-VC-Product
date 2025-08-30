"""
Scoring engine for investment evaluation and risk assessment
"""

import asyncio
import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ScoreResult:
    """Data class for scoring results"""
    financial_score: float
    market_score: float
    team_score: float
    product_score: float
    risk_score: float
    overall_score: float
    confidence_interval: Tuple[float, float]
    recommendation: str
    reasoning: Dict[str, Any]


class ScoringEngineError(Exception):
    """Custom exception for scoring engine errors"""
    pass


class ScoringEngine:
    """Investment scoring engine with multi-dimensional analysis"""
    
    def __init__(self):
        self.weights = {
            'financial': 0.30,
            'market': 0.25,
            'team': 0.25,
            'product': 0.20
        }
        
        # Scoring thresholds for recommendations
        self.recommendation_thresholds = {
            'strong_buy': 85,
            'buy': 70,
            'hold': 50,
            'pass': 0
        }
    
    async def calculate_investment_score(
        self,
        nlp_analysis: Dict[str, Any],
        document_content: Dict[str, Any],
        venture_data: Optional[Dict[str, Any]] = None
    ) -> ScoreResult:
        """
        Calculate comprehensive investment score based on multiple dimensions
        
        Args:
            nlp_analysis: Results from NLP analysis
            document_content: Extracted document content
            venture_data: Additional venture information
            
        Returns:
            ScoreResult with detailed scoring breakdown
        """
        logger.info("Starting investment score calculation")
        
        try:
            # Calculate individual dimension scores
            financial_score = await self._calculate_financial_score(nlp_analysis, document_content)
            market_score = await self._calculate_market_score(nlp_analysis, document_content)
            team_score = await self._calculate_team_score(nlp_analysis, document_content)
            product_score = await self._calculate_product_score(nlp_analysis, document_content)
            
            # Calculate risk-adjusted scores
            risk_factors = await self._assess_risk_factors(nlp_analysis, document_content)
            risk_score = risk_factors['overall_risk_score']
            
            # Apply risk adjustment to individual scores
            risk_adjustment = 1 - (risk_score / 100 * 0.3)  # Max 30% reduction
            
            adjusted_financial = financial_score * risk_adjustment
            adjusted_market = market_score * risk_adjustment
            adjusted_team = team_score * risk_adjustment
            adjusted_product = product_score * risk_adjustment
            
            # Calculate weighted overall score
            overall_score = (
                adjusted_financial * self.weights['financial'] +
                adjusted_market * self.weights['market'] +
                adjusted_team * self.weights['team'] +
                adjusted_product * self.weights['product']
            )
            
            # Calculate confidence interval
            confidence_interval = self._calculate_confidence_interval(
                overall_score, nlp_analysis.get('confidence_score', 0.5)
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(overall_score)
            
            # Compile reasoning
            reasoning = {
                'financial_reasoning': self._get_financial_reasoning(nlp_analysis, financial_score),
                'market_reasoning': self._get_market_reasoning(nlp_analysis, market_score),
                'team_reasoning': self._get_team_reasoning(nlp_analysis, team_score),
                'product_reasoning': self._get_product_reasoning(nlp_analysis, product_score),
                'risk_assessment': risk_factors,
                'key_strengths': self._identify_key_strengths(nlp_analysis, {
                    'financial': adjusted_financial,
                    'market': adjusted_market,
                    'team': adjusted_team,
                    'product': adjusted_product
                }),
                'key_concerns': self._identify_key_concerns(risk_factors, {
                    'financial': financial_score,
                    'market': market_score,
                    'team': team_score,
                    'product': product_score
                })
            }
            
            result = ScoreResult(
                financial_score=round(adjusted_financial, 2),
                market_score=round(adjusted_market, 2),
                team_score=round(adjusted_team, 2),
                product_score=round(adjusted_product, 2),
                risk_score=round(risk_score, 2),
                overall_score=round(overall_score, 2),
                confidence_interval=confidence_interval,
                recommendation=recommendation,
                reasoning=reasoning
            )
            
            logger.info(f"Investment score calculation completed: {overall_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Scoring calculation failed: {str(e)}")
            raise ScoringEngineError(f"Score calculation failed: {str(e)}")
    
    async def _calculate_financial_score(
        self, 
        nlp_analysis: Dict[str, Any], 
        document_content: Dict[str, Any]
    ) -> float:
        """Calculate financial health score (0-100)"""
        score = 50.0  # Base score
        
        try:
            financial_metrics = nlp_analysis.get('financial_metrics', {})
            
            # Revenue metrics analysis
            revenue_metrics = financial_metrics.get('revenue_metrics', [])
            if revenue_metrics:
                score += 15  # Has revenue data
                
                # Check for growth indicators
                for metric in revenue_metrics:
                    if metric.get('amount', 0) > 1000000:  # > $1M revenue
                        score += 10
                        break
            
            # Funding metrics analysis
            funding_metrics = financial_metrics.get('funding_metrics', [])
            if funding_metrics:
                score += 10  # Has funding
                
                # Check funding amount
                for metric in funding_metrics:
                    amount = metric.get('amount', 0)
                    unit = metric.get('unit', '').lower()
                    
                    # Convert to actual amount
                    multiplier = {'k': 1000, 'm': 1000000, 'b': 1000000000}.get(unit, 1)
                    actual_amount = amount * multiplier
                    
                    if actual_amount >= 5000000:  # >= $5M funding
                        score += 15
                        break
                    elif actual_amount >= 1000000:  # >= $1M funding
                        score += 10
                        break
            
            # Valuation metrics
            valuation_metrics = financial_metrics.get('valuation_metrics', [])
            if valuation_metrics:
                score += 10  # Has valuation
            
            # Business model sustainability
            business_insights = nlp_analysis.get('business_insights', {})
            revenue_model = business_insights.get('revenue_model')
            
            if revenue_model in ['subscription', 'saas']:
                score += 15  # Recurring revenue model
            elif revenue_model in ['transaction', 'marketplace']:
                score += 10  # Scalable model
            
            # Financial document quality
            if 'financial_model' in document_content.get('document_classification', {}).get('document_type', ''):
                score += 10  # Has financial model document
            
            return min(score, 100.0)
            
        except Exception as e:
            logger.error(f"Financial score calculation error: {str(e)}")
            return 50.0
    
    async def _calculate_market_score(
        self, 
        nlp_analysis: Dict[str, Any], 
        document_content: Dict[str, Any]
    ) -> float:
        """Calculate market opportunity score (0-100)"""
        score = 50.0  # Base score
        
        try:
            market_analysis = nlp_analysis.get('market_analysis', {})
            business_insights = nlp_analysis.get('business_insights', {})
            
            # Market size analysis
            market_size = market_analysis.get('market_size', [])
            if market_size:
                score += 15  # Has market size data
                
                for size_info in market_size:
                    amount = size_info.get('amount', '').replace(',', '')
                    unit = size_info.get('unit', '').lower()
                    
                    try:
                        amount_num = float(amount)
                        multiplier = {'k': 1000, 'm': 1000000, 'b': 1000000000}.get(unit, 1)
                        market_value = amount_num * multiplier
                        
                        if market_value >= 10000000000:  # >= $10B market
                            score += 20
                            break
                        elif market_value >= 1000000000:  # >= $1B market
                            score += 15
                            break
                        elif market_value >= 100000000:  # >= $100M market
                            score += 10
                            break
                    except (ValueError, TypeError):
                        continue
            
            # Competition analysis
            competitors = market_analysis.get('competitors', [])
            if competitors:
                if len(competitors) <= 3:
                    score += 15  # Low competition
                elif len(competitors) <= 6:
                    score += 10  # Moderate competition
                else:
                    score += 5   # High competition but market validation
            
            # Business model fit
            business_model = business_insights.get('business_model')
            if business_model in ['saas', 'marketplace', 'fintech']:
                score += 10  # High-growth potential models
            
            # Target market clarity
            target_market = business_insights.get('target_market', [])
            if target_market:
                score += 10  # Clear target market
            
            # Market trends and timing
            market_trends = market_analysis.get('market_trends', [])
            if market_trends:
                score += 10  # Market timing awareness
            
            # Technology trends alignment
            key_topics = nlp_analysis.get('key_topics', [])
            trending_topics = ['technology', 'ai', 'blockchain', 'fintech', 'healthtech']
            
            for topic in key_topics:
                if topic.get('topic') in trending_topics:
                    score += 5
                    break
            
            return min(score, 100.0)
            
        except Exception as e:
            logger.error(f"Market score calculation error: {str(e)}")
            return 50.0
    
    async def _calculate_team_score(
        self, 
        nlp_analysis: Dict[str, Any], 
        document_content: Dict[str, Any]
    ) -> float:
        """Calculate team strength score (0-100)"""
        score = 50.0  # Base score
        
        try:
            team_info = nlp_analysis.get('team_information', {})
            
            # Founder information
            founders = team_info.get('founders', [])
            if founders:
                score += 15  # Has founder information
                
                if len(founders) >= 2:
                    score += 10  # Co-founder team
                
                # Check for experience indicators
                for founder in founders:
                    context = founder.get('context', '').lower()
                    if any(exp in context for exp in ['experience', 'previous', 'former', 'ex-']):
                        score += 10  # Experience mentioned
                        break
            
            # Team size
            team_size = team_info.get('team_size')
            if team_size:
                if 5 <= team_size <= 20:
                    score += 15  # Optimal team size
                elif 2 <= team_size <= 50:
                    score += 10  # Reasonable team size
                elif team_size > 50:
                    score += 5   # Large team (could be good or concerning)
            
            # Key personnel
            key_personnel = team_info.get('key_personnel', [])
            if key_personnel:
                score += 10  # Has key personnel identified
            
            # Experience highlights
            experience_highlights = team_info.get('experience_highlights', [])
            if experience_highlights:
                score += 15  # Documented experience
            
            # Domain expertise indicators
            entities = nlp_analysis.get('entities', {})
            organizations = entities.get('organizations', [])
            
            # Check for prestigious company mentions
            prestigious_companies = [
                'google', 'microsoft', 'apple', 'amazon', 'facebook', 'meta',
                'tesla', 'uber', 'airbnb', 'stripe', 'salesforce'
            ]
            
            for org in organizations:
                org_name = org.get('text', '').lower()
                if any(company in org_name for company in prestigious_companies):
                    score += 10  # Prestigious background
                    break
            
            return min(score, 100.0)
            
        except Exception as e:
            logger.error(f"Team score calculation error: {str(e)}")
            return 50.0
    
    async def _calculate_product_score(
        self, 
        nlp_analysis: Dict[str, Any], 
        document_content: Dict[str, Any]
    ) -> float:
        """Calculate product-market fit and product quality score (0-100)"""
        score = 50.0  # Base score
        
        try:
            business_insights = nlp_analysis.get('business_insights', {})
            key_topics = nlp_analysis.get('key_topics', [])
            
            # Product/solution clarity
            value_proposition = business_insights.get('value_proposition', [])
            if value_proposition:
                score += 15  # Clear value proposition
            
            # Competitive advantages
            competitive_advantages = business_insights.get('competitive_advantages', [])
            if competitive_advantages:
                score += 15  # Identified competitive advantages
            
            # Technology innovation
            tech_topics = [topic for topic in key_topics if topic.get('topic') == 'technology']
            if tech_topics:
                tech_score = tech_topics[0].get('relevance_score', 0)
                score += tech_score * 20  # Up to 20 points for tech innovation
            
            # Product development stage indicators
            text_analysis = nlp_analysis.get('text_analysis', {})
            full_text = document_content.get('extracted_content', {}).get('full_text', '').lower()
            
            # Look for product development indicators
            development_indicators = {
                'mvp': 10,
                'prototype': 8,
                'beta': 12,
                'launched': 15,
                'customers': 15,
                'users': 12,
                'traction': 15
            }
            
            for indicator, points in development_indicators.items():
                if indicator in full_text:
                    score += points
                    break  # Only count the highest indicator
            
            # Customer validation
            if any(word in full_text for word in ['customer feedback', 'user feedback', 'testimonial']):
                score += 10
            
            # Scalability indicators
            if any(word in full_text for word in ['scalable', 'scale', 'growth', 'expand']):
                score += 10
            
            return min(score, 100.0)
            
        except Exception as e:
            logger.error(f"Product score calculation error: {str(e)}")
            return 50.0
    
    async def _assess_risk_factors(
        self, 
        nlp_analysis: Dict[str, Any], 
        document_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess various risk factors and calculate overall risk score"""
        risk_assessment = {
            'market_risk': 50,
            'financial_risk': 50,
            'operational_risk': 50,
            'regulatory_risk': 50,
            'technology_risk': 50,
            'team_risk': 50,
            'overall_risk_score': 50,
            'risk_factors': []
        }
        
        try:
            identified_risks = nlp_analysis.get('risk_factors', [])
            
            # Categorize and score risks
            risk_scores = {
                'market': [],
                'financial': [],
                'operational': [],
                'regulatory': [],
                'technology': [],
                'team': []
            }
            
            for risk in identified_risks:
                category = risk.get('category', 'operational')
                severity = risk.get('severity', 'medium')
                
                # Convert severity to score (lower is better for risk)
                severity_scores = {'low': 20, 'medium': 50, 'high': 80, 'critical': 95}
                risk_score = severity_scores.get(severity, 50)
                
                if category in risk_scores:
                    risk_scores[category].append(risk_score)
                
                risk_assessment['risk_factors'].append({
                    'category': category,
                    'description': risk.get('context', ''),
                    'severity': severity,
                    'score': risk_score
                })
            
            # Calculate category risk scores
            for category, scores in risk_scores.items():
                if scores:
                    avg_score = sum(scores) / len(scores)
                    risk_assessment[f'{category}_risk'] = min(avg_score, 100)
            
            # Calculate overall risk score
            category_risks = [
                risk_assessment['market_risk'],
                risk_assessment['financial_risk'],
                risk_assessment['operational_risk'],
                risk_assessment['regulatory_risk'],
                risk_assessment['technology_risk'],
                risk_assessment['team_risk']
            ]
            
            risk_assessment['overall_risk_score'] = sum(category_risks) / len(category_risks)
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Risk assessment error: {str(e)}")
            return risk_assessment
    
    def _calculate_confidence_interval(self, score: float, confidence: float) -> Tuple[float, float]:
        """Calculate confidence interval for the score"""
        # Simple confidence interval calculation
        margin = (1 - confidence) * 20  # Max margin of ±20 points
        
        lower_bound = max(0, score - margin)
        upper_bound = min(100, score + margin)
        
        return (round(lower_bound, 2), round(upper_bound, 2))
    
    def _generate_recommendation(self, overall_score: float) -> str:
        """Generate investment recommendation based on overall score"""
        if overall_score >= self.recommendation_thresholds['strong_buy']:
            return 'strong_buy'
        elif overall_score >= self.recommendation_thresholds['buy']:
            return 'buy'
        elif overall_score >= self.recommendation_thresholds['hold']:
            return 'hold'
        else:
            return 'pass'
    
    def _get_financial_reasoning(self, nlp_analysis: Dict[str, Any], score: float) -> str:
        """Generate reasoning for financial score"""
        financial_metrics = nlp_analysis.get('financial_metrics', {})
        
        reasons = []
        
        if financial_metrics.get('revenue_metrics'):
            reasons.append("Revenue data available")
        
        if financial_metrics.get('funding_metrics'):
            reasons.append("Funding information present")
        
        if financial_metrics.get('valuation_metrics'):
            reasons.append("Valuation metrics identified")
        
        business_model = nlp_analysis.get('business_insights', {}).get('business_model')
        if business_model:
            reasons.append(f"Business model: {business_model}")
        
        if score >= 70:
            return f"Strong financial indicators: {', '.join(reasons)}"
        elif score >= 50:
            return f"Moderate financial health: {', '.join(reasons) if reasons else 'Limited financial data'}"
        else:
            return f"Financial concerns: {', '.join(reasons) if reasons else 'Insufficient financial information'}"
    
    def _get_market_reasoning(self, nlp_analysis: Dict[str, Any], score: float) -> str:
        """Generate reasoning for market score"""
        market_analysis = nlp_analysis.get('market_analysis', {})
        
        reasons = []
        
        if market_analysis.get('market_size'):
            reasons.append("Market size data available")
        
        competitors = market_analysis.get('competitors', [])
        if competitors:
            reasons.append(f"{len(competitors)} competitors identified")
        
        if score >= 70:
            return f"Strong market opportunity: {', '.join(reasons)}"
        elif score >= 50:
            return f"Moderate market potential: {', '.join(reasons) if reasons else 'Limited market data'}"
        else:
            return f"Market concerns: {', '.join(reasons) if reasons else 'Insufficient market information'}"
    
    def _get_team_reasoning(self, nlp_analysis: Dict[str, Any], score: float) -> str:
        """Generate reasoning for team score"""
        team_info = nlp_analysis.get('team_information', {})
        
        reasons = []
        
        founders = team_info.get('founders', [])
        if founders:
            reasons.append(f"{len(founders)} founder(s) identified")
        
        team_size = team_info.get('team_size')
        if team_size:
            reasons.append(f"Team size: {team_size}")
        
        if score >= 70:
            return f"Strong team: {', '.join(reasons)}"
        elif score >= 50:
            return f"Adequate team: {', '.join(reasons) if reasons else 'Limited team information'}"
        else:
            return f"Team concerns: {', '.join(reasons) if reasons else 'Insufficient team information'}"
    
    def _get_product_reasoning(self, nlp_analysis: Dict[str, Any], score: float) -> str:
        """Generate reasoning for product score"""
        business_insights = nlp_analysis.get('business_insights', {})
        
        reasons = []
        
        if business_insights.get('value_proposition'):
            reasons.append("Value proposition identified")
        
        if business_insights.get('competitive_advantages'):
            reasons.append("Competitive advantages noted")
        
        if score >= 70:
            return f"Strong product-market fit: {', '.join(reasons)}"
        elif score >= 50:
            return f"Moderate product potential: {', '.join(reasons) if reasons else 'Basic product information'}"
        else:
            return f"Product concerns: {', '.join(reasons) if reasons else 'Limited product information'}"
    
    def _identify_key_strengths(self, nlp_analysis: Dict[str, Any], scores: Dict[str, float]) -> List[str]:
        """Identify key strengths based on analysis and scores"""
        strengths = []
        
        # High-scoring dimensions
        for dimension, score in scores.items():
            if score >= 75:
                strengths.append(f"Strong {dimension} performance ({score:.1f}/100)")
        
        # Specific strengths from analysis
        financial_metrics = nlp_analysis.get('financial_metrics', {})
        if financial_metrics.get('revenue_metrics'):
            strengths.append("Revenue generation demonstrated")
        
        if financial_metrics.get('funding_metrics'):
            strengths.append("Secured funding")
        
        market_analysis = nlp_analysis.get('market_analysis', {})
        if market_analysis.get('market_size'):
            strengths.append("Large market opportunity")
        
        team_info = nlp_analysis.get('team_information', {})
        if len(team_info.get('founders', [])) >= 2:
            strengths.append("Co-founder team")
        
        return strengths[:5]  # Top 5 strengths
    
    def _identify_key_concerns(self, risk_factors: Dict[str, Any], scores: Dict[str, float]) -> List[str]:
        """Identify key concerns based on risk assessment and scores"""
        concerns = []
        
        # Low-scoring dimensions
        for dimension, score in scores.items():
            if score <= 40:
                concerns.append(f"Weak {dimension} indicators ({score:.1f}/100)")
        
        # High-risk categories
        risk_categories = ['market_risk', 'financial_risk', 'operational_risk', 'regulatory_risk', 'technology_risk', 'team_risk']
        for category in risk_categories:
            risk_score = risk_factors.get(category, 50)
            if risk_score >= 70:
                category_name = category.replace('_risk', '')
                concerns.append(f"High {category_name} risk ({risk_score:.1f}/100)")
        
        # Specific risk factors
        identified_risks = risk_factors.get('risk_factors', [])
        high_severity_risks = [risk for risk in identified_risks if risk.get('severity') in ['high', 'critical']]
        
        for risk in high_severity_risks[:3]:  # Top 3 high-severity risks
            concerns.append(f"{risk.get('category', 'General')} risk: {risk.get('description', '')[:50]}...")
        
        return concerns[:5]  # Top 5 concerns


# Global scoring engine instance
scoring_engine = ScoringEngine()
