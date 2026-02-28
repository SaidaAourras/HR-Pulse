# import json, os, sys, time
# from collections import Counter
# import pandas as pd
# from azure.ai.textanalytics import TextAnalyticsClient
# from azure.core.credentials import AzureKeyCredential
# from dotenv import load_dotenv

# load_dotenv()

# SKILL_CATEGORIES = {"Skill", "Product", "PersonType"}
# MIN_CONFIDENCE   = 0.75


# def get_client() -> TextAnalyticsClient:
#     endpoint = os.getenv("AZURE_LANGUAGE_ENDPOINT")
#     key      = os.getenv("AZURE_LANGUAGE_KEY")
#     if not endpoint or not key:
#         raise ValueError("AZURE_LANGUAGE_ENDPOINT ou AZURE_LANGUAGE_KEY manquant dans .env")
#     return TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))


# def extract_skills(client, texts, batch_size=5, sleep_sec=0.5):
#     results = []
#     for i in range(0, len(texts), batch_size):
#         batch = texts[i: i + batch_size]
#         docs  = [{"id": str(j), "text": t[:5120], "language": "en"} for j, t in enumerate(batch)]
#         try:
#             for idx, doc in enumerate(client.recognize_entities(documents=docs)):
#                 if doc.is_error:
#                     results.append(json.dumps([]))
#                 else:
#                     skills = sorted({
#                         e.text.strip() for e in doc.entities
#                         if e.category in SKILL_CATEGORIES
#                         and e.confidence_score >= MIN_CONFIDENCE
#                         and 2 <= len(e.text.strip()) <= 40
#                     })
#                     results.append(json.dumps(skills))
#         except Exception as e:
#             print(f"Erreur batch {i} : {e}")
#             results.extend([json.dumps([])] * len(batch))

#         print(f"{min(i+batch_size, len(texts))}/{len(texts)} traitees", end="\r")
#         if i + batch_size < len(texts):
#             time.sleep(sleep_sec)
#     print()
#     return results


# def run(input_csv="data/ds-jobs-clean.csv", output_csv="data/ds-jobs-ner.csv"):
#     df          = pd.read_csv(input_csv)
#     client      = get_client()
#     start       = time.time()
#     skills_list = extract_skills(client, df["job_description_clean"].tolist())
#     df["skills_extracted"] = skills_list

#     all_skills = [s for row in skills_list for s in json.loads(row)]
#     print(f"Duree        : {time.time()-start:.1f}s")
#     print(f"Total skills : {len(all_skills)}")
#     print(f"Moyenne/offre: {len(all_skills)/len(df):.1f}")
#     for skill, count in Counter(all_skills).most_common(10):
#         print(f"  {skill:<25} {count}")

#     df.to_csv(output_csv, index=False)
#     print(f"Sauvegarde : {output_csv}")


# if __name__ == "__main__":
#     run(
#         sys.argv[1] if len(sys.argv) > 1 else "data/ds-jobs-clean.csv",
#         sys.argv[2] if len(sys.argv) > 2 else "data/ds-jobs-ner.csv",
#     )


import time

import pandas as pd
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from tqdm import tqdm

import os
AZURE_LANGUAGE_KEY = os.environ.get("AZURE_LANGUAGE_KEY")
AZURE_LANGUAGE_ENDPOINT = os.environ.get("AZURE_LANGUAGE_ENDPOINT")

ENDPOINT = AZURE_LANGUAGE_ENDPOINT
KEY = AZURE_LANGUAGE_KEY

def authenticate_client():
    return TextAnalyticsClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))


def run_ner_extraction(data_path, output_path, limit=100):
    client = authenticate_client()
    df = pd.read_csv(data_path)

    # Process only the requested limit
    df_subset = df.head(limit).copy()

    all_skills = []

    print(f"Extracting skills for {limit} jobs using Azure NER...")

    # Process 1 by 1 to avoid batch limits
    for i, row in tqdm(df_subset.iterrows(), total=len(df_subset)):
        description = str(row["job_description_clean"])[:1000]  # 1000 chars
        try:
            response = client.recognize_entities([description])
            doc = response[0]
            if not doc.is_error:
                # relevant skills are in 'Skill' or 'Product' categories
                skills = [
                    entity.text
                    for entity in doc.entities
                    if entity.category in ["Skill", "Product"]
                ]
                all_skills.append(", ".join(list(set(skills))))
            else:
                all_skills.append("")
        except Exception as e:
            print(f"\nError at row {i}: {e}")
            all_skills.append("")

        # Free tier pause
        time.sleep(1.0)

    df_subset["extracted_skills"] = all_skills
    df_subset.to_csv(output_path, index=False)
    print(f"\nExtraction complete. Saved {len(df_subset)} records to {output_path}")


if __name__ == "__main__":
    run_ner_extraction("data/ds-jobs-ner.csv", "data/dataset_with_skills.csv", limit=100)
