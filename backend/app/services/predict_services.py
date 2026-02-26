import json
from pathlib import Path
import joblib
import pandas as pd
from scipy.sparse import hstack, csr_matrix

MODELS_DIR = Path("backend/app/ml/models")


def load_artifacts():
    model       = joblib.load(MODELS_DIR / "model.pkl")
    tfidf_desc  = joblib.load(MODELS_DIR / "tfidf_desc.pkl")
    tfidf_title = joblib.load(MODELS_DIR / "tfidf_title.pkl")
    encoder     = joblib.load(MODELS_DIR / "encoder.pkl")
    meta        = json.load(open(MODELS_DIR / "model_meta.json"))
    return model, tfidf_desc, tfidf_title, encoder, meta


def predict(job_title, job_description, sector, size, type_of_ownership, state) -> dict:
    model, tfidf_desc, tfidf_title, encoder, meta = load_artifacts()

    X_desc  = tfidf_desc.transform([job_description])
    X_title = tfidf_title.transform([job_title])
    X_cat   = csr_matrix(encoder.transform(
        pd.DataFrame(
            [[sector, size, type_of_ownership, state]],
            columns=meta["cat_cols"]
        )
    ))

    X          = hstack([X_desc, X_title, X_cat])
    prediction = round(float(model.predict(X)[0]), 1)

    return {
        "predicted_salary_k": prediction,
        "mae_k":              meta["mae_k"],
        "salary_mean_k":      meta["salary_mean"],
        "salary_min_k":       meta["salary_min"],
        "salary_max_k":       meta["salary_max"],
    }