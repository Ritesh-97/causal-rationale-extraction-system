"""
Main explanation generation module
"""

from typing import List, Dict, Any, Optional
from .llm_generator import LLMGenerator
from ..retrieval.retrieval_pipeline import RetrievalPipeline
from ..causal_analysis.causal_analyzer import CausalAnalyzer


class ExplanationGenerator:
    """Generate evidence-based causal explanations"""
    
    def __init__(
        self,
        retrieval_pipeline: RetrievalPipeline,
        causal_analyzer: CausalAnalyzer,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4"
    ):
        self.retrieval_pipeline = retrieval_pipeline
        self.causal_analyzer = causal_analyzer
        self.llm_generator = LLMGenerator(
            provider=llm_provider,
            model=llm_model
        )
    
    def generate_explanation(
        self,
        query: str,
        top_k: int = 10,
        event_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate evidence-based causal explanation for a query.
        
        Args:
            query: Natural language query
            top_k: Number of top evidence spans to use
            event_type: Optional event type to focus on
        
        Returns:
            Dictionary with explanation, evidence, and citations
        """
        # Retrieve relevant spans
        retrieved_spans = self.retrieval_pipeline.retrieve(
            query=query,
            top_k=20,
            rerank_top_k=top_k
        )
        
        # Analyze causal patterns
        analyzed_spans = self.causal_analyzer.analyze_causal_spans(
            spans=retrieved_spans,
            query=query,
            event_type=event_type,
            top_k=top_k
        )
        
        # Generate explanation with LLM
        explanation_result = self.llm_generator.generate_with_citations(
            query=query,
            evidence=analyzed_spans
        )
        
        return {
            'query': query,
            'explanation': explanation_result['explanation'],
            'evidence': analyzed_spans,
            'citations': explanation_result['citations'],
            'evidence_count': len(analyzed_spans),
            'metadata': {
                'top_k': top_k,
                'event_type': event_type
            }
        }
    
    def generate_structured_explanation(
        self,
        query: str,
        top_k: int = 10,
        event_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured explanation with components.
        
        Args:
            query: Natural language query
            top_k: Number of top evidence spans to use
            event_type: Optional event type to focus on
        
        Returns:
            Structured explanation dictionary
        """
        # Generate base explanation
        result = self.generate_explanation(query, top_k=top_k, event_type=event_type)
        
        # Structure the explanation
        structured = {
            'query': query,
            'summary': self._extract_summary(result['explanation']),
            'key_factors': self._extract_key_factors(result['explanation']),
            'causal_mechanisms': self._extract_causal_mechanisms(result['explanation']),
            'evidence': result['evidence'],
            'citations': result['citations'],
            'evidence_count': result['evidence_count'],
            'full_explanation': result['explanation']
        }
        
        return structured
    
    def _extract_summary(self, explanation: str) -> str:
        """Extract summary from explanation"""
        # Simple extraction: first sentence or first paragraph
        sentences = explanation.split('.')
        if sentences:
            return sentences[0].strip() + '.'
        return explanation[:200] + '...' if len(explanation) > 200 else explanation
    
    def _extract_key_factors(self, explanation: str) -> List[str]:
        """Extract key factors from explanation"""
        # Simple extraction: look for numbered or bulleted lists
        import re
        
        factors = []
        
        # Look for numbered lists
        pattern = r'\d+[\.\)]\s*([^\n]+)'
        matches = re.findall(pattern, explanation)
        factors.extend([m.strip() for m in matches])
        
        # Look for bullet points
        pattern = r'[-•]\s*([^\n]+)'
        matches = re.findall(pattern, explanation)
        factors.extend([m.strip() for m in matches])
        
        # If no structured format, extract key sentences
        if not factors:
            sentences = explanation.split('.')
            factors = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]
        
        return factors[:5]  # Limit to top 5
    
    def _extract_causal_mechanisms(self, explanation: str) -> List[str]:
        """Extract causal mechanisms from explanation"""
        # Look for causal language
        import re
        
        mechanisms = []
        
        # Patterns indicating causal mechanisms
        patterns = [
            r'because\s+([^\.]+)',
            r'due\s+to\s+([^\.]+)',
            r'led\s+to\s+([^\.]+)',
            r'caused\s+([^\.]+)',
            r'resulted\s+in\s+([^\.]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, explanation, re.IGNORECASE)
            mechanisms.extend([m.strip() for m in matches])
        
        return mechanisms[:5]  # Limit to top 5

