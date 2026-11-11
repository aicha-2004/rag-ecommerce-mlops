"""Generation : LLM extractif (sans API, pour tests/CI) ou Groq."""
import os
import time

from src.config import ROOT


def load_system_prompt() -> str:
    return (ROOT / "prompts" / "rag_system.txt").read_text(encoding="utf-8")


class ExtractiveLLM:
    """Renvoie le meilleur passage tel quel. Deterministe : sert a la CI et aux tests."""

    name = "extractive"

    def generate(self, question, hits):
        return hits[0]["text"]


class GroqLLM:
    name = "groq"

    def __init__(self, model: str, temperature: float):
        from groq import Groq

        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY manquante : renseignez-la dans le fichier .env")
        self.client = Groq(api_key=key)
        self.model, self.temperature = model, temperature
        self.system = load_system_prompt()

    def generate(self, question, hits):
        context = "\n\n".join(f"[{h['source']}] {h['text']}" for h in hits)
        messages = [
            {"role": "system", "content": self.system},
            {"role": "user", "content": f"CONTEXTE :\n{context}\n\nQUESTION : {question}"},
        ]
        for attempt in range(4):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model, temperature=self.temperature, messages=messages
                )
                return (resp.choices[0].message.content or "").strip()
            except Exception as exc:  # limite de debit (429) : on attend puis on reessaie
                if "rate" in str(exc).lower() and attempt < 3:
                    time.sleep(20 * (attempt + 1))
                    continue
                raise


def get_llm(params):
    cfg = params["llm"]
    provider = os.getenv("LLM_PROVIDER") or cfg["provider"]
    if provider == "groq":
        return GroqLLM(cfg["model"], cfg["temperature"])
    return ExtractiveLLM()
