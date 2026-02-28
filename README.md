# HR-Pulse — Backend

> API REST de prédiction salariale et d'analyse du marché Data Science, construite avec FastAPI et déployée via Docker.

---

## Table des matières

- [Présentation](#présentation)
- [Stack technique](#stack-technique)
- [Architecture](#architecture)
- [Installation](#installation)
- [Pipeline de données](#pipeline-de-données)
- [API Endpoints](#api-endpoints)
- [Modèle ML](#modèle-ml)
- [Tests](#tests)
- [Docker](#docker)
- [CI/CD](#cicd)
- [Variables d'environnement](#variables-denvironnement)

---

## Présentation

HR-Pulse automatise l'analyse des offres d'emploi Data Science. À partir de 672 offres réelles collectées sur Glassdoor, il permet de :

- **Rechercher** des offres par compétence (Python, SQL, Azure, etc.)
- **Identifier** les compétences les plus demandées sur le marché
- **Prédire** le salaire compétitif pour un profil donné grâce à un modèle RandomForest

**Problème résolu :** Une recruteuse passait 3–4 heures par semaine à analyser manuellement des offres et proposait des salaires basés sur l'intuition. HR-Pulse réduit ce travail à quelques secondes avec des données réelles.

---

## Stack technique

| Composant | Technologie |
|---|---|
| API | FastAPI 0.133+ |
| Base de données | PostgreSQL (dev) / Azure SQL (prod) |
| ORM | SQLAlchemy 2.0 |
| ML | scikit-learn — RandomForestRegressor |
| NLP | spaCy `en_core_web_lg` + Azure AI Language |
| Auth | JWT (python-jose) + bcrypt (pwdlib) |
| Package manager | uv |
| Conteneurisation | Docker + Docker Compose |
| Tests | Pytest + httpx |
| Linting | Ruff |
| CI/CD | GitHub Actions |

---

## Architecture

```
backend/app/
├── api/
│   ├── db/
│   │   ├── models/       ← SQLAlchemy ORM (Job, User)
│   │   ├── schemas/      ← Pydantic v2 (JobResponse, PredictRequest)
│   │   └── database.py   ← engine + get_db()
│   └── routes/
│       ├── auth.py       ← POST /auth/register, /login, /logout
│       ├── jobs.py       ← GET  /jobs/, /search/, /skills/top/, /{id}
│       └── predict.py    ← POST /predict/
├── ml/
│   ├── models/           ← artifacts .pkl + model_meta.json
│   ├── notebooks/        ← exploration, cleaning, feature eng, training
│   └── predictor/        ← train.py + predict.py
├── pipeline/
│   ├── clean.py          ← nettoyage du CSV brut
│   ├── ner_local.py      ← extraction NER avec spaCy
│   ├── ner_azure.py      ← extraction NER avec Azure AI Language
│   └── database_inject.py← injection CSV → PostgreSQL
├── services/             ← logique métier (auth, jobs, predict, users)
└── utils/
    └── hashing.py        ← bcrypt password hashing
```

---

## Installation

### Prérequis

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) installé
- PostgreSQL (local) ou accès Azure SQL

### Étapes

```bash
# 1. Cloner le repo
git clone https://github.com/SaidaAourras/HR-Pulse_backend.git
cd HR-Pulse_backend

# 2. Installer les dépendances API
uv sync

# 3. Installer les dépendances pipeline (NER, notebooks)
uv sync --all-extras

# 4. Configurer les variables d'environnement
cp .env.example .env
# Remplir DATABASE_URL, SECRET_KEY, etc.

# 5. Lancer l'API
uv run uvicorn main:app --reload --port 8000
```

API disponible sur : `http://localhost:8000/docs`

---

## Pipeline de données

Le pipeline se lance en 3 étapes avant de démarrer l'API :

```bash
# Étape 1 — Nettoyage du CSV brut
uv run python backend/app/pipeline/clean.py
# Input  : data/ds_jobs.csv
# Output : data/ds-jobs-clean.csv

# Étape 2 — Extraction NER (spaCy local)
uv run python backend/app/pipeline/ner_local.py
# Input  : data/ds-jobs-clean.csv
# Output : data/ds-jobs-ner.csv (+ colonne skills_extracted)

# Étape 3 — Injection dans PostgreSQL
uv run python backend/app/pipeline/database_inject.py
# Injecte 672 offres dans la table jobs (id, job_title, skills_extracted)

# Étape 4 — Entraînement du modèle ML
uv run python backend/app/ml/predictor/train.py
# Output : backend/app/ml/models/ (model.pkl, tfidf_desc.pkl, tfidf_title.pkl, encoder.pkl, model_meta.json)
```

---

## API Endpoints

Tous les endpoints `/jobs/` et `/predict/` sont protégés par JWT.

### Authentification

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Créer un compte |
| POST | `/auth/login` | Obtenir un token JWT |
| POST | `/auth/logout` | Déconnexion |

### Jobs

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/jobs/` | Liste paginée `?page=1&limit=20` |
| GET | `/jobs/{id}` | Détail d'une offre |
| GET | `/jobs/search/?skill=Python` | Recherche par compétence |
| GET | `/jobs/skills/top/?n=20` | Top N compétences du marché |

### Prédiction

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/predict/` | Prédiction de salaire |

**Body `/predict/` :**
```json
{
  "job_title":         "Senior Data Scientist",
  "job_description":   "Python, Azure, MLOps, 5 ans d'expérience...",
  "sector":            "Information Technology",
  "size":              "51 to 200 employees",
  "type_of_ownership": "Company - Private",
  "state":             "CA"
}
```

**Réponse :**
```json
{
  "predicted_salary_k": 138.5,
  "mae_k":              27.2,
  "salary_mean_k":      112.0,
  "salary_min_k":       45.0,
  "salary_max_k":       210.0
}
```

---

## Modèle ML

Le modèle `RandomForestRegressor` prédit le salaire moyen en K$ à partir de **254 features** :

| Features | Nombre | Description |
|---|---|---|
| TF-IDF description | 200 | Mots-clés de la description du poste |
| TF-IDF titre | 50 | Mots-clés du titre du poste |
| Catégoriels encodés | 4 | sector, size, type_of_ownership, state |

**Performance :** MAE ≈ 27.2 K$ sur 134 offres de test (20% holdout).

---

## Tests

```bash
# Lancer tous les tests
uv run pytest tests/ -v

# Avec coverage
uv run pytest tests/ -v --cov=backend
```

**13 tests unitaires :**
- `test_routes_jobs.py` — 7 tests (list, pagination, get by id, 404, search, top skills)
- `test_routes_predict.py` — 6 tests (200, champs, type, fourchette, 422, secteur inconnu)

Les tests utilisent une base SQLite en mémoire — aucune connexion PostgreSQL requise.

---

## Docker

```bash
# Build + lancer tous les services
docker-compose up --build

# Services disponibles
# http://localhost:8000  ← API FastAPI
# http://localhost:3000  ← Frontend NextJS
# http://localhost:16686 ← Jaeger (observabilité)
```

**Services docker-compose :**

| Service | Image | Port |
|---|---|---|
| `backend` | Dockerfile (multi-stage) | 8000 |
| `db` | postgres:15-alpine | 5432 |
| `frontend` | Dockerfile.frontend | 3000 |
| `jaeger` | jaegertracing/all-in-one | 16686 |

---

## CI/CD

Pipeline GitHub Actions en 3 jobs séquentiels (`.github/workflows/ci.yml`) :

```
git push
    │
    ▼
Job 1 : Ruff       → vérification qualité du code Python
    │ (si OK)
    ▼
Job 2 : Pytest     → 13 tests unitaires
    │ (si OK)
    ▼
Job 3 : Docker     → build de l'image hr-pulse-backend
```

---

## Variables d'environnement

Copiez `.env.example` en `.env` et remplissez :

```env
# Base de données
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/hr_pulse

# JWT
SECRET_KEY=votre-secret-key-tres-long
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Azure AI Language (pipeline NER uniquement)
AZURE_LANGUAGE_ENDPOINT=https://votre-resource.cognitiveservices.azure.com/
AZURE_LANGUAGE_KEY=votre-cle-azure
```
