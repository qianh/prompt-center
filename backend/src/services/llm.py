"""
LLM service for calling different language models.
"""

import time
import json
import asyncio
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import httpx
from sqlalchemy.orm import Session

from src.models.llm_config import LLMConfig
from src.models.comparison import Comparison
from src.models.comparison_prompt_version import ComparisonPromptVersion
from src.models.prompt_version import PromptVersion


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def call(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Call the LLM with the given prompt and configuration."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def get_provider_name(self) -> str:
        return "openai"

    async def call(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Call OpenAI API."""
        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": config.get("model", "gpt-3.5-turbo"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 1000)
        }

        # Use custom base_url if provided, otherwise use default
        base_url = config.get("base_url", "https://api.openai.com")
        api_url = f"{base_url.rstrip('/')}/v1/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                end_time = time.time()

                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {}),
                    "model": result["model"],
                    "execution_time_ms": int((end_time - start_time) * 1000),
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                }

        except httpx.HTTPStatusError as e:
            end_time = time.time()
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "execution_time_ms": int((end_time - start_time) * 1000),
                "tokens_used": 0
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": int((end_time - start_time) * 1000),
                "tokens_used": 0
            }


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def get_provider_name(self) -> str:
        return "anthropic"

    async def call(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Call Anthropic API."""
        start_time = time.time()

        headers = {
            "x-api-key": config['api_key'],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": config.get("model", "claude-3-sonnet-20240229"),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.get("max_tokens", 1000),
            "temperature": config.get("temperature", 0.7)
        }

        # Use custom base_url if provided, otherwise use default
        base_url = config.get("base_url", "https://api.anthropic.com")
        api_url = f"{base_url.rstrip('/')}/v1/messages"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                end_time = time.time()

                return {
                    "success": True,
                    "content": result["content"][0]["text"],
                    "usage": result.get("usage", {}),
                    "model": result["model"],
                    "execution_time_ms": int((end_time - start_time) * 1000),
                    "tokens_used": result.get("usage", {}).get("input_tokens", 0) + result.get("usage", {}).get("output_tokens", 0)
                }

        except httpx.HTTPStatusError as e:
            end_time = time.time()
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "execution_time_ms": int((end_time - start_time) * 1000),
                "tokens_used": 0
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": int((end_time - start_time) * 1000),
                "tokens_used": 0
            }


class GoogleAIProvider(LLMProvider):
    """Google AI (Gemini) API provider."""

    def get_provider_name(self) -> str:
        return "google"

    async def call(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Call Google AI API."""
        start_time = time.time()

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": config.get("temperature", 0.7),
                "maxOutputTokens": config.get("max_tokens", 1000)
            }
        }

        # Use custom base_url if provided
        base_url = config.get("base_url", "https://generativelanguage.googleapis.com")
        model = config.get("model", "gemini-pro")
        api_key = config['api_key']
        api_url = f"{base_url.rstrip('/')}/v1beta/models/{model}:generateContent?key={api_key}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                end_time = time.time()

                content = result["candidates"][0]["content"]["parts"][0]["text"]
                tokens = result.get("usageMetadata", {}).get("totalTokenCount", 0)

                return {
                    "success": True,
                    "content": content,
                    "usage": result.get("usageMetadata", {}),
                    "model": model,
                    "execution_time_ms": int((end_time - start_time) * 1000),
                    "tokens_used": tokens
                }

        except httpx.HTTPStatusError as e:
            end_time = time.time()
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "execution_time_ms": int((end_time - start_time) * 1000),
                "tokens_used": 0
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": int((end_time - start_time) * 1000),
                "tokens_used": 0
            }


class DeepSeekProvider(LLMProvider):
    """DeepSeek API provider (OpenAI-compatible)."""

    def get_provider_name(self) -> str:
        return "deepseek"

    async def call(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Call DeepSeek API (OpenAI-compatible format)."""
        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": config.get("model", "deepseek-chat"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 1000)
        }

        # Use custom base_url if provided, otherwise use DeepSeek default
        base_url = config.get("base_url", "https://api.deepseek.com")
        api_url = f"{base_url.rstrip('/')}/v1/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                end_time = time.time()

                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {}),
                    "model": result["model"],
                    "execution_time_ms": int((end_time - start_time) * 1000),
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                }

        except httpx.HTTPStatusError as e:
            end_time = time.time()
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "execution_time_ms": int((end_time - start_time) * 1000),
                "tokens_used": 0
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": int((end_time - start_time) * 1000),
                "tokens_used": 0
            }


class QwenProvider(LLMProvider):
    """Qwen (通义千问) API provider (OpenAI-compatible)."""

    def get_provider_name(self) -> str:
        return "qwen"

    async def call(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Call Qwen API (OpenAI-compatible format)."""
        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": config.get("model", "qwen-turbo"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 1000)
        }

        # Use custom base_url if provided, otherwise use Alibaba Cloud default
        base_url = config.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode")
        api_url = f"{base_url.rstrip('/')}/v1/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                end_time = time.time()

                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {}),
                    "model": result["model"],
                    "execution_time_ms": int((end_time - start_time) * 1000),
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                }

        except httpx.HTTPStatusError as e:
            end_time = time.time()
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "execution_time_ms": int((end_time - start_time) * 1000),
                "tokens_used": 0
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": int((end_time - start_time) * 1000),
                "tokens_used": 0
            }


class KimiProvider(LLMProvider):
    """Kimi (月之暗面/Moonshot) API provider (OpenAI-compatible)."""

    def get_provider_name(self) -> str:
        return "kimi"

    async def call(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Call Kimi API (OpenAI-compatible format)."""
        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": config.get("model", "moonshot-v1-8k"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 1000)
        }

        # Use custom base_url if provided, otherwise use Moonshot default
        base_url = config.get("base_url", "https://api.moonshot.cn")
        api_url = f"{base_url.rstrip('/')}/v1/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                end_time = time.time()

                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {}),
                    "model": result["model"],
                    "execution_time_ms": int((end_time - start_time) * 1000),
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                }

        except httpx.HTTPStatusError as e:
            end_time = time.time()
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "execution_time_ms": int((end_time - start_time) * 1000),
                "tokens_used": 0
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": int((end_time - start_time) * 1000),
                "tokens_used": 0
            }


