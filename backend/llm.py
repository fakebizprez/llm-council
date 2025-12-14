"""LLM Provider interface for multiple backends (OpenRouter, Ollama, Local OpenAI)."""

import httpx
import asyncio
import os
from typing import List, Dict, Any, Optional
from .config import OPENROUTER_API_KEY, OPENROUTER_API_URL, MODEL_CONFIGS

DEFAULT_TIMEOUT = 120.0

async def query_model(
    model_id: str,
    messages: List[Dict[str, str]],
    timeout: float = DEFAULT_TIMEOUT
) -> Optional[Dict[str, Any]]:
    """
    Query a model via the configured provider.

    Args:
        model_id: Model identifier (used for config lookup)
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds

    Returns:
        Response dict with 'content' and optional 'reasoning_details', or None if failed
    """
    # Look up config, default to OpenRouter
    config = MODEL_CONFIGS.get(model_id, {})
    provider = config.get("provider", "openrouter")

    if provider == "openrouter":
        return await _query_openrouter(model_id, messages, timeout)
    elif provider == "ollama":
        return await _query_ollama(model_id, messages, config, timeout)
    elif provider == "openai_compatible":
        return await _query_openai_compatible(model_id, messages, config, timeout)
    else:
        print(f"Unknown provider '{provider}' for model '{model_id}'")
        return None

async def _query_openrouter(model_id: str, messages: List[Dict[str, str]], timeout: float) -> Optional[Dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/stackblitz/bolt", # Optional but good practice
    }

    payload = {
        "model": model_id,
        "messages": messages,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            message = data['choices'][0]['message']

            return {
                'content': message.get('content'),
                'reasoning_details': message.get('reasoning_details')
            }

    except Exception as e:
        print(f"Error querying OpenRouter model {model_id}: {e}")
        return None

async def _query_ollama(model_id: str, messages: List[Dict[str, str]], config: Dict[str, Any], timeout: float) -> Optional[Dict[str, Any]]:
    base_url = config.get("base_url", "http://localhost:11434")
    # Clean URL
    base_url = base_url.rstrip("/")

    # Check if model name overrides the ID
    actual_model = config.get("model", model_id)

    url = f"{base_url}/api/chat"

    payload = {
        "model": actual_model,
        "messages": messages,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            message = data.get('message', {})

            return {
                'content': message.get('content'),
                # Ollama responses typically don't have reasoning_details yet
                'reasoning_details': None
            }

    except Exception as e:
        print(f"Error querying Ollama model {model_id}: {e}")
        return None

async def _query_openai_compatible(model_id: str, messages: List[Dict[str, str]], config: Dict[str, Any], timeout: float) -> Optional[Dict[str, Any]]:
    base_url = config.get("base_url", "http://localhost:1234/v1")
    base_url = base_url.rstrip("/")

    api_key = config.get("api_key", "lm-studio")
    actual_model = config.get("model", model_id)

    url = f"{base_url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": actual_model,
        "messages": messages,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            message = data['choices'][0]['message']

            return {
                'content': message.get('content'),
                'reasoning_details': message.get('reasoning_details')
            }

    except Exception as e:
        print(f"Error querying OpenAI-compatible model {model_id}: {e}")
        return None

async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.

    Args:
        models: List of model identifiers
        messages: List of message dicts to send to each model

    Returns:
        Dict mapping model identifier to response dict (or None if failed)
    """
    # Create tasks for all models
    tasks = [query_model(model, messages) for model in models]

    # Wait for all to complete
    responses = await asyncio.gather(*tasks)

    # Map models to their responses
    return {model: response for model, response in zip(models, responses)}
