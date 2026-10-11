"""Đường dẫn và biến môi trường. Đọc file .env ở gốc repo nếu có."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_INDEX = ROOT / "data" / "index"
ONTOLOGY_DIR = ROOT / "ontology"
EVAL_DIR = ROOT / "eval"

CORPUS_PATH = DATA_PROCESSED / "corpus.json"
ONTOLOGY_PATH = ONTOLOGY_DIR / "family-law.ttl"
MAPPING_PATH = ONTOLOGY_DIR / "mapping.csv"


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


LLM_BASE_URL = env("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai")
LLM_API_KEY = env("LLM_API_KEY", "")
LLM_MODEL = env("LLM_MODEL", "gemini-2.0-flash")
EMBEDDING_BACKEND = env("EMBEDDING_BACKEND", "fastembed")
EMBEDDING_MODEL = env("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
ABSTAIN_RRF_THRESHOLD = float(env("ABSTAIN_RRF_THRESHOLD", "0.012"))