class CustomProvider(LLMProvider):
    """Custom OpenAI-compatible API provider."""

    def get_provider_name(self) -> str:
        return "custom"

    async def call(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Call custom OpenAI-compatible API."""
        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": config.get("model", "gpt-3.5-turbo"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 1000)
        }

        # Custom provider MUST have base_url
        base_url = config.get("base_url")
        if not base_url:
            return {
                "success": False,
                "error": "Custom provider requires base_url to be configured",
                "execution_time_ms": 0,
                "tokens_used": 0
            }

        api_url = f"{base_url.rstrip('/')}/v1/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                end_time = time.time()

                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {}),
                    "model": result.get("model", config.get("model")),
                    "execution_time_ms": int((end_time - start_time) * 1000),
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                }

        except httpx.HTTPStatusError as e:
            end_time = time.time()
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "execution_time_ms": int((end_time - start_time) * 1000),
                "tokens_used": 0
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": int((end_time - start_time) * 1000),
                "tokens_used": 0
            }


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def get_provider_name(self) -> str:
        return "mock"

    async def call(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Mock LLM call for testing."""
        start_time = time.time()

        # Simulate processing time
        await asyncio.sleep(0.1)

        end_time = time.time()

        # Generate mock response based on prompt length
        mock_content = f"Mock response to: {prompt[:50]}..."

        return {
            "success": True,
            "content": mock_content,
            "usage": {"total_tokens": len(mock_content.split())},
            "model": config.get("model", "mock-model"),
            "execution_time_ms": int((end_time - start_time) * 1000),
            "tokens_used": len(mock_content.split())
        }


class LLMService:
    """Service for managing LLM operations."""

    def __init__(self):
        self.providers = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "google": GoogleAIProvider(),
            "deepseek": DeepSeekProvider(),
            "qwen": QwenProvider(),
            "kimi": KimiProvider(),
            "custom": CustomProvider(),
            "mock": MockLLMProvider()
        }
    
    def get_provider(self, provider_name: str) -> LLMProvider:
        """Get LLM provider by name."""
        if provider_name not in self.providers:
            raise ValueError(f"Unsupported provider: {provider_name}")
        return self.providers[provider_name]
    
    async def call_llm(self, prompt: str, config: LLMConfig) -> Dict[str, Any]:
        """Call LLM with the given prompt and configuration."""
        provider = self.get_provider(config.provider)

        provider_config = {
            "api_key": config.api_key,
            "model": config.model,
            "base_url": config.base_url,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens
        }

        return await provider.call(prompt, provider_config)
    
    async def compare_prompt_versions(
        self,
        db: Session,
        *,
        comparison: Comparison,
        prompt_versions: List[PromptVersion]
    ) -> List[Dict[str, Any]]:
        """Compare multiple prompt versions using the same LLM."""
        results = []
        
        for version in prompt_versions:
            result = await self.call_llm(comparison.input_text, comparison.llm_config)
            
            # Store result in database
            comparison_prompt_version = ComparisonPromptVersion(
                comparison_id=comparison.id,
                prompt_version_id=version.id,
                result=json.dumps(result) if result else None,
                execution_time_ms=result["execution_time_ms"],
                tokens_used=result["tokens_used"],
                error_message=result.get("error")
            )
            
            db.add(comparison_prompt_version)
            
            results.append({
                "version_id": version.id,
                "version_number": version.version_number,
                "prompt_content": version.content,
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
        
        return results
    
    def get_comparison_results(
        self,
        db: Session,
        comparison_id: str
    ) -> List[Dict[str, Any]]:
        """Get results for a comparison."""
        results = (
            db.query(ComparisonPromptVersion)
            .join(PromptVersion)
            .filter(ComparisonPromptVersion.comparison_id == comparison_id)
            .all()
        )

        # Sort by version number (handle both int and str types, compare numerically)
        def version_sort_key(result):
            try:
                version_value = result.prompt_version.version_number
                # Handle both integer (old) and string (new) version numbers
                if isinstance(version_value, int):
                    return float(version_value)
                else:
                    return float(version_value)
            except (ValueError, TypeError):
                return 0.0

        results = sorted(results, key=version_sort_key)

        return [
            {
                "version_id": result.prompt_version_id,
                "version_number": result.prompt_version.version_number,
                "prompt_content": result.prompt_version.content,
                "execution_result": json.loads(result.result) if result.result else None,
                "success": json.loads(result.result).get("success", False) if result.result else False,
                "execution_time_ms": result.execution_time_ms,
                "tokens_used": result.tokens_used,
                "error_message": result.error_message,
                "created_at": result.created_at
            }
            for result in results
        ]


# Create a singleton instance
llm_service = LLMService()
