"""
LLM-based explanation generation
"""

from typing import List, Dict, Any, Optional
import os
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai


class LLMGenerator:
    """Generate explanations using LLMs"""
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4",
        api_key: Optional[str] = None
    ):
        self.provider = provider
        self.model = model
        
        # Initialize client
        if provider == "openai":
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not provided")
            self.client = OpenAI(api_key=api_key)
        elif provider == "anthropic":
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key not provided")
            self.client = Anthropic(api_key=api_key)
        elif provider == "gemini":
            api_key = api_key or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("Gemini API key not provided")
            genai.configure(api_key=api_key)
            self.client = genai
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate_explanation(
        self,
        query: str,
        evidence: List[Dict[str, Any]],
        context: Optional[str] = None
    ) -> str:
        """
        Generate a causal explanation from evidence.
        
        Args:
            query: User query
            evidence: List of evidence spans
            context: Optional context from previous conversation
        
        Returns:
            Generated explanation text
        """
        # Format evidence
        evidence_text = self._format_evidence(evidence)
        
        # Build prompt
        prompt = self._build_explanation_prompt(query, evidence_text, context)
        
        # Generate response
        response = self._generate(prompt)
        
        return response
    
    def _format_evidence(self, evidence: List[Dict[str, Any]]) -> str:
        """Format evidence spans for prompt"""
        formatted = []
        
        for i, span in enumerate(evidence[:10], 1):  # Limit to top 10
            text = span.get('text', '')
            metadata = span.get('metadata', {})
            transcript_id = metadata.get('transcript_id', 'unknown')
            turn_ids = span.get('turn_ids', [])
            
            evidence_entry = f"[Evidence {i}]\n"
            evidence_entry += f"Transcript: {transcript_id}\n"
            if turn_ids:
                evidence_entry += f"Turns: {turn_ids[0]}-{turn_ids[-1]}\n"
            evidence_entry += f"Text: {text}\n"
            
            # Add scores if available
            if 'evidence_score' in span:
                evidence_entry += f"Relevance Score: {span['evidence_score']:.2f}\n"
            
            formatted.append(evidence_entry)
        
        return "\n".join(formatted)
    
    def _build_explanation_prompt(
        self,
        query: str,
        evidence_text: str,
        context: Optional[str] = None
    ) -> str:
        """Build prompt for explanation generation"""
        prompt = """You are an expert analyst specializing in understanding causal relationships in customer service conversations. Your task is to analyze dialogue evidence and provide clear, evidence-based causal explanations.

User Query: {query}

Evidence from Conversations:
{evidence}

Instructions:
1. Analyze the provided evidence to identify causal relationships between dialogue patterns and the business event mentioned in the query.
2. Provide a structured explanation that:
   - Clearly articulates the causal mechanisms
   - References specific evidence spans with citations
   - Explains how conversational elements led to the event
   - Identifies key contributing factors and behaviors
3. Be specific and data-driven, avoiding vague correlations.
4. Cite evidence using [Evidence N] format when referencing specific spans.

"""
        
        if context:
            prompt += f"Previous Context:\n{context}\n\n"
        
        prompt += "Provide your causal explanation:"
        
        return prompt.format(query=query, evidence=evidence_text)
    
    def _generate(self, prompt: str) -> str:
        """Generate response from LLM"""
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides evidence-based causal explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        elif self.provider == "gemini":
            # Build full prompt with system message
            full_prompt = "You are a helpful assistant that provides evidence-based causal explanations.\n\n" + prompt
            
            model = self.client.GenerativeModel(self.model)
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1000,
                }
            )
            return response.text
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def generate_with_citations(
        self,
        query: str,
        evidence: List[Dict[str, Any]],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate explanation with evidence citations.
        
        Args:
            query: User query
            evidence: List of evidence spans
            context: Optional context from previous conversation
        
        Returns:
            Dictionary with explanation and citations
        """
        explanation = self.generate_explanation(query, evidence, context)
        
        # Extract citations from explanation
        citations = self._extract_citations(explanation, evidence)
        
        return {
            'explanation': explanation,
            'citations': citations,
            'evidence_count': len(evidence)
        }
    
    def _extract_citations(
        self,
        explanation: str,
        evidence: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract evidence citations from explanation"""
        import re
        
        citations = []
        
        # Find references to evidence (e.g., [Evidence 1], [Evidence 2])
        pattern = r'\[Evidence\s+(\d+)\]'
        matches = re.finditer(pattern, explanation, re.IGNORECASE)
        
        for match in matches:
            evidence_num = int(match.group(1))
            if 1 <= evidence_num <= len(evidence):
                span = evidence[evidence_num - 1]
                citation = {
                    'evidence_number': evidence_num,
                    'span_id': span.get('span_id', 'unknown'),
                    'text': span.get('text', '')[:200],  # Truncate for display
                    'transcript_id': span.get('metadata', {}).get('transcript_id', 'unknown'),
                    'turn_ids': span.get('turn_ids', [])
                }
                citations.append(citation)
        
        return citations

