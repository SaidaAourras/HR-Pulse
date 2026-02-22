import json, sys
from pathlib import Path
import joblib, pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder


INPUT_CSV  = "data/ds-jobs-ner.csv"
MODELS_DIR = Path("backend/app/ml/models")
CAT_COLS   = ["sector", "size", "type_of_ownership", "state"]
TARGET     = "salary_avg_k"

df = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else INPUT_CSV)
for col in CAT_COLS:
    df[col] = df[col].fillna("Unknown")

# ── Features 
tfidf_desc  = TfidfVectorizer(max_features=200, stop_words="english", ngram_range=(1,2))
tfidf_title = TfidfVectorizer(max_features=50,  stop_words="english", ngram_range=(1,2))
encoder     = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)

X = hstack([
    tfidf_desc.fit_transform(df["job_description_clean"]),
    tfidf_title.fit_transform(df["job_title_clean"]),
    csr_matrix(encoder.fit_transform(df[CAT_COLS])),
])
y = df[TARGET]
print(f"Features : {X.shape} ")

# ── Split + Train 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_leaf=5, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# ── Évaluation 
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2  = r2_score(y_test, y_pred)
print(f"MAE : {mae:.1f} K$  |  R² : {r2:.3f}")

# ── Sauvegarder 
MODELS_DIR.mkdir(parents=True, exist_ok=True)
joblib.dump(model,       MODELS_DIR / "model.pkl")
joblib.dump(tfidf_desc,  MODELS_DIR / "tfidf_desc.pkl")
joblib.dump(tfidf_title, MODELS_DIR / "tfidf_title.pkl")
joblib.dump(encoder,     MODELS_DIR / "encoder.pkl")

json.dump({
    "model": "RandomForest", "cat_cols": CAT_COLS,
    "mae_k": round(mae,2), "r2": round(r2,3),
    "salary_mean": round(float(y.mean()),1),
    "salary_min":  round(float(y.min()),1),
    "salary_max":  round(float(y.max()),1),
    "categories":  {col: sorted(df[col].unique().tolist()) for col in CAT_COLS},
}, open(MODELS_DIR / "model_meta.json", "w"), indent=2)

print("Modèle sauvegardé →", MODELS_DIR)