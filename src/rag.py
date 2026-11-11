"""Phase 2 - Pipeline RAG : retrieval -> garde-fous -> generation -> reponse citee."""
from src.guardrails import is_prompt_injection

MSG_OOS = (
    "Je ne peux repondre qu'aux questions sur la documentation ShopMed "
    "(commande, livraison, retours, paiement). Cette question est hors perimetre."
)
MSG_INJ = "Requete refusee : tentative de contournement des consignes detectee."
MSG_INSUF = "Les documents disponibles ne contiennent pas assez d'informations pour repondre."


class RAGPipeline:
    def __init__(self, retriever, llm, min_score: float):
        self.retriever, self.llm, self.min_score = retriever, llm, min_score

    def answer(self, question: str) -> dict:
        if is_prompt_injection(question):
            return self._refuse(MSG_INJ, "prompt_injection", [])
        hits = self.retriever.search(question)
        if not hits or hits[0]["score"] < self.min_score:
            return self._refuse(MSG_OOS, "out_of_scope", hits)
        text = self.llm.generate(question, hits)
        if "INFORMATION_INSUFFISANTE" in text:
            return self._refuse(MSG_INSUF, "insufficient_context", hits)
        sources = []
        for h in hits:
            label = f"{h['source']} > {h['section']}" if h.get("section") else h["source"]
            if label not in sources:
                sources.append(label)
        return {
            "answer": text, "sources": sources, "hits": hits,
            "refused": False, "reason": None,
        }

    @staticmethod
    def _refuse(message, reason, hits):
        return {"answer": message, "sources": [], "hits": hits, "refused": True, "reason": reason}
