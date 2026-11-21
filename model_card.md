# System card : assistant RAG ShopMed

## Usage prévu
Répondre aux questions de clients sur la commande, le paiement, la livraison et les retours, à partir de la documentation ShopMed uniquement.

## Hors usage
Conseil juridique ou médical, questions générales, toute information absente de la documentation.

## Version
Commit Git : 0389530. Tag du corpus : corpus-v1. Run MLflow de référence : groq_section (c6f339ad152143659b3f650bb8dc8a7b).

## Données
3 documents Markdown fictifs (faq, politique de retour, guide de livraison), versionnés avec DVC. Jeu d'évaluation : 28 questions (17 valides, 5 hors périmètre, 3 injections, 3 documentation insuffisante).

## Méthode
Découpage par section avec métadonnées, embeddings multilingues (paraphrase-multilingual-MiniLM-L12-v2), index Chroma (cosinus), refus si le meilleur score est sous `min_score`, génération par LLM (Groq) contraint par le contexte.

## Paramètres retenus
chunk_size = 400 ; chunk_overlap = 60 ; stratégie = section ; top_k = 3 ; min_score = 0,26

## Métriques (run groq_section)
Recall@3 = 1,00 ; MRR = 0,97 ; exactitude stricte par mots-clés = 0,65 ; fidélité (proxy lexical) = 0,74 ; refus des questions hors périmètre, injections et documentation insuffisante = 1,00 ; faux refus = 0,00.

## Quality gates
Seuils dans `params.yaml`, vérifiés par `scripts/check_gates.py` en CI (mode extractif : mesure du retrieval, pas du LLM).

## Limites connues
Corpus minuscule et fictif ; seuil et découpage réglés sur le jeu d'évaluation (résultats optimistes) ; fidélité mesurée par proxy lexical ; détection d'injection par regex ; deux erreurs identifiées avec Groq (délai de 48 h omis, tarif de livraison absent du contexte récupéré).

## Gouvernance
Approbation humaine avant production (environnement GitHub `production`). Voir `docs/risques.md`.