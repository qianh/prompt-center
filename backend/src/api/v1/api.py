"""
API v1 router for Prompt Center.
This implements the API endpoints with real database operations.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel as PydanticBaseModel
import json

from src.core.database import get_db
from src.crud import prompt_crud, prompt_version_crud, comparison_crud, llm_config_crud
from src.services import prompt_version_service, llm_service, comparison_service
from src.schemas import (
    PromptCreate, PromptUpdate, PromptResponse, PromptListResponse,
    PromptVersionCreate, PromptVersionUpdate, PromptVersionResponse,
    ComparisonCreate, ComparisonResponse, ComparisonListResponse,
    LLMConfigCreate, LLMConfigUpdate, LLMConfigResponse, LLMConfigListResponse
)

router = APIRouter(prefix="/api/v1", tags=["api"])


# Request models
class LLMTestRequest(PydanticBaseModel):
    llm_config_id: str
    prompt: str


# Prompts endpoints
@router.get("/prompts", response_model=PromptListResponse)
async def get_prompts(
    search: Optional[str] = Query(None, description="Search in title, description, and content"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db)
):
    """Get list of prompts with search and pagination."""
    # Parse tags
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    # Calculate skip
    skip = (page - 1) * limit
    
    # Get prompts
    prompts, total = prompt_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        tags=tag_list,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Calculate pagination
    total_pages = (total + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1
    
    return PromptListResponse(
        items=[
            PromptResponse(
                id=prompt.id,
                title=prompt.title,
                description=prompt.description,
                content=prompt.content,
                tags=prompt.tag_list,
                created_at=prompt.created_at,
                updated_at=prompt.updated_at
            ) for prompt in prompts
        ],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.post("/prompts", response_model=PromptResponse, status_code=201)
async def create_prompt(
    prompt_data: PromptCreate,
    db: Session = Depends(get_db)
):
    """Create a new prompt."""
    prompt = prompt_crud.create(db=db, obj_in=prompt_data)
    return PromptResponse(
        id=prompt.id,
        title=prompt.title,
        description=prompt.description,
        content=prompt.content,
        tags=prompt.tag_list,
        created_at=prompt.created_at,
        updated_at=prompt.updated_at
    )


@router.get("/prompts/{prompt_id}", response_model=PromptResponse)
async def get_prompt_by_id(
    prompt_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific prompt by ID."""
    prompt = prompt_crud.get(db=db, prompt_id=prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return PromptResponse(
        id=prompt.id,
        title=prompt.title,
        description=prompt.description,
        content=prompt.content,
        tags=prompt.tag_list,
        created_at=prompt.created_at,
        updated_at=prompt.updated_at
    )


@router.put("/prompts/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: str,
    prompt_data: PromptUpdate,
    db: Session = Depends(get_db)
):
    """Update a prompt."""
    prompt = prompt_crud.get(db=db, prompt_id=prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    updated_prompt = prompt_crud.update(db=db, db_obj=prompt, obj_in=prompt_data)
    return PromptResponse(
        id=updated_prompt.id,
        title=updated_prompt.title,
        description=updated_prompt.description,
        content=updated_prompt.content,
        tags=updated_prompt.tag_list,
        created_at=updated_prompt.created_at,
        updated_at=updated_prompt.updated_at
    )


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(
    prompt_id: str,
    db: Session = Depends(get_db)
):
    """Delete a prompt."""
    success = prompt_crud.delete(db=db, prompt_id=prompt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {"message": "Prompt deleted successfully"}


# Enhanced version management endpoints (specific routes first)
@router.get("/prompts/{prompt_id}/versions/history")
async def get_prompt_version_history(
    prompt_id: str,
    include_content: bool = Query(False, description="Include full content in history"),
    db: Session = Depends(get_db)
):
    """Get detailed version history for a prompt."""
    try:
        history = prompt_version_service.get_version_history(
            db=db,
            prompt_id=prompt_id,
            include_content=include_content
        )
        return {
            "prompt_id": prompt_id,
            "history": history,
            "total_versions": len(history)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/prompts/{prompt_id}/versions/latest")
async def get_latest_prompt_version(
    prompt_id: str,
    db: Session = Depends(get_db)
):
    """Get the latest version of a prompt."""
    try:
        latest_version = prompt_version_service.get_latest_version(
            db=db,
            prompt_id=prompt_id
        )
        if not latest_version:
            raise HTTPException(status_code=404, detail="No versions found")
        
        return PromptVersionResponse(
            id=latest_version.id,
            prompt_id=latest_version.prompt_id,
            version_number=latest_version.version_number,
            content=latest_version.content,
            change_notes=latest_version.change_notes,
            created_at=latest_version.created_at,
            updated_at=latest_version.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/prompts/{prompt_id}/versions/compare/detailed")
async def compare_prompt_versions_detailed(
    prompt_id: str,
    version_a: int = Query(..., description="First version number"),
    version_b: int = Query(..., description="Second version number"),
    include_diff: bool = Query(True, description="Include detailed diff"),
    db: Session = Depends(get_db)
):
    """Compare two versions with detailed analysis."""
    try:
        comparison = prompt_version_service.compare_versions_detailed(
            db=db,
            prompt_id=prompt_id,
            version_a=version_a,
            version_b=version_b,
            include_diff=include_diff
        )
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/prompts/{prompt_id}/versions/compare")
async def compare_prompt_versions(
    prompt_id: str,
    version_a: int = Query(..., description="First version number"),
    version_b: int = Query(..., description="Second version number"),
    db: Session = Depends(get_db)
):
    """Compare two versions of a prompt."""
    # Check if prompt exists
    prompt = prompt_crud.get(db=db, prompt_id=prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    comparison_result = prompt_version_crud.compare_versions(
        db=db,
        prompt_id=prompt_id,
        version_a=version_a,
        version_b=version_b
    )
    
    if not comparison_result:
        raise HTTPException(status_code=404, detail="One or both versions not found")
    
    return comparison_result


@router.get("/prompts/{prompt_id}/versions", response_model=List[PromptVersionResponse])
async def get_prompt_versions(
    prompt_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all versions of a prompt."""
    # Check if prompt exists
    prompt = prompt_crud.get(db=db, prompt_id=prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    skip = (page - 1) * limit
    versions = prompt_version_crud.get_by_prompt(
        db=db,
        prompt_id=prompt_id,
        skip=skip,
        limit=limit
    )
    
    return [PromptVersionResponse(
        id=version.id,
        prompt_id=version.prompt_id,
        version_number=version.version_number,
        content=version.content,
        change_notes=version.change_notes,
        created_at=version.created_at,
        updated_at=version.updated_at
    ) for version in versions]


@router.post("/prompts/{prompt_id}/versions", response_model=PromptVersionResponse, status_code=201)
async def create_prompt_version(
    prompt_id: str,
    version_data: PromptVersionCreate,
    db: Session = Depends(get_db)
):
    """Create a new version of a prompt."""
    # Check if prompt exists
    prompt = prompt_crud.get(db=db, prompt_id=prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    version = prompt_version_crud.create(db=db, obj_in=version_data, prompt_id=prompt_id)
    return PromptVersionResponse(
        id=version.id,
        prompt_id=version.prompt_id,
        version_number=version.version_number,
        content=version.content,
        change_notes=version.change_notes,
        created_at=version.created_at,
        updated_at=version.updated_at
    )


@router.get("/prompts/{prompt_id}/versions/{version_id}", response_model=PromptVersionResponse)
async def get_prompt_version(
    prompt_id: str,
    version_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific version of a prompt."""
    version = prompt_version_crud.get(db=db, version_id=version_id)
    if not version or version.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return PromptVersionResponse(
        id=version.id,
        prompt_id=version.prompt_id,
        version_number=version.version_number,
        content=version.content,
        change_notes=version.change_notes,
        created_at=version.created_at,
        updated_at=version.updated_at
    )


@router.put("/prompts/{prompt_id}/versions/{version_id}", response_model=PromptVersionResponse)
async def update_prompt_version(
    prompt_id: str,
    version_id: str,
    version_data: PromptVersionUpdate,
    db: Session = Depends(get_db)
):
    """Update a prompt version."""
    version = prompt_version_crud.get(db=db, version_id=version_id)
    if not version or version.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="Version not found")
    
    updated_version = prompt_version_crud.update(
        db=db,
        db_obj=version,
        obj_in=version_data
    )
    return PromptVersionResponse(
        id=updated_version.id,
        prompt_id=updated_version.prompt_id,
        version_number=updated_version.version_number,
        content=updated_version.content,
        change_notes=updated_version.change_notes,
        created_at=updated_version.created_at,
        updated_at=updated_version.updated_at
    )


@router.delete("/prompts/{prompt_id}/versions/{version_id}")
async def delete_prompt_version(
    prompt_id: str,
    version_id: str,
    db: Session = Depends(get_db)
):
    """Delete a prompt version."""
    version = prompt_version_crud.get(db=db, version_id=version_id)
    if not version or version.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="Version not found")
    
    success = prompt_version_crud.delete(db=db, version_id=version_id)
    if not success:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return {"message": "Version deleted successfully"}


@router.post("/prompts/{prompt_id}/versions/revert")
async def revert_prompt_to_version(
    prompt_id: str,
    version_number: int,
    change_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Revert a prompt to a specific version."""
    try:
        new_version = prompt_version_service.revert_to_version(
            db=db,
            prompt_id=prompt_id,
            version_number=version_number,
            change_notes=change_notes
        )
        return PromptVersionResponse(
            id=new_version.id,
            prompt_id=new_version.prompt_id,
            version_number=new_version.version_number,
            content=new_version.content,
            change_notes=new_version.change_notes,
            created_at=new_version.created_at,
            updated_at=new_version.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/prompts/{prompt_id}/versions/from-content")
async def create_version_from_content(
    prompt_id: str,
    content: str,
    change_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new version from content, checking for duplicates."""
    try:
        new_version = prompt_version_service.create_version_from_prompt(
            db=db,
            prompt_id=prompt_id,
            content=content,
            change_notes=change_notes
        )
        return PromptVersionResponse(
            id=new_version.id,
            prompt_id=new_version.prompt_id,
            version_number=new_version.version_number,
            content=new_version.content,
            change_notes=new_version.change_notes,
            created_at=new_version.created_at,
            updated_at=new_version.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Comparisons endpoints
@router.post("/comparisons/compare", response_model=ComparisonResponse, status_code=201)
async def create_comparison(
    comparison_data: ComparisonCreate,
    db: Session = Depends(get_db)
):
    """Create a new comparison."""
    comparison = comparison_crud.create(db=db, obj_in=comparison_data)
    return ComparisonResponse(
        id=comparison.id,
        name=comparison.name,
        description=comparison.description,
        type=comparison.type,
        input_text=comparison.input_text,
        llm_config_id=comparison.llm_config_id,
        save_snapshot=comparison.save_snapshot,
        results=comparison.results,
        successful_executions=comparison.successful_executions,
        total_executions=comparison.total_executions,
        average_execution_time_ms=comparison.average_execution_time_ms,
        total_tokens_used=comparison.total_tokens_used,
        created_at=comparison.created_at,
        updated_at=comparison.updated_at
    )


@router.get("/comparisons", response_model=ComparisonListResponse)
async def get_comparisons(
    type: Optional[str] = Query(None, description="Filter by comparison type"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of comparisons."""
    skip = (page - 1) * limit
    
    comparisons, total = comparison_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        type=type
    )
    
    # Calculate pagination
    total_pages = (total + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1
    
    return ComparisonListResponse(
        items=[ComparisonResponse(
            id=comp.id,
            name=comp.name,
            description=comp.description,
            type=comp.type,
            input_text=comp.input_text,
            llm_config_id=comp.llm_config_id,
            save_snapshot=comp.save_snapshot,
            results=comp.results,
            successful_executions=comp.successful_executions,
            total_executions=comp.total_executions,
            average_execution_time_ms=comp.average_execution_time_ms,
            total_tokens_used=comp.total_tokens_used,
            created_at=comp.created_at,
            updated_at=comp.updated_at
        ) for comp in comparisons],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/comparisons/{comparison_id}", response_model=ComparisonResponse)
async def get_comparison_by_id(
    comparison_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific comparison by ID."""
    comparison = comparison_crud.get(db=db, comparison_id=comparison_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    return ComparisonResponse(
        id=comparison.id,
        name=comparison.name,
        description=comparison.description,
        type=comparison.type,
        input_text=comparison.input_text,
        llm_config_id=comparison.llm_config_id,
        save_snapshot=comparison.save_snapshot,
        results=comparison.results,
        successful_executions=comparison.successful_executions,
        total_executions=comparison.total_executions,
        average_execution_time_ms=comparison.average_execution_time_ms,
        total_tokens_used=comparison.total_tokens_used,
        created_at=comparison.created_at,
        updated_at=comparison.updated_at
    )


@router.delete("/comparisons/{comparison_id}")
async def delete_comparison(
    comparison_id: str,
    db: Session = Depends(get_db)
):
    """Delete a comparison."""
    success = comparison_crud.delete(db=db, comparison_id=comparison_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    return {"message": "Comparison deleted successfully"}


@router.get("/comparisons/{comparison_id}/export")
async def export_comparison(
    comparison_id: str,
    format: str = Query("json", description="Export format"),
    db: Session = Depends(get_db)
):
    """Export a comparison."""
    comparison_data = comparison_crud.export_comparison(
        db=db,
        comparison_id=comparison_id
    )
    
    if not comparison_data:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    if format == "json":
        return {
            "id": comparison_data["id"],
            "name": comparison_data["name"],
            "exported_at": "2025-11-06T10:00:00Z",
            "format": "json",
            "data": comparison_data
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


# Enhanced comparison endpoints
@router.post("/comparisons/same-llm", response_model=ComparisonResponse, status_code=201)
async def create_same_llm_comparison(
    comparison_data: ComparisonCreate,
    prompt_version_ids: List[str],
    db: Session = Depends(get_db)
):
    """Create a comparison using the same LLM for multiple prompt versions."""
    try:
        comparison = await comparison_service.create_same_llm_comparison(
            db=db,
            comparison_data=comparison_data,
            prompt_version_ids=prompt_version_ids
        )
        
        return ComparisonResponse(
            id=comparison.id,
            name=comparison.name,
            description=comparison.description,
            type=comparison.type,
            input_text=comparison.input_text,
            llm_config_id=comparison.llm_config_id,
            save_snapshot=comparison.save_snapshot,
            results=comparison.results,
            successful_executions=comparison.successful_executions,
            total_executions=comparison.total_executions,
            average_execution_time_ms=comparison.average_execution_time_ms,
            total_tokens_used=comparison.total_tokens_used,
            created_at=comparison.created_at,
            updated_at=comparison.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/comparisons/different-llm", response_model=ComparisonResponse, status_code=201)
async def create_different_llm_comparison(
    prompt_version_id: str,
    llm_config_ids: List[str],
    input_text: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a comparison using different LLMs for the same prompt version."""
    try:
        comparison = await comparison_service.create_different_llm_comparison(
            db=db,
            prompt_version_id=prompt_version_id,
            llm_config_ids=llm_config_ids,
            input_text=input_text,
            name=name,
            description=description
        )
        
        return ComparisonResponse(
            id=comparison.id,
            name=comparison.name,
            description=comparison.description,
            type=comparison.type,
            input_text=comparison.input_text,
            llm_config_id=comparison.llm_config_id,
            save_snapshot=comparison.save_snapshot,
            results=comparison.results,
            successful_executions=comparison.successful_executions,
            total_executions=comparison.total_executions,
            average_execution_time_ms=comparison.average_execution_time_ms,
            total_tokens_used=comparison.total_tokens_used,
            created_at=comparison.created_at,
            updated_at=comparison.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/comparisons/{comparison_id}/summary")
async def get_comparison_summary(
    comparison_id: str,
    db: Session = Depends(get_db)
):
    """Get a detailed summary of comparison results."""
    try:
        summary = comparison_service.get_comparison_summary(
            db=db,
            comparison_id=comparison_id
        )
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/comparisons/{comparison_id}/results")
async def get_comparison_results(
    comparison_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed results for a comparison."""
    try:
        results = llm_service.get_comparison_results(db, comparison_id)
        return {
            "comparison_id": comparison_id,
            "results": results,
            "total_results": len(results)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/comparisons/{comparison_id}/quality-analysis")
async def get_comparison_quality_analysis(
    comparison_id: str,
    db: Session = Depends(get_db)
):
    """Get quality analysis of comparison results."""
    try:
        results = llm_service.get_comparison_results(db, comparison_id)
        analysis = comparison_service.compare_results_quality(results)
        return {
            "comparison_id": comparison_id,
            "quality_analysis": analysis
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/comparisons/{comparison_id}/retry")
async def retry_comparison(
    comparison_id: str,
    db: Session = Depends(get_db)
):
    """Retry a failed comparison."""
    try:
        # Get comparison details
        comparison = comparison_crud.get(db=db, comparison_id=comparison_id)
        if not comparison:
            raise ValueError("Comparison not found")
        
        # Get existing results to retry failed ones
        results = llm_service.get_comparison_results(db, comparison_id)
        failed_results = [r for r in results if not r["success"]]
        
        if not failed_results:
            return {"message": "No failed executions to retry"}
        
        # Retry failed executions
        retry_count = 0
        for failed_result in failed_results:
            # Get prompt version
            prompt_version = prompt_version_crud.get(db=db, version_id=failed_result["version_id"])
            
            # Retry LLM call
            new_result = await llm_service.call_llm(comparison.input_text, comparison.llm_config)
            
            # Update existing record
            from src.models.comparison_prompt_version import ComparisonPromptVersion
            existing_record = (
                db.query(ComparisonPromptVersion)
                .filter(
                    ComparisonPromptVersion.comparison_id == comparison_id,
                    ComparisonPromptVersion.prompt_version_id == failed_result["version_id"]
                )
                .first()
            )
            
            if existing_record:
                existing_record.result = json.dumps(new_result) if new_result else None
                existing_record.execution_time_ms = new_result["execution_time_ms"]
                existing_record.tokens_used = new_result["tokens_used"]
                existing_record.error_message = new_result.get("error")
                retry_count += 1
        
        db.commit()
        
        # Update comparison statistics
        updated_results = llm_service.get_comparison_results(db, comparison_id)
        successful_results = [r for r in updated_results if r["success"]]
        
        comparison.successful_executions = len(successful_results)
        comparison.total_executions = len(updated_results)
        
        if successful_results:
            avg_execution_time = sum(r["execution_time_ms"] for r in successful_results) / len(successful_results)
            total_tokens = sum(r["tokens_used"] for r in successful_results)
        else:
            avg_execution_time = 0
            total_tokens = 0
        
        comparison.average_execution_time_ms = int(avg_execution_time)
        comparison.total_tokens_used = total_tokens
        
        db.commit()
        
        return {
            "message": f"Retried {retry_count} failed executions",
            "successful_executions": len(successful_results),
            "total_executions": len(updated_results)
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# LLM Configuration endpoints
@router.get("/llm-configs", response_model=LLMConfigListResponse)
async def get_llm_configs(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """Get list of LLM configurations with filtering and pagination."""
    skip = (page - 1) * limit

    configs, total = llm_config_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        provider=provider,
        active=active
    )

    # Calculate pagination
    total_pages = (total + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1

    return LLMConfigListResponse(
        items=[
            LLMConfigResponse(
                id=config.id,
                provider=config.provider,
                api_key=config.api_key,
                model=config.model,
                base_url=config.base_url,
                temperature=float(config.temperature),
                max_tokens=config.max_tokens,
                active=config.is_active,
                created_at=config.created_at.isoformat(),
                updated_at=config.updated_at.isoformat()
            ) for config in configs
        ],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.post("/llm-configs", response_model=LLMConfigResponse, status_code=201)
async def create_llm_config(
    config_data: LLMConfigCreate,
    db: Session = Depends(get_db)
):
    """Create a new LLM configuration."""
    config = llm_config_crud.create(db=db, obj_in=config_data)
    return LLMConfigResponse(
        id=config.id,
        provider=config.provider,
        api_key=config.api_key,
        model=config.model,
        base_url=config.base_url,
        temperature=float(config.temperature),
        max_tokens=config.max_tokens,
        active=config.is_active,
        created_at=config.created_at.isoformat(),
        updated_at=config.updated_at.isoformat()
    )


@router.get("/llm-configs/{config_id}", response_model=LLMConfigResponse)
async def get_llm_config_by_id(
    config_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific LLM configuration by ID."""
    config = llm_config_crud.get(db=db, config_id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail="LLM configuration not found")

    return LLMConfigResponse(
        id=config.id,
        provider=config.provider,
        api_key=config.api_key,
        model=config.model,
        base_url=config.base_url,
        temperature=float(config.temperature),
        max_tokens=config.max_tokens,
        active=config.is_active,
        created_at=config.created_at.isoformat(),
        updated_at=config.updated_at.isoformat()
    )


@router.put("/llm-configs/{config_id}", response_model=LLMConfigResponse)
async def update_llm_config(
    config_id: str,
    config_data: LLMConfigUpdate,
    db: Session = Depends(get_db)
):
    """Update an LLM configuration."""
    config = llm_config_crud.get(db=db, config_id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail="LLM configuration not found")

    updated_config = llm_config_crud.update(db=db, db_obj=config, obj_in=config_data)
    return LLMConfigResponse(
        id=updated_config.id,
        provider=updated_config.provider,
        api_key=updated_config.api_key,
        model=updated_config.model,
        base_url=updated_config.base_url,
        temperature=float(updated_config.temperature),
        max_tokens=updated_config.max_tokens,
        active=updated_config.is_active,
        created_at=updated_config.created_at.isoformat(),
        updated_at=updated_config.updated_at.isoformat()
    )


@router.delete("/llm-configs/{config_id}")
async def delete_llm_config(
    config_id: str,
    db: Session = Depends(get_db)
):
    """Delete an LLM configuration."""
    success = llm_config_crud.delete(db=db, config_id=config_id)
    if not success:
        raise HTTPException(status_code=404, detail="LLM configuration not found")
    return {"message": "LLM configuration deleted successfully"}


@router.patch("/llm-configs/{config_id}/toggle")
async def toggle_llm_config(
    config_id: str,
    db: Session = Depends(get_db)
):
    """Toggle (activate/deactivate) an LLM configuration."""
    config = llm_config_crud.get(db=db, config_id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail="LLM configuration not found")

    # Toggle the active state
    if config.is_active:
        updated_config = llm_config_crud.deactivate(db=db, config_id=config_id)
    else:
        updated_config = llm_config_crud.activate(db=db, config_id=config_id)

    return LLMConfigResponse(
        id=updated_config.id,
        provider=updated_config.provider,
        api_key=updated_config.api_key,
        model=updated_config.model,
        base_url=updated_config.base_url,
        temperature=float(updated_config.temperature),
        max_tokens=updated_config.max_tokens,
        active=updated_config.is_active,
        created_at=updated_config.created_at.isoformat(),
        updated_at=updated_config.updated_at.isoformat()
    )


@router.post("/llm/test")
async def test_llm_with_prompt(
    request: LLMTestRequest,
    db: Session = Depends(get_db)
):
    """Test a prompt with a specific LLM configuration."""
    config = llm_config_crud.get(db=db, config_id=request.llm_config_id)
    if not config:
        raise HTTPException(status_code=404, detail="LLM configuration not found")

    try:
        result = await llm_service.call_llm(request.prompt, config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/llm-configs/test")
async def test_llm_connection(
    provider: str,
    api_key: str,
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 100,
    db: Session = Depends(get_db)
):
    """Test LLM provider connection with the given credentials."""
    # Create a temporary config object for testing
    from src.models.llm_config import LLMConfig

    temp_config = LLMConfig(
        name=f"temp-{provider}",
        provider=provider,
        api_key=api_key,
        model=model,
        temperature=str(temperature),
        max_tokens=max_tokens,
        is_active=True
    )

    # Use a simple test prompt
    test_prompt = "Say 'Connection test successful' if you can read this."

    try:
        result = await llm_service.call_llm(test_prompt, temp_config)

        if result["success"]:
            return {
                "success": True,
                "message": "Connection test successful",
                "provider": provider,
                "model": result.get("model"),
                "execution_time_ms": result.get("execution_time_ms"),
                "response_preview": result.get("content", "")[:100]
            }
        else:
            return {
                "success": False,
                "message": "Connection test failed",
                "error": result.get("error", "Unknown error"),
                "provider": provider
            }
    except Exception as e:
        return {
            "success": False,
            "message": "Connection test failed",
            "error": str(e),
            "provider": provider
        }
