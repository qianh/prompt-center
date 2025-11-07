"""
Prompt version management service.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import difflib
import json

from src.crud import prompt_crud, prompt_version_crud
from src.models.prompt import Prompt
from src.models.prompt_version import PromptVersion


class PromptVersionService:
    """Service for managing prompt versions with business logic."""

    def create_version_from_prompt(
        self,
        db: Session,
        *,
        prompt_id: str,
        content: str,
        change_notes: Optional[str] = None
    ) -> PromptVersion:
        """Create a new version from existing prompt content."""
        # Check if prompt exists
        prompt = prompt_crud.get(db=db, prompt_id=prompt_id)
        if not prompt:
            raise ValueError("Prompt not found")
        
        # Check if content is different from latest version
        latest_version = prompt_version_crud.get_by_prompt(
            db=db, prompt_id=prompt_id, skip=0, limit=1
        )
        
        if latest_version and latest_version[0].content == content:
            raise ValueError("Content is identical to latest version")
        
        # Create new version
        from src.schemas.prompt_version import PromptVersionCreate
        version_data = PromptVersionCreate(
            content=content,
            change_notes=change_notes
        )
        
        return prompt_version_crud.create(
            db=db, obj_in=version_data, prompt_id=prompt_id
        )

    def get_version_history(
        self,
        db: Session,
        *,
        prompt_id: str,
        include_content: bool = False
    ) -> List[Dict[str, Any]]:
        """Get version history for a prompt."""
        # Check if prompt exists
        prompt = prompt_crud.get(db=db, prompt_id=prompt_id)
        if not prompt:
            raise ValueError("Prompt not found")
        
        versions = prompt_version_crud.get_by_prompt(
            db=db, prompt_id=prompt_id, skip=0, limit=100
        )
        
        if not versions:
            return []
        
        history = []
        for version in versions:
            version_info = {
                "id": version.id,
                "version_number": version.version_number,
                "change_notes": version.change_notes,
                "created_at": version.created_at,
                "updated_at": version.updated_at
            }
            
            if include_content:
                version_info["content"] = version.content
                version_info["content_preview"] = version.content_preview
            
            history.append(version_info)
        
        return history

    def compare_versions_detailed(
        self,
        db: Session,
        *,
        prompt_id: str,
        version_a: str,
        version_b: str,
        include_diff: bool = True
    ) -> Dict[str, Any]:
        """Compare two versions with detailed analysis."""
        # Get versions
        version_a_obj = (
            db.query(PromptVersion)
            .filter(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.version_number == version_a
            )
            .first()
        )
        
        version_b_obj = (
            db.query(PromptVersion)
            .filter(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.version_number == version_b
            )
            .first()
        )
        
        if not version_a_obj or not version_b_obj:
            raise ValueError("One or both versions not found")
        
        # Basic comparison
        comparison = {
            "version_a": {
                "version_number": version_a_obj.version_number,
                "content": version_a_obj.content,
                "change_notes": version_a_obj.change_notes,
                "created_at": version_a_obj.created_at
            },
            "version_b": {
                "version_number": version_b_obj.version_number,
                "content": version_b_obj.content,
                "change_notes": version_b_obj.change_notes,
                "created_at": version_b_obj.created_at
            },
            "is_identical": version_a_obj.content == version_b_obj.content
        }
        
        if include_diff and not comparison["is_identical"]:
            # Generate unified diff
            diff_lines = list(difflib.unified_diff(
                version_a_obj.content.splitlines(keepends=True),
                version_b_obj.content.splitlines(keepends=True),
                fromfile=f"version_{version_a}",
                tofile=f"version_{version_b}",
                lineterm=""
            ))
            
            # Generate HTML diff
            html_diff = self._generate_html_diff(
                version_a_obj.content,
                version_b_obj.content
            )
            
            # Calculate statistics
            stats = self._calculate_diff_stats(
                version_a_obj.content,
                version_b_obj.content
            )
            
            comparison.update({
                "unified_diff": "".join(diff_lines),
                "html_diff": html_diff,
                "stats": stats
            })
        
        return comparison

    def revert_to_version(
        self,
        db: Session,
        *,
        prompt_id: str,
        version_number: str,
        change_notes: Optional[str] = None
    ) -> PromptVersion:
        """Revert prompt to a specific version."""
        # Get target version
        target_version = (
            db.query(PromptVersion)
            .filter(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.version_number == version_number
            )
            .first()
        )
        
        if not target_version:
            raise ValueError("Version not found")
        
        # Create new version with old content
        revert_notes = change_notes or f"Reverted to version {version_number}"
        
        return self.create_version_from_prompt(
            db=db,
            prompt_id=prompt_id,
            content=target_version.content,
            change_notes=revert_notes
        )

    def get_latest_version(
        self,
        db: Session,
        *,
        prompt_id: str
    ) -> Optional[PromptVersion]:
        """Get the latest version of a prompt."""
        versions = prompt_version_crud.get_by_prompt(
            db=db, prompt_id=prompt_id, skip=0, limit=1
        )
        return versions[0] if versions else None

    def _generate_html_diff(self, text_a: str, text_b: str) -> str:
        """Generate HTML side-by-side diff."""
        differ = difflib.HtmlDiff()
        return differ.make_table(
            text_a.splitlines(),
            text_b.splitlines(),
            fromdesc="Version A",
            todesc="Version B",
            context=True,
            numlines=3
        )

    def _calculate_diff_stats(self, text_a: str, text_b: str) -> Dict[str, int]:
        """Calculate diff statistics."""
        lines_a = text_a.splitlines()
        lines_b = text_b.splitlines()
        
        matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
        
        additions = 0
        deletions = 0
        modifications = 0
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                modifications += max(i2 - i1, j2 - j1)
            elif tag == 'delete':
                deletions += i2 - i1
            elif tag == 'insert':
                additions += j2 - j1
        
        return {
            "additions": additions,
            "deletions": deletions,
            "modifications": modifications,
            "total_changes": additions + deletions + modifications
        }


# Create a singleton instance
prompt_version_service = PromptVersionService()
