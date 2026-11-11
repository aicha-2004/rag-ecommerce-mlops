# Dossier de reproductibilite

## Versions
| Element | Valeur (a completer) |
|---|---|
| Python | 3.11 (CI) / votre version locale : `python --version` |
| Dependances exactes | `pip freeze > requirements.lock.txt` (a committer) |
| Commit Git | `git rev-parse --short HEAD` |
| Tag du corpus | `corpus-v1` |
| Hash DVC du corpus | champ `md5` de `data/raw.dvc` |
| Modele d'embeddings | voir `params.yaml` (`embedding.model_name`) |
| LLM | voir `params.yaml` (`llm.model`), temperature 0 |

## Parametres
Tous dans `params.yaml` (chunking, embedding, retrieval, llm, quality_gate). Les parametres de
chaque run sont aussi enregistres dans MLflow, avec le tag `git_commit` et `dvc_data_hash`.

## Runs MLflow de reference
| Run | Identifiant MLflow | chunk_size | Recall@k | Exactitude |
|---|---|---|---|---|
| (a completer) | | | | |

## Procedure de reconstruction depuis zero
```cmd
git clone https://github.com/<VOTRE_USER>/rag-ecommerce-mlops.git
cd rag-ecommerce-mlops
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.lock.txt
python -m dvc pull
python -m dvc repro
```
Resultat attendu : `reports/metrics.json` avec les memes metriques que le run de reference
(embeddings et extractif deterministes ; Groq a temperature 0 peut varier legerement).

## Artefacts
`reports/metrics.json`, `reports/details.json`, `reports/failures.json`, artefacts MLflow
(params.yaml, prompt, questions), `dvc.lock`.
