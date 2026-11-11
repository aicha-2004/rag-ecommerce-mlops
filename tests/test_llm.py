import pytest

from src.llm import ExtractiveLLM, GroqLLM, get_llm, load_system_prompt


def test_extractive_llm_returns_best_passage():
    hits = [{"text": "meilleur passage"}, {"text": "autre"}]
    assert ExtractiveLLM().generate("question", hits) == "meilleur passage"


def test_default_provider_is_extractive(params, monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    assert isinstance(get_llm(params), ExtractiveLLM)


def test_groq_requires_api_key(params, monkeypatch):
    pytest.importorskip("groq")
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        get_llm(params)
    assert GroqLLM  # classe disponible


def test_system_prompt_defines_abstention_rule():
    assert "INFORMATION_INSUFFISANTE" in load_system_prompt()
