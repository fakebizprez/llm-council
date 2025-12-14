"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Council members - list of model identifiers
COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "x-ai/grok-4",
    # Add your local models here, e.g.:
    # "llama3",
]

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = "google/gemini-3-pro-preview"

# Model Configurations
# Map model identifiers to their provider and settings.
# Default provider is "openrouter" if not specified.
MODEL_CONFIGS = {
    # OpenRouter models don't strictly need entries here if they use defaults,
    # but you can customize them if needed.

    # Examples for Local Models:
    # "llama3": {
    #     "provider": "ollama",
    #     "base_url": "http://localhost:11434",
    #     "model": "llama3"
    # },
    # "local-mistral": {
    #     "provider": "openai_compatible",
    #     "base_url": "http://localhost:1234/v1",
    #     "api_key": "lm-studio",
    #     "model": "mistral-7b-instruct"
    # }
}

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Data directory for conversation storage
DATA_DIR = "data/conversations"

# SQLite database path (created automatically if missing)
DB_PATH = os.getenv("DB_PATH", "data/conversations.db")
