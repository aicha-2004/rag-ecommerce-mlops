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

## Exceptions pip-audit acceptees (CI)

`pip-audit` signale cinq vulnerabilites sans version corrigee disponible. Elles sont ignorees
explicitement dans `.github/workflows/ci.yml`, apres analyse, et doivent etre reverifiees a chaque
mise a jour des dependances.

| Identifiant | Paquet | Nature | Pourquoi ne s'applique pas ici |
|---|---|---|---|
| PYSEC-2026-311 | chromadb | execution de code via l'API HTTP du serveur Chroma | nous utilisons le client embarque (PersistentClient), sans serveur HTTP |
| PYSEC-2026-3813, 3814, 3815 | chromadb | autorisations insuffisantes (multi-tenant, RBAC) du serveur Chroma | idem : pas de serveur, pas d'authentification multi-utilisateurs |
| PYSEC-2026-2447 | diskcache (dependance de DVC) | pickle : execution de code si un attaquant ecrit dans le dossier de cache | cache local de la CI, sans acces d'un tiers |

Limite : si le projet passait a un serveur Chroma expose ou a un cache partage, ces exceptions
seraient a reconsiderer (changement de base vectorielle, ou mise a jour des qu'un correctif existe).