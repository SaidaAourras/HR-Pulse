import joblib
from pathlib import Path
from fastapi import HTTPException
import json


MODELS_DIR = Path("backend/app/ml/models")

def load_artifacts():
    try:
        model   = joblib.load(MODELS_DIR / "model.pkl")
        encoder = joblib.load(MODELS_DIR / "encoder.pkl")
        meta    = json.load(open(MODELS_DIR / "model_meta.json"))
        return model, encoder, meta
    except FileNotFoundError as e:
        raise HTTPException(500, detail=f"Modele manquant : {e}")