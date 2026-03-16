"""
Common configuration and environment setup
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent  # Go up to project root
load_dotenv(project_root / ".env")

# Project root directory (one level up from code folder)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "huggingface")  # Options: "huggingface", "groq", "ollama"

# HuggingFace Configuration (FREE - High rate limits!)
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
HF_PRIMARY_MODEL = os.getenv("HF_PRIMARY_MODEL", "Qwen/Qwen2.5-Coder-32B-Instruct")
HF_FALLBACK_1 = os.getenv("HF_FALLBACK_1", "Qwen/Qwen2.5-Coder-7B-Instruct")
HF_FALLBACK_2 = os.getenv("HF_FALLBACK_2", "Qwen/Qwen2.5-Coder-14B-Instruct")
HF_FALLBACK_3 = os.getenv("HF_FALLBACK_3", "deepseek-ai/deepseek-coder-1.3b-instruct")

# All HuggingFace models in fallback order
HF_MODELS = [HF_PRIMARY_MODEL, HF_FALLBACK_1, HF_FALLBACK_2, HF_FALLBACK_3]

# Groq Configuration (Fallback: 14,400 requests/day)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Ollama Configuration (Local fallback - unlimited)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-coder:6.7b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# MCP Server Configuration
MCP_SERVER_URL = "http://localhost:8003"

# Rate Limiting (Custom setting: 4 RPM = ~15 seconds between requests)
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "4"))
REQUEST_TIMEOUT = 30  # seconds

# Vector Database
VECTOR_DB_PATH = PROJECT_ROOT / "chroma_db"

# Output Configuration
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Server paths
SERVER_DIR = PROJECT_ROOT / "server"
EMBEDDING_MODEL_PATH = SERVER_DIR / "embedding_model"
STORAGE_PATH = SERVER_DIR / "storage"

# CSV Output Format
CSV_COLUMNS = ["ID", "Bug Line", "Explanation"]

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
