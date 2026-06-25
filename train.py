"""
train.py — BharatVote Model Trainer
Trains all 3 models and saves them to saved_models/ directory.
Run once before starting the web app.
"""

import warnings
warnings.filterwarnings("ignore")

import os
import pickle
import sqlite3
import numpy as np
import pandas as pd

from sklearn.preprocessing   import LabelEncoder, StandardScaler
from sklearn.ensemble        import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model    import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics         import accuracy_score, r2_score, mean_squared_error

MODELS_DIR = "saved_models"
os.makedirs(MODELS_DIR, exist_ok=True)

SEED = 42
DB   = "election.db"

# ── Try alternate DB filenames ────────────────────────────────────
if not os.path.exists(DB):
    for candidate in ["loksabha_star_schema.db", "election.db"]:
        if os.path.exists(candidate):
            DB = candidate
            break

print(f"Using database: {DB}")

# -- Load data -----------------------------------------------------
conn = sqlite3.connect(DB)

df = pd.read_sql("""
    SELECT
        f.votes,      f.electors,  f.margin,
        f.marginpct,  f.turnout,   f.won,
        c.pc_name,    c.state,     c.type,
        c.region,
        p.party,      p.party_type, p.alliance,
        y.year,       y.decade,    y.era,
        cnd.edu_level, cnd.criminal_cases, cnd.total_assets,
        t.male_turnout, t.female_turnout
    FROM   fact_election_results f
    JOIN   dim_constituency c  ON f.constituency_id = c.constituency_id
    JOIN   dim_party        p  ON f.party_id        = p.party_id
    JOIN   dim_year         y  ON f.year_id         = y.year_id
    LEFT JOIN dim_candidate cnd ON f.candidate_id   = cnd.candidate_id
    LEFT JOIN dim_turnout t ON f.turnout_id = t.turnout_id
    WHERE  c.region   IS NOT NULL
      AND  f.turnout  IS NOT NULL
      AND  f.marginpct IS NOT NULL
""", conn).dropna(subset=["type", "region", "party_type", "decade"])

conn.close()
print(f"Loaded {df.shape[0]:,} rows x {df.shape[1]} columns")

# -- Build Label Encoders ------------------------------------------
CATEGORICAL = ["type", "region", "party_type", "alliance", "era"]
encoders = {}

for col in CATEGORICAL:
    le = LabelEncoder()
    df[col + "_enc"] = le.fit_transform(df[col].fillna("Unknown"))
    encoders[col]    = le

with open(f"{MODELS_DIR}/encoders.pkl", "wb") as f:
    pickle.dump(encoders, f)

# Save valid values for frontend dropdowns
valid_values = {col: list(le.classes_) for col, le in encoders.items()}
with open(f"{MODELS_DIR}/valid_values.pkl", "wb") as f:
    pickle.dump(valid_values, f)

print("Encoders saved. Valid categorical values:")
for col, vals in valid_values.items():
    print(f"  {col:<15}: {vals}")

# =================================================================
# MODEL 1 — Safe vs Swing Classifier
# =================================================================
winners = df[df["won"] == 1].copy()
SAFE_THRESHOLD = 15.0
winners["target"] = (winners["marginpct"] >= SAFE_THRESHOLD).astype(int)

# Removed 'votes' to prevent overfitting on specific vote counts
M1_FEATURES = ["electors", "turnout",
                "type_enc", "region_enc", "party_type_enc",
                "alliance_enc", "era_enc", "decade"]

X1 = winners[M1_FEATURES].fillna(0)
y1 = winners["target"]

X1_train, X1_test, y1_train, y1_test = train_test_split(
    X1, y1, test_size=0.25, random_state=SEED, stratify=y1)

scaler1 = StandardScaler()
X1_train_s = scaler1.fit_transform(X1_train)
X1_test_s  = scaler1.transform(X1_test)

model1 = RandomForestClassifier(n_estimators=200, max_depth=12,
                                 random_state=SEED, n_jobs=-1)
model1.fit(X1_train_s, y1_train)

acc1 = accuracy_score(y1_test, model1.predict(X1_test_s))
print(f"Model 1 — Safe vs Swing | Accuracy: {acc1:.4f} ({acc1*100:.2f}%)")

with open(f"{MODELS_DIR}/model1_safe_swing.pkl", "wb") as f: pickle.dump(model1, f)
with open(f"{MODELS_DIR}/scaler1.pkl",            "wb") as f: pickle.dump(scaler1, f)
with open(f"{MODELS_DIR}/m1_features.pkl",        "wb") as f: pickle.dump(M1_FEATURES, f)

# =================================================================
# MODEL 2 — Voter Turnout Predictors
# =================================================================
M2_FEATURES = ["electors", "type_enc", "region_enc", "party_type_enc", "decade"]

# Filter out rows where male/female turnout is missing for these specific models
df2 = df.dropna(subset=["male_turnout", "female_turnout"])

X2 = df[M2_FEATURES].fillna(0)
y2_overall = df["turnout"]

