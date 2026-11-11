# Risques et gouvernance

| Risque | Exemple | Mesure en place | Limite restante |
|---|---|---|---|
| Prompt injection | « Ignore tes instructions... » | regex + prompt systeme + refus | reformulations non detectees |
| Hallucination | reponse inventee | contexte impose, INFORMATION_INSUFFISANTE, citations | fidelite mesuree par proxy |
| Hors perimetre | « Capitale de la France ? » | seuil `min_score` calibre | seuil a recalibrer si le corpus change |
| Documentation obsolete | politique de retour modifiee | corpus versionne (DVC), tag | pas de detection automatique |
| Donnees personnelles | un client saisit son numero | aucune donnee stockee, pas de journalisation du contenu | a verifier en production |
| Secrets | cle Groq dans le depot | `.env` ignore, test anti-secret, `.env.example` | historique Git a verifier |
| Regression | nouveau chunking moins bon | quality gates en CI | seuils pedagogiques |
