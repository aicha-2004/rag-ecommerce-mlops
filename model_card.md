# System card : assistant RAG ShopMed

## Usage prevu
Repondre aux questions de clients sur la commande, le paiement, la livraison et les retours,
a partir de la documentation ShopMed uniquement.

## Hors usage
Conseil juridique ou medical, questions generales, toute information absente de la documentation.

## Version
Commit Git : A COMPLETER. Tag du corpus : A COMPLETER. Run MLflow : A COMPLETER.

## Donnees
3 documents Markdown fictifs (faq, politique de retour, guide de livraison), versionnes avec DVC.
Jeu d'evaluation : 28 questions (17 valides, 5 hors perimetre, 3 injections, 3 documents insuffisants).

## Methode
Decoupage en chunks avec metadonnees, embeddings multilingues, index Chroma (cosinus),
refus si le meilleur score est sous `min_score`, generation par LLM contraint par le contexte.

## Parametres retenus
chunk_size = A COMPLETER ; chunk_overlap = A COMPLETER ; top_k = A COMPLETER ; min_score = A COMPLETER

## Metriques (jeu d'evaluation)
Recall@k = A COMPLETER ; exactitude = A COMPLETER ; fidelite (proxy) = A COMPLETER ;
refus hors perimetre = A COMPLETER

## Quality gates
Seuils dans `params.yaml` (`quality_gate`), verifies par `scripts/check_gates.py` en CI.

## Limites connues
Corpus minuscule ; fidelite mesuree par proxy lexical ; detection d'injection par regex ;
le mode extractif de la CI ne mesure pas la qualite du LLM.

## Gouvernance
Approbation humaine avant production (environnement GitHub `production`). Voir `docs/risques.md`.
