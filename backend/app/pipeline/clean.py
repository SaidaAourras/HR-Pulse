import re
import numpy as np
import pandas as pd


def parse_salary(s: str) -> float:
    """Convertit '$137K-$171K (Glassdoor est.)' en valeur moyenne numérique (154.0)."""
    numbers = re.findall(r"[$](\d+)K", str(s))
    if len(numbers) >= 2:
        return (int(numbers[0]) + int(numbers[1])) / 2
    return np.nan


def load_and_clean(filepath: str) -> pd.DataFrame:
    """
    Charge et nettoie le fichier ds-jobs.csv.

    Transformations :
    - Supprime les colonnes inutiles (index, Competitors)
    - Remplace les valeurs -1 par NaN
    - Nettoie Company Name (retire le rating collé)
    - Normalise Job Title (strip + title case)
    - Parse Salary Estimate en valeur numérique moyenne
    - Réinitialise l'index en id propre (commence à 1)

    Returns:
        pd.DataFrame nettoyé
    """
    df = pd.read_csv(filepath)

    # ── 1. Supprimer colonnes inutiles ──────────────────────
    cols_to_drop = [col for col in ["index", "Competitors"] if col in df.columns]
    df.drop(columns=cols_to_drop, inplace=True)

    # ── 2. Remplacer toutes les valeurs -1 par NaN ──────────
    df.replace("-1", np.nan, inplace=True)
    df.replace(-1, np.nan, inplace=True)
    df.replace(-1.0, np.nan, inplace=True)

    # ── 3. Nettoyer Company Name ────────────────────────────
    # Exemple : "Healthfirst\n3.1" → "Healthfirst"
    if "Company Name" in df.columns:
        df["Company Name"] = df["Company Name"].str.split("\n").str[0].str.strip()

    # ── 4. Normaliser Job Title ─────────────────────────────
    if "Job Title" in df.columns:
        df["Job Title"] = df["Job Title"].str.strip().str.title()

    # ── 5. Nettoyer Job Description et Location ─────────────
    if "Job Description" in df.columns:
        df["Job Description"] = df["Job Description"].str.strip()

    if "Location" in df.columns:
        df["Location"] = df["Location"].str.strip()

    # ── 6. Size : unifier "Unknown" avec NaN ────────────────
    if "Size" in df.columns:
        df["Size"] = df["Size"].replace("Unknown", np.nan)

    # ── 7. Founded : convertir en numérique ─────────────────
    if "Founded" in df.columns:
        df["Founded"] = pd.to_numeric(df["Founded"], errors="coerce")

    # ── 8. Salary Avg : parser Salary Estimate ──────────────
    if "Salary Estimate" in df.columns:
        df["Salary Avg"] = df["Salary Estimate"].apply(parse_salary)

    # ── 9. Reset index propre → id (commence à 1) ───────────
    df.reset_index(drop=True, inplace=True)
    df.index = df.index + 1
    df.index.name = "id"
    df = df.reset_index()

    return df


def save_cleaned(df: pd.DataFrame, output_path: str) -> None:
    """Sauvegarde le DataFrame nettoyé en CSV."""
    df.to_csv(output_path, index=False)
    print(f"✅ Fichier sauvegardé : {output_path}")


def print_report(df: pd.DataFrame) -> None:
    """Affiche un rapport de qualité après nettoyage."""
    print("=" * 50)
    print("RAPPORT DE NETTOYAGE")
    print("=" * 50)
    print(f"Shape        : {df.shape[0]} lignes × {df.shape[1]} colonnes")
    print(f"Doublons     : {df.duplicated().sum()}")
    print()
    print("--- Valeurs nulles par colonne ---")
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    print(nulls if not nulls.empty else "Aucune valeur nulle ✅")
    print()
    if "Salary Avg" in df.columns:
        print("--- Salary Avg (en K$) ---")
        print(df["Salary Avg"].describe().round(1))
    print("=" * 50)


if __name__ == "__main__":
    INPUT_PATH = "data/ds-jobs-.csv"
    OUTPUT_PATH = "data/ds-jobs-cleaned.csv"

    print("🔄 Chargement et nettoyage en cours...")
    df = load_and_clean(INPUT_PATH)
    print_report(df)
    save_cleaned(df, OUTPUT_PATH)
