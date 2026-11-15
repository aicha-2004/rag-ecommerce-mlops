"""Generation : LLM extractif (sans API, pour tests/CI) ou Groq."""
import os
import time

from src.config import ROOT


def load_system_prompt() -> str:
    return (ROOT / "prompts" / "rag_system.txt").read_text(encoding="utf-8")


class ExtractiveLLM:
    """Renvoie tous les passages recuperes, sans les reformuler. Deterministe : sert a la CI.

    C'est exactement le contexte que verrait un vrai LLM. En mode extractif, `answer_accuracy`
    mesure donc « le fait attendu figure-t-il dans le contexte recupere ? » (borne haute de la
    generation). La qualite reelle des reponses se mesure avec Groq.
    """

    name = "extractive"

    def generate(self, question, hits):
        return "\n\n".join(h["text"] for h in hits)


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
