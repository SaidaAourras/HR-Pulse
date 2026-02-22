HR-PULSE-BACKEND/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── backend/
│   └── app/
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes_jobs.py
│       │   └── routes_predict.py
│       ├── core/
│       │   ├── __init__.py
│       │   └── config.py
│       ├── ml/
│       │   ├── predictor/
│       │   │   ├── __init__.py
│       │   │   ├── train.py
│       │   │   └── predict.py
│       │   ├── models/             ← model.pkl, encoders.pkl
│       │   └── notebooks/
│       ├── pipeline/
│       │   ├── __init__.py
│       │   ├── clean.py
│       │   ├── ner.py
│       │   └── database.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── job_service.py
│       └── __init__.py
│
├── data/
│   ├── ds-jobs.csv
│   ├── ds-jobs-clean.csv
│   └── ds-jobs-ner.csv
│
├── tests/
│   ├── test_clean.py
│   ├── test_predict.py
│   └── test_api.py
│
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── providers.tf
│   └── backend.tf
│
├── main.py                         ← FastAPI entry point
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env
└── .env.example