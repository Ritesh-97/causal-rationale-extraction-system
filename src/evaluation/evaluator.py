"""
Main evaluation framework
"""

from typing import List, Dict, Any, Optional
import pandas as pd
from .metrics import EvaluationMetrics
from .baselines import KeywordSearchBaseline, SimpleRAGBaseline, RuleBasedBaseline
from ..system import System


class Evaluator:
    """Main evaluation framework"""
    
    def __init__(self, system: Optional[System] = None):
        self.system = system or System()
        self.metrics = EvaluationMetrics()
        self.baselines = {
            'keyword_search': KeywordSearchBaseline(),
            'simple_rag': SimpleRAGBaseline(),
            'rule_based': RuleBasedBaseline()
        }
    
    def evaluate_system(
        self,
        dataset: pd.DataFrame,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate system performance on a dataset.
        
        Args:
            dataset: DataFrame with queries and system outputs
            output_path: Optional path to save evaluation results
        
        Returns:
            Dictionary with evaluation results
        """
        results = {
            'response_quality': [],
            'evidence_quality': [],
            'explanation_quality': [],
            'conversational_coherence': []
        }
        
        for _, row in dataset.iterrows():
            query = row['Query']
            system_output = row['System_Output']
            query_id = row.get('Query_Id', 'unknown')
            
            # Get evidence if available
            evidence = []  # Would need to retrieve from system
            
            # Evaluate response quality
            response_metrics = self.metrics.evaluate_response_quality(system_output)
            results['response_quality'].append({
                'query_id': query_id,
                'query': query,
                **response_metrics
            })
            
            # Evaluate evidence quality
            if evidence:
                evidence_metrics = self.metrics.evaluate_evidence_quality(evidence, query)
                results['evidence_quality'].append({
                    'query_id': query_id,
                    'query': query,
                    **evidence_metrics
                })
            
            # Evaluate explanation quality
            explanation_metrics = self.metrics.evaluate_causal_explanation_quality(
                system_output,
                evidence,
                query
            )
            results['explanation_quality'].append({
                'query_id': query_id,
                'query': query,
                **explanation_metrics
            })
        
        # Aggregate results
        aggregated = self._aggregate_results(results)
        
        # Save if path provided
        if output_path:
            self._save_results(aggregated, output_path)
        
        return aggregated
    
    def compare_with_baselines(
        self,
        queries: List[str],
        spans: List[Dict[str, Any]],
        event_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare system with baseline methods.
        
        Args:
            queries: List of test queries
            spans: List of dialogue spans
            event_types: Optional list of event types
        
        Returns:
            Dictionary with comparison results
        """
        comparison_results = {}
        
        # Evaluate each baseline
        for baseline_name, baseline in self.baselines.items():
            baseline_results = []
            
            for query in queries:
                # Get baseline results
                if baseline_name == 'rule_based':
                    event_type = event_types[0] if event_types else None
                    baseline_spans = baseline.search(query, spans, event_type=event_type)
                else:
                    baseline_spans = baseline.search(query, spans)
                
                baseline_response = baseline.generate_response(query, baseline_spans)
                
                # Evaluate baseline
                response_metrics = self.metrics.evaluate_response_quality(baseline_response)
                evidence_metrics = self.metrics.evaluate_evidence_quality(baseline_spans, query)
                
                baseline_results.append({
                    'query': query,
                    'response': baseline_response,
                    **response_metrics,
                    **evidence_metrics
                })
            
            comparison_results[baseline_name] = baseline_results
        
        # Evaluate system
        system_results = []
        for query in queries:
            try:
                result = self.system.process_query(query)
                system_response = result.get('response', '')
                system_evidence = result.get('evidence', [])
                
                response_metrics = self.metrics.evaluate_response_quality(system_response)
                evidence_metrics = self.metrics.evaluate_evidence_quality(system_evidence, query)
                
                system_results.append({
                    'query': query,
                    'response': system_response,
                    **response_metrics,
                    **evidence_metrics
                })
            except Exception as e:
                print(f"Error evaluating system for query: {e}")
                continue
        
        comparison_results['system'] = system_results
        
        # Aggregate comparison
        aggregated = self._aggregate_comparison(comparison_results)
        
        return aggregated
    
    def ablation_study(
        self,
        queries: List[str],
        components: List[str] = ['retrieval', 'reranking', 'causal_analysis', 'llm']
    ) -> Dict[str, Any]:
        """
        Perform ablation study by removing components.
        
        Args:
            queries: List of test queries
            components: List of components to ablate
        
        Returns:
            Dictionary with ablation study results
        """
        ablation_results = {}
        
        # Full system
        full_results = []
        for query in queries:
            try:
                result = self.system.process_query(query)
                full_results.append({
                    'query': query,
                    'response': result.get('response', ''),
                    'evidence_count': len(result.get('evidence', []))
                })
            except Exception as e:
                print(f"Error in full system: {e}")
                continue
        
        ablation_results['full_system'] = full_results
        
        # Ablate each component
        for component in components:
            # Create system without component
            ablated_system = self._create_ablated_system(component)
            
            ablated_results = []
            for query in queries:
                try:
                    result = ablated_system.process_query(query)
                    ablated_results.append({
                        'query': query,
                        'response': result.get('response', ''),
                        'evidence_count': len(result.get('evidence', []))
                    })
                except Exception as e:
                    print(f"Error in ablated system ({component}): {e}")
                    continue
            
            ablation_results[f'without_{component}'] = ablated_results
        
        # Compare results
        comparison = self._compare_ablation_results(ablation_results)
        
        return {
            'ablation_results': ablation_results,
            'comparison': comparison
        }
    
    def _aggregate_results(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Aggregate evaluation results"""
        aggregated = {}
        
        for metric_type, metric_list in results.items():
            if not metric_list:
                continue
            
            # Calculate averages
            df = pd.DataFrame(metric_list)
            aggregated[metric_type] = {
                'mean': df.mean().to_dict(),
                'std': df.std().to_dict(),
                'min': df.min().to_dict(),
                'max': df.max().to_dict()
            }
        
        return aggregated
    
    def _aggregate_comparison(self, comparison_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Aggregate comparison results"""
        aggregated = {}
        
        for method, results in comparison_results.items():
            if not results:
                continue
            
            df = pd.DataFrame(results)
            aggregated[method] = {
                'mean': df.mean().to_dict(),
                'std': df.std().to_dict()
            }
        
        return aggregated
    
    def _create_ablated_system(self, component: str) -> System:
        """Create system with component ablated"""
        # This would require modifying system initialization
        # For now, return full system (would need implementation)
        return self.system
    
    def _compare_ablation_results(self, ablation_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Compare ablation study results"""
        comparison = {}
        
        full_results = ablation_results.get('full_system', [])
        if not full_results:
            return comparison
        
        full_df = pd.DataFrame(full_results)
        
        for key, results in ablation_results.items():
            if key == 'full_system':
                continue
            
            if not results:
                continue
            
            ablated_df = pd.DataFrame(results)
            
            # Compare metrics
            comparison[key] = {
                'response_length_diff': (
                    ablated_df['response'].str.len().mean() -
                    full_df['response'].str.len().mean()
                ),
                'evidence_count_diff': (
                    ablated_df['evidence_count'].mean() -
                    full_df['evidence_count'].mean()
                )
            }
        
        return comparison
    
    def _save_results(self, results: Dict[str, Any], output_path: str):
        """Save evaluation results"""
        import json
        from pathlib import Path
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

