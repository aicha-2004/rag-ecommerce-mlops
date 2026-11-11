"""Aucun secret ne doit etre present dans les fichiers du depot."""
import re

from src.config import ROOT

SKIP_DIRS = {".git", ".venv", "venv", "artifacts", "mlruns", "mlartifacts", ".pytest_cache",
             "__pycache__", ".ruff_cache", "dvc_storage", ".dvc"}
TEXT_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".txt", ".json", ".toml", ".example"}
KEY_PATTERN = re.compile(r"gsk_[A-Za-z0-9]{20,}")


def _text_files():
    for p in ROOT.rglob("*"):
        skipped = set(p.relative_to(ROOT).parts) & SKIP_DIRS
        if p.is_file() and not skipped and p.suffix in TEXT_SUFFIXES:
            yield p


def test_no_api_key_in_repository_files():
    for p in _text_files():
        assert not KEY_PATTERN.search(p.read_text(encoding="utf-8", errors="ignore")), p


def test_env_example_has_no_secret_value():
    lines = (ROOT / ".env.example").read_text(encoding="utf-8").splitlines()
    for line in lines:
        if line.startswith("GROQ_API_KEY"):
            assert line.split("=", 1)[1].strip() == ""


def test_env_file_is_gitignored():
    assert ".env" in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
