"""
Phase 2 — Extraction NER locale avec spaCy + mots-clés tech.
Aucun accès Azure requis.

Installation :
    uv add spacy pandas
    uv run python -m spacy download en_core_web_lg

Lancer :
    uv run python backend/app/pipeline/ner_local.py
"""
import json
import time

import pandas as pd
import spacy

# ── Mots-clés tech organisés par catégorie ───────────────────
TECH_SKILLS = {
    # Langages
    "python", "r", "sql", "java", "scala", "julia", "go",
    "javascript", "typescript", "c++", "c#", "matlab", "sas", "stata",

    # ML / DL
    "machine learning", "deep learning", "nlp", "computer vision",
    "reinforcement learning", "neural network", "regression",
    "classification", "clustering", "random forest", "xgboost",
    "gradient boosting", "time series", "forecasting",

    # Frameworks ML
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "huggingface", "transformers", "bert", "gpt", "llm",
    "mlflow", "mlops", "kubeflow",

    # Data
    "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    "spark", "pyspark", "hadoop", "kafka", "airflow",
    "dbt", "etl", "pipeline", "databricks", "snowflake",

    # Bases de données
    "sql server", "postgresql", "mysql", "mongodb", "redis",
    "elasticsearch", "bigquery", "redshift", "cassandra",
    "oracle", "sqlite",

    # Cloud & DevOps
    "azure", "aws", "gcp", "google cloud", "docker",
    "kubernetes", "git", "github", "gitlab", "linux",
    "bash", "terraform", "ci/cd",

    # BI / Viz
    "tableau", "power bi", "powerbi", "looker", "excel",
    "dax", "vba", "qlik",

    # API / Backend
    "fastapi", "flask", "django", "rest api", "graphql",
}


def load_spacy(model: str = "en_core_web_lg") -> spacy.language.Language:
    """Charge le modèle spaCy."""
    try:
        nlp = spacy.load(model)
        print(f" Modèle spaCy : {model}")
        return nlp
    except OSError:
        raise OSError(
            f"\n Modèle '{model}' introuvable.\n"
            f"Installez-le avec :\n"
            f"    uv run python -m spacy download {model}\n"
        )


def extract_skills(nlp: spacy.language.Language, text: str) -> list[str]:
    """
    Extrait les compétences via deux stratégies :
    1. spaCy NER  → entités ORG / PRODUCT
    2. Mots-clés  → scan de la liste TECH_SKILLS
    """
    skills = set()
    text_lower = text.lower()

    # ── Stratégie 1 : spaCy NER ─────────────────────────────
    doc = nlp(text[:50000])
    for ent in doc.ents:
        if ent.label_ in {"ORG", "PRODUCT"}:
            skill = ent.text.strip()
            if 2 <= len(skill) <= 40:
                skills.add(skill)

    # ── Stratégie 2 : Mots-clés tech ────────────────────────
    for keyword in TECH_SKILLS:
        if keyword in text_lower:
            # Formater proprement
            if len(keyword) <= 3:
                skills.add(keyword.upper())        # sql → SQL
            else:
                skills.add(keyword.title())        # python → Python

    return sorted(skills)


def run( input_csv: str = "data/ds-jobs-clean.csv", output_csv: str = "data/ds-jobs-ner.csv", ):
    """Pipeline NER complet."""

    print("  NER LOCAL — Extraction des compétences (spaCy)")

    # Charger le CSV nettoyé
    df = pd.read_csv(input_csv)
    print(f"✅ {len(df)} offres chargées depuis : {input_csv}")

    # Charger spaCy
    nlp = load_spacy()

    # Extraction
    print("\n Extraction en cours...")
    skills_list = []
    start = time.time()

    for i, text in enumerate(df["job_description_clean"]):
        skills = extract_skills(nlp, str(text))
        skills_list.append(json.dumps(skills))

        if (i + 1) % 100 == 0 or (i + 1) == len(df):
            elapsed = time.time() - start
            print(f" {i+1}/{len(df)} traitées — {elapsed:.1f}s", end="\r")

    print()

    # Ajouter la colonne
    df["skills_extracted"] = skills_list

    # Stats
    all_skills = [s for row in skills_list for s in json.loads(row)]
    print("\n=== RÉSULTATS ===")
    print(f"  Total skills extraits : {len(all_skills)}")
    print(f"  Moyenne par offre     : {len(all_skills)/len(df):.1f}")
    print(f"  Offres sans skills    : {(df['skills_extracted'] == '[]').sum()}")

    # Top 10 skills
    from collections import Counter
    top = Counter(all_skills).most_common(10)
    print("\n  Top 10 compétences :")
    for skill, count in top:
        bar = "█" * int(count / max(c for _, c in top) * 20)
        print(f"    {skill:<20} {bar} {count}")

    # Sauvegarder
    df.to_csv(output_csv, index=False)
    print(f"\n Sauvegardé : {output_csv}")
    print("=" * 55)


if __name__ == "__main__":
    import sys
    inp = sys.argv[1] if len(sys.argv) > 1 else "data/ds-jobs-clean.csv"
    out = sys.argv[2] if len(sys.argv) > 2 else "data/ds-jobs-ner.csv"
    run(inp, out)
