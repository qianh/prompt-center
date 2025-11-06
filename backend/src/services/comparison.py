"""
Comparison service for managing prompt comparisons.
"""

import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import uuid

from src.crud import comparison_crud, prompt_version_crud, llm_config_crud
from src.models.comparison import Comparison
from src.models.prompt_version import PromptVersion
from src.models.llm_config import LLMConfig
from src.services.llm import llm_service
from src.schemas.comparison import ComparisonCreate


class ComparisonService:
    """Service for managing prompt comparisons."""
    
    async def create_same_llm_comparison(
        self,
        db: Session,
        *,
        comparison_data: ComparisonCreate,
        prompt_version_ids: List[str]
    ) -> Comparison:
        """Create a comparison using the same LLM for multiple prompt versions."""
        
        # Validate prompt versions exist
        prompt_versions = []
        for version_id in prompt_version_ids:
            version = prompt_version_crud.get(db=db, version_id=version_id)
            if not version:
                raise ValueError(f"Prompt version {version_id} not found")
            prompt_versions.append(version)
        
        # Validate LLM config exists
        llm_config = llm_config_crud.get(db=db, config_id=comparison_data.llm_config_id)
        if not llm_config:
            raise ValueError(f"LLM config {comparison_data.llm_config_id} not found")
        
        # Create comparison record
        comparison = comparison_crud.create(db=db, obj_in=comparison_data)
        
        # Execute comparison
        results = await llm_service.compare_prompt_versions(
            db=db,
            comparison=comparison,
            prompt_versions=prompt_versions
        )
        
        return comparison
    
    async def create_different_llm_comparison(
        self,
        db: Session,
        *,
        prompt_version_id: str,
        llm_config_ids: List[str],
        input_text: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Comparison:
        """Create a comparison using different LLMs for the same prompt version."""
        
        # Validate prompt version exists
        prompt_version = prompt_version_crud.get(db=db, version_id=prompt_version_id)
        if not prompt_version:
            raise ValueError(f"Prompt version {prompt_version_id} not found")
        
        # Validate LLM configs exist
        llm_configs = []
        for config_id in llm_config_ids:
            config = llm_config_crud.get(db=db, config_id=config_id)
            if not config:
                raise ValueError(f"LLM config {config_id} not found")
            llm_configs.append(config)
        
        # Create comparison record (use first LLM config as reference)
        comparison_data = ComparisonCreate(
            name=name or f"Multi-LLM Comparison for {prompt_version.version_number}",
            description=description or f"Comparing {len(llm_configs)} LLMs on the same prompt",
            type="different_llm",
            input_text=input_text,
            llm_config_id=llm_configs[0].id,  # Reference config
            save_snapshot=True
        )
        
        comparison = comparison_crud.create(db=db, obj_in=comparison_data)
        
        # Execute comparison with different LLMs
        results = []
        for llm_config in llm_configs:
            result = await llm_service.call_llm(input_text, llm_config)
            
            # Store result
            from src.models.comparison_prompt_version import ComparisonPromptVersion
            comparison_prompt_version = ComparisonPromptVersion(
                comparison_id=comparison.id,
                prompt_version_id=prompt_version_id,
                result=json.dumps(result) if result else None,
                execution_time_ms=result["execution_time_ms"],
                tokens_used=result["tokens_used"],
                error_message=result.get("error")
            )
            
            db.add(comparison_prompt_version)
            
            results.append({
                "llm_config_id": llm_config.id,
                "llm_provider": llm_config.provider,
                "llm_model": llm_config.model,
                "result": result
            })
        
        db.commit()
        
        # Update comparison statistics
        successful_results = [r for r in results if r["result"]["success"]]
        total_executions = len(results)
        successful_executions = len(successful_results)
        
        if successful_executions > 0:
            avg_execution_time = sum(r["result"]["execution_time_ms"] for r in successful_results) / successful_executions
            total_tokens = sum(r["result"]["tokens_used"] for r in successful_results)
        else:
            avg_execution_time = 0
            total_tokens = 0
        
        comparison.successful_executions = successful_executions
        comparison.total_executions = total_executions
        comparison.average_execution_time_ms = int(avg_execution_time)
        comparison.total_tokens_used = total_tokens
        comparison.results = [r["result"] for r in results]
        
        db.commit()
        
        return comparison
    
    def get_comparison_summary(
        self,
        db: Session,
        comparison_id: str
    ) -> Dict[str, Any]:
        """Get a summary of comparison results."""
        
        comparison = comparison_crud.get(db=db, comparison_id=comparison_id)
        if not comparison:
            raise ValueError("Comparison not found")
        
        results = llm_service.get_comparison_results(db, comparison_id)
        
        # Calculate statistics
        successful_results = [r for r in results if r["success"]]
        
        summary = {
            "comparison_id": comparison.id,
            "name": comparison.name,
            "type": comparison.type,
            "input_text": comparison.input_text,
            "total_executions": len(results),
            "successful_executions": len(successful_results),
            "success_rate": len(successful_results) / len(results) if results else 0,
            "average_execution_time_ms": comparison.average_execution_time_ms,
            "total_tokens_used": comparison.total_tokens_used,
            "results": results
        }
        
        # Add performance analysis
        if successful_results:
            execution_times = [r["execution_time_ms"] for r in successful_results]
            token_counts = [r["tokens_used"] for r in successful_results]
            
            summary.update({
                "performance": {
                    "fastest_execution_ms": min(execution_times),
                    "slowest_execution_ms": max(execution_times),
                    "average_tokens_per_execution": sum(token_counts) / len(token_counts),
                    "total_tokens_per_second": (sum(token_counts) / sum(execution_times)) * 1000 if sum(execution_times) > 0 else 0
                }
            })
        
        return summary
    
    def compare_results_quality(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare the quality of different results."""
        
        successful_results = [r for r in results if r["success"]]
        
        if len(successful_results) < 2:
            return {"error": "Need at least 2 successful results for quality comparison"}
        
        # Basic quality metrics
        quality_metrics = {}
        
        for i, result in enumerate(successful_results):
            content = result.get("execution_result", {}).get("content", "")
            
            metrics = {
                "version_number": result["version_number"],
                "content_length": len(content),
                "word_count": len(content.split()),
                "sentence_count": content.count('.') + content.count('!') + content.count('?'),
                "execution_time_ms": result["execution_time_ms"],
                "tokens_used": result["tokens_used"],
                "performance_score": 0  # Will be calculated
            }
            
            # Calculate performance score (higher is better)
            # Balance between speed, efficiency, and content length
            time_score = 1000 / (result["execution_time_ms"] + 1)  # Faster is better
            token_score = 100 / (result["tokens_used"] + 1)  # More efficient is better
            content_score = min(len(content) / 100, 10)  # Longer content up to a point
            
            metrics["performance_score"] = (time_score + token_score + content_score) / 3
            
            quality_metrics[f"result_{i}"] = metrics
        
        # Find best performer
        best_result = max(quality_metrics.items(), key=lambda x: x[1]["performance_score"])
        
        return {
            "quality_metrics": quality_metrics,
            "best_performer": {
                "key": best_result[0],
                "metrics": best_result[1]
            },
            "recommendation": f"Version {best_result[1]['version_number']} performed best with a score of {best_result[1]['performance_score']:.2f}"
        }


# Create a singleton instance
comparison_service = ComparisonService()