# Overall Model
X2_train, X2_test, y2_train, y2_test = train_test_split(X2, y2_overall, test_size=0.2, random_state=SEED)
scaler2 = StandardScaler()
X2_train_s = scaler2.fit_transform(X2_train)
X2_test_s  = scaler2.transform(X2_test)

model2 = Ridge(alpha=1.0)
model2.fit(X2_train_s, y2_train)
print(f"Model 2 (Overall) | R2: {r2_score(y2_test, model2.predict(X2_test_s)):.4f}")

# Male Model
X2_m = df2[M2_FEATURES].fillna(0)
y2_m = df2["male_turnout"]
X2_m_train, X2_m_test, y2_m_train, y2_m_test = train_test_split(X2_m, y2_m, test_size=0.2, random_state=SEED)
model2_m = Ridge(alpha=1.0)
model2_m.fit(scaler2.transform(X2_m_train), y2_m_train)
print(f"Model 2 (Male)    | R2: {r2_score(y2_m_test, model2_m.predict(scaler2.transform(X2_m_test))):.4f}")

# Female Model
X2_f = df2[M2_FEATURES].fillna(0)
y2_f = df2["female_turnout"]
X2_f_train, X2_f_test, y2_f_train, y2_f_test = train_test_split(X2_f, y2_f, test_size=0.2, random_state=SEED)
model2_f = Ridge(alpha=1.0)
model2_f.fit(scaler2.transform(X2_f_train), y2_f_train)
print(f"Model 2 (Female)  | R2: {r2_score(y2_f_test, model2_f.predict(scaler2.transform(X2_f_test))):.4f}")

with open(f"{MODELS_DIR}/model2_turnout.pkl", "wb") as f: pickle.dump(model2, f)
with open(f"{MODELS_DIR}/model2_male.pkl",    "wb") as f: pickle.dump(model2_m, f)
with open(f"{MODELS_DIR}/model2_female.pkl",  "wb") as f: pickle.dump(model2_f, f)
with open(f"{MODELS_DIR}/scaler2.pkl",        "wb") as f: pickle.dump(scaler2, f)
with open(f"{MODELS_DIR}/m2_features.pkl",    "wb") as f: pickle.dump(M2_FEATURES, f)

# =================================================================
# MODEL 3 — Win / Loss Classifier (Gradient Boosting)
# =================================================================
# Features include "Candidate DNA" (Education, Cases, Assets)
M3_FEATURES = ["electors", "turnout",
               "type_enc", "region_enc",
               "party_type_enc", "alliance_enc",
               "era_enc", "decade",
               "edu_level", "criminal_cases", "total_assets"]

X3 = df[M3_FEATURES].fillna(0)
# Ensure numeric types for DNA features
X3["edu_level"] = pd.to_numeric(X3["edu_level"], errors="coerce").fillna(4)
X3["criminal_cases"] = pd.to_numeric(X3["criminal_cases"], errors="coerce").fillna(0)
X3["total_assets"] = pd.to_numeric(X3["total_assets"], errors="coerce").fillna(0)
y3 = df["won"]

# Oversample losers (won=0) to balance the extreme class imbalance
X3_winners = X3[y3 == 1]
X3_losers  = X3[y3 == 0]

if len(X3_losers) > 0:
    oversample_factor = len(X3_winners) // len(X3_losers)
    X3_losers_up = pd.concat([X3_losers] * oversample_factor, ignore_index=True)
    y3_losers_up = pd.Series([0] * len(X3_losers_up))
    X3_balanced = pd.concat([X3_winners, X3_losers_up], ignore_index=True)
    y3_balanced = pd.concat([pd.Series([1] * len(X3_winners)), y3_losers_up], ignore_index=True)
else:
    X3_balanced, y3_balanced = X3, y3

X3_train, X3_test, y3_train, y3_test = train_test_split(
    X3_balanced, y3_balanced, test_size=0.2, random_state=SEED, stratify=y3_balanced)

scaler3 = StandardScaler()
X3_train_s = scaler3.fit_transform(X3_train)
X3_test_s  = scaler3.transform(X3_test)

model3 = GradientBoostingClassifier(n_estimators=150, learning_rate=0.1,
                                     max_depth=5, random_state=SEED)
model3.fit(X3_train_s, y3_train)

acc3 = accuracy_score(y3_test, model3.predict(X3_test_s))
print(f"Model 3 — Win/Loss       | Accuracy: {acc3:.4f} ({acc3*100:.2f}%)")

with open(f"{MODELS_DIR}/model3_winner.pkl", "wb") as f: pickle.dump(model3, f)
with open(f"{MODELS_DIR}/scaler3.pkl",       "wb") as f: pickle.dump(scaler3, f)
with open(f"{MODELS_DIR}/m3_features.pkl",   "wb") as f: pickle.dump(M3_FEATURES, f)

print("""
====================================================
   ALL 3 MODELS SAVED to saved_models/          
      model1_safe_swing.pkl  (RandomForest)        
      model2_turnout.pkl     (Ridge Regression)    
      model3_winner.pkl      (GradientBoosting)    
====================================================
""")
