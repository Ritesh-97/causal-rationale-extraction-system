"""
Query simulation framework for generating test queries
"""

from typing import List, Dict, Any, Optional
import os
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
import json


class QuerySimulator:
    """Generate simulated queries using LLMs"""
    
    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        # Get provider and model from environment if not provided
        if provider is None:
            provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        if model is None:
            if provider == "gemini":
                model = os.getenv("DEFAULT_LLM_MODEL", "gemini-2.0-flash")
            elif provider == "openai":
                model = os.getenv("DEFAULT_LLM_MODEL", "gpt-4")
            elif provider == "anthropic":
                model = os.getenv("DEFAULT_LLM_MODEL", "claude-3-opus-20240229")
            else:
                model = os.getenv("DEFAULT_LLM_MODEL", "gpt-4")
        
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
    
    def generate_queries(
        self,
        event_types: List[str],
        num_queries_per_type: int = 10,
        query_categories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate queries for different event types and categories.
        
        Args:
            event_types: List of event types (e.g., ['escalation', 'refund', 'churn'])
            num_queries_per_type: Number of queries to generate per event type
            query_categories: Optional list of query categories
        
        Returns:
            List of generated queries with metadata
        """
        all_queries = []
        
        for event_type in event_types:
            queries = self._generate_queries_for_event(
                event_type=event_type,
                num_queries=num_queries_per_type,
                categories=query_categories
            )
            all_queries.extend(queries)
        
        return all_queries
    
    def _generate_queries_for_event(
        self,
        event_type: str,
        num_queries: int = 10,
        categories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Generate queries for a specific event type"""
        if categories is None:
            categories = [
                'causal_inquiry',
                'pattern_analysis',
                'specific_event',
                'agent_behavior',
                'product_feedback'
            ]
        
        queries = []
        queries_per_category = num_queries // len(categories)
        
        for category in categories:
            category_queries = self._generate_category_queries(
                event_type=event_type,
                category=category,
                num_queries=queries_per_category
            )
            queries.extend(category_queries)
        
        return queries
    
    def _generate_category_queries(
        self,
        event_type: str,
        category: str,
        num_queries: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate queries for a specific category"""
        prompt = self._build_query_generation_prompt(event_type, category, num_queries)
        
        response = self._generate(prompt)
        
        # Parse response
        queries = self._parse_query_response(response, event_type, category)
        
        return queries
    
    def _build_query_generation_prompt(
        self,
        event_type: str,
        category: str,
        num_queries: int
    ) -> str:
        """Build prompt for query generation"""
        category_descriptions = {
            'causal_inquiry': 'queries asking why events happen (e.g., "Why are escalations happening?")',
            'pattern_analysis': 'queries asking about patterns (e.g., "What patterns lead to refunds?")',
            'specific_event': 'queries about specific calls or events',
            'agent_behavior': 'queries about agent behavior and performance',
            'product_feedback': 'queries about product feedback and customer satisfaction'
        }
        
        category_desc = category_descriptions.get(category, category)
        
        prompt = f"""Generate {num_queries} natural language queries for a customer service analytics system.

Event Type: {event_type}
Category: {category} ({category_desc})

Requirements:
1. Queries should be realistic and relevant to customer service conversations
2. Queries should ask about causal relationships between dialogue patterns and {event_type} events
3. Queries should be diverse in phrasing and complexity
4. Queries should be suitable for an agent coach or analyst perspective

Generate {num_queries} queries, one per line, in the following format:
1. [query text]
2. [query text]
...

Queries:"""
        
        return prompt
    
    def _generate(self, prompt: str) -> str:
        """Generate response from LLM"""
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates realistic queries for customer service analytics."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
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
            full_prompt = "You are a helpful assistant that generates realistic queries for customer service analytics.\n\n" + prompt
            
            model = self.client.GenerativeModel(self.model)
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.8,
                    "max_output_tokens": 1000,
                }
            )
            return response.text
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _parse_query_response(
        self,
        response: str,
        event_type: str,
        category: str
    ) -> List[Dict[str, Any]]:
        """Parse LLM response into query dictionaries"""
        queries = []
        lines = response.strip().split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Remove numbering
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove prefix
                query_text = line.split('.', 1)[-1].strip()
                if query_text.startswith('-'):
                    query_text = query_text[1:].strip()
                
                if query_text:
                    queries.append({
                        'query': query_text,
                        'event_type': event_type,
                        'category': category,
                        'query_id': f"{event_type}_{category}_{i}"
                    })
        
        return queries
    
    def generate_followup_queries(
        self,
        initial_query: str,
        initial_response: str,
        num_followups: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate follow-up queries based on initial query and response.
        
        Args:
            initial_query: Initial query text
            initial_response: Response to initial query
            num_followups: Number of follow-up queries to generate
        
        Returns:
            List of follow-up queries
        """
        prompt = f"""Generate {num_followups} natural language follow-up queries based on the following conversation:

Initial Query: {initial_query}
Response: {initial_response[:500]}...

Requirements:
1. Follow-up queries should be contextually linked to the initial query and response
2. Follow-up queries should ask for clarification, additional details, or related information
3. Follow-up queries should be realistic and natural
4. Follow-up queries should use pronouns or references to previous context when appropriate

Generate {num_followups} follow-up queries, one per line:
1. [query text]
2. [query text]
...

Follow-up Queries:"""
        
        response = self._generate(prompt)
        
        # Parse response
        followups = []
        lines = response.strip().split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                query_text = line.split('.', 1)[-1].strip()
                if query_text.startswith('-'):
                    query_text = query_text[1:].strip()
                
                if query_text:
                    followups.append({
                        'query': query_text,
                        'category': 'followup',
                        'query_id': f"followup_{i}",
                        'is_followup': True
                    })
        
        return followups

