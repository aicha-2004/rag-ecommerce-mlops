# Dossier de reproductibilité

## Versions

| Élément | Valeur |
|---|---|
| Python | 3.13.14 (poste de développement), 3.11 (CI GitHub Actions) |
| Dépendances | plages de versions dans `requirements.txt` et `requirements-dev.txt` ; versions exactes utilisées localement dans `requirements.lock.txt` |
| Commit Git | `0389530` |
| Tag du corpus | `corpus-v1` |
| Hash DVC du corpus | `fe76dfa8880d5c07fbe73384d2c1e934.dir` (champ `md5` de `data/raw.dvc`) |
| Modèle d'embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| LLM | Groq, `openai/gpt-oss-20b`, température 0 (`params.yaml`) |

## Paramètres

Tous dans `params.yaml` : découpage (`chunk_size` 400, `chunk_overlap` 60, stratégie `section`), embeddings, récupération (`top_k` 3, `min_score` 0,26), LLM et seuils des quality gates. Les paramètres de chaque run sont aussi enregistrés dans MLflow, avec les tags `git_commit` et `dvc_data_hash`.

## Runs MLflow de référence

| Run | Identifiant MLflow | LLM | Découpage | Recall@3 | MRR | Exactitude |
|---|---|---|---|---|---|---|
| strat_section | e72bc55977314120a8688f27353a6ed9 | extractif | section | 1,00 | 0,97 | 0,88 |
| groq_section | c6f339ad152143659b3f650bb8dc8a7b | Groq | section | 1,00 | 0,97 | 0,65 (mesure stricte) |
| dvc_repro | adaa2bc84e1c488cbbfc5c9077cda13f | extractif | section | 1,00 | 0,97 | 0,88 |

En mode extractif, l'exactitude indique si le fait attendu figure dans le contexte récupéré ; avec Groq, elle est mesurée par mots-clés dans la réponse générée.

## Procédure de reconstruction depuis zéro

```cmd
git clone https://github.com/aicha-2004/rag-ecommerce-mlops.git
cd rag-ecommerce-mlops
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m dvc pull
set LLM_PROVIDER=extractive
python -m dvc repro
```

Le serveur MLflow doit tourner (`python -m mlflow server --host 127.0.0.1 --port 5000`) ou `MLFLOW_TRACKING_URI` doit pointer vers une base locale (`sqlite:///mlflow.db`).

Résultat attendu en mode extractif (déterministe) : `reports/metrics.json` avec `recall_at_k` = 1,00, `answer_accuracy` = 0,88, `refusal_rate_oos` = 0,875 et `false_refusal_rate` = 0,00. Avec Groq (`LLM_PROVIDER=groq`, clé dans `.env`), les réponses peuvent varier légèrement d'un run à l'autre, même à température 0.

## Artefacts

`reports/metrics.json`, `reports/details.json`, `reports/failures.json`, artefacts MLflow de chaque run (`params.yaml`, prompt système, questions), `dvc.lock`.