import os

from dotenv import load_dotenv

from backend.app.pipeline.clean import load_and_clean
from backend.app.pipeline.database import check_data, create_table, get_engine, insert_jobs
from backend.app.pipeline.ner import extract_skills_batch, get_client

# Charger les variables d'environnement depuis .env
load_dotenv()


def run(csv_path: str = "data/ds-jobs-.csv") -> None:
    """
    Pipeline complet Phase 2 :
      1. Nettoyage du CSV
      2. Extraction NER via Azure AI Language
      3. Injection dans Azure SQL
    """

    # ── ÉTAPE 1 : Nettoyage ─────────────────────────────────
    print("\n" + "=" * 55)
    print("  ÉTAPE 1 — Chargement et nettoyage du CSV")
    print("=" * 55)

    df = load_and_clean(csv_path)
    print(f"✅ {len(df)} offres chargées et nettoyées.")
    print(f"   Colonnes : {df.columns.tolist()}")

    # ── ÉTAPE 2 : Extraction NER ────────────────────────────
    print("\n" + "=" * 55)
    print("  ÉTAPE 2 — Extraction des compétences (Azure NER)")
    print("=" * 55)

    client = get_client()
    descriptions = df["Job Description"].tolist()

    print(f"🔄 Traitement de {len(descriptions)} descriptions...")
    skills_list = extract_skills_batch(client, descriptions)
    df["skills_extracted"] = skills_list

    # Afficher un aperçu
    print("\nAperçu des compétences extraites (5 premières) :")
    for i in range(min(5, len(df))):
        title = df["Job Title"].iloc[i]
        skills = df["skills_extracted"].iloc[i]
        print(f"  [{i+1}] {title[:40]:<40} → {skills[:80]}")

    # ── ÉTAPE 3 : Injection Azure SQL ───────────────────────
    print("\n" + "=" * 55)
    print("  ÉTAPE 3 — Injection dans Azure SQL")
    print("=" * 55)

    engine = get_engine()
    create_table(engine)

    # Préparer les records avec uniquement les colonnes nécessaires
    records = (
        df[["id", "Job Title", "skills_extracted"]]
        .rename(columns={"Job Title": "job_title"})
        .to_dict(orient="records")
    )

    insert_jobs(engine, records)
    check_data(engine, limit=5)

    print("\n" + "=" * 55)
    print("  ✅ PHASE 2 TERMINÉE AVEC SUCCÈS")
    print("=" * 55)


if __name__ == "__main__":
    CSV_PATH = os.getenv("CSV_PATH", "data/ds_jobs.csv")
    run(CSV_PATH)