"""
app.py — BharatVote Flask Web Server
Serves the frontend and handles live prediction requests.
"""

import os
import sys
import pickle
import subprocess
import numpy as np
import json
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# ── Ensure we're running from the analysis directory ─────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "saved_models")

# ── Auto-train if models are missing ─────────────────────────────
def models_exist():
    required = ["model1_safe_swing.pkl", "model2_turnout.pkl",
                "model3_winner.pkl", "encoders.pkl",
                "scaler1.pkl", "scaler2.pkl", "scaler3.pkl",
                "m1_features.pkl", "m2_features.pkl", "m3_features.pkl",
                "valid_values.pkl"]
    return all(os.path.exists(os.path.join(MODELS_DIR, f)) for f in required)

if not models_exist():
    print("[!] Models not found. Training now... (this may take ~60s)")
    train_script = os.path.join(BASE_DIR, "train.py")
    result = subprocess.run([sys.executable, train_script],
                            cwd=BASE_DIR, capture_output=False)
    if result.returncode != 0:
        print("[X] Training failed. Please run train.py manually first.")
        sys.exit(1)

# -- Load all models -----------------------------------------------
def load_pkl(name):
    with open(os.path.join(MODELS_DIR, name), "rb") as f:
        return pickle.load(f)

model1   = load_pkl("model1_safe_swing.pkl")
model2   = load_pkl("model2_turnout.pkl")
model2_m = load_pkl("model2_male.pkl")
model2_f = load_pkl("model2_female.pkl")
model3   = load_pkl("model3_winner.pkl")
scaler1  = load_pkl("scaler1.pkl")
scaler2  = load_pkl("scaler2.pkl")
scaler3  = load_pkl("scaler3.pkl")
encoders = load_pkl("encoders.pkl")
M1_FEATURES   = load_pkl("m1_features.pkl")
M2_FEATURES   = load_pkl("m2_features.pkl")
M3_FEATURES   = load_pkl("m3_features.pkl")
valid_values  = load_pkl("valid_values.pkl")

print("[OK] All models loaded successfully!")

# ── Helper: encode categorical field ─────────────────────────────
def encode_cat(col, value):
    le = encoders[col]
    value = str(value)
    if value in le.classes_:
        return int(le.transform([value])[0])
    return len(le.classes_) // 2   # fallback for unseen category

# ── Helper: build feature row ─────────────────────────────────────
def build_row(enc, feature_list):
    return np.array([float(enc.get(f, 0)) for f in feature_list]).reshape(1, -1)

# ─────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    decade_stats = {}
    stats_path = os.path.join(BASE_DIR, "decade_stats.json")
    if os.path.exists(stats_path):
        with open(stats_path, "r") as f:
            decade_stats = json.load(f)
    return render_template("index.html", valid_values=valid_values, decade_stats=decade_stats)


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)

    try:
        # ── Parse numeric inputs ──────────────────────────────────
        votes     = float(data.get("votes",     500000))
        electors  = float(data.get("electors",  900000))
        margin    = float(data.get("margin",     50000))
        marginpct = float(data.get("marginpct",  10.0))
        turnout   = float(data.get("turnout",    65.0))
        won       = int(data.get("won",          1))
        decade    = float(data.get("decade",     2010))

        # ── Parse categorical inputs ──────────────────────────────
        con_type   = data.get("con_type",   "GEN")
        region     = data.get("region",     "North")
        party_type = data.get("party_type", "National")
        alliance   = data.get("alliance",   "NDA")
        era        = data.get("era",        "NDA Era")

        # ── Build encoded dict ────────────────────────────────────
        # Extract Candidate DNA
        edu_level      = int(data.get("edu_level", 6))
        criminal_cases = int(data.get("criminal_cases", 0))
        total_assets   = float(data.get("total_assets", 10000000))

        # Build feature dict
        enc = {
            "electors":       electors,
            "turnout":        turnout,
            "decade":         decade,
            "type_enc":       encode_cat("type",       con_type),
            "region_enc":     encode_cat("region",     region),
            "party_type_enc": encode_cat("party_type", party_type),
            "alliance_enc":   encode_cat("alliance",   alliance),
            "era_enc":        encode_cat("era",        era),
            "edu_level":      edu_level,
            "criminal_cases": criminal_cases,
            "total_assets":   total_assets
        }

        # ── Prediction 1: Safe vs Swing ───────────────────────────
        r1      = scaler1.transform(build_row(enc, M1_FEATURES))
        p1_lbl  = int(model1.predict(r1)[0])
        p1_prob = model1.predict_proba(r1)[0].tolist()
        safe_swing     = "Safe"  if p1_lbl == 1 else "Swing"
        safe_prob      = round(p1_prob[1] * 100, 2)
        swing_prob     = round(p1_prob[0] * 100, 2)

        # ── Prediction 2: Voter Turnout ───────────────────────────
        r2           = scaler2.transform(build_row(enc, M2_FEATURES))
        pred_turnout = float(model2.predict(r2)[0])
        pred_turnout = round(max(20.0, min(95.0, pred_turnout)), 2)
        
        pred_male_turnout   = float(model2_m.predict(r2)[0])
        pred_male_turnout   = round(max(20.0, min(95.0, pred_male_turnout)), 2)
        
        pred_female_turnout = float(model2_f.predict(r2)[0])
        pred_female_turnout = round(max(20.0, min(95.0, pred_female_turnout)), 2)

        # ── Prediction 3: Win / Loss ──────────────────────────────
        r3      = scaler3.transform(build_row(enc, M3_FEATURES))
        p3_prob = model3.predict_proba(r3)[0].tolist()
        
        raw_win_prob  = p3_prob[1] * 100
        raw_loss_prob = p3_prob[0] * 100

        if safe_swing == "Swing":
            swing_weight = swing_prob / 100.0
            win_prob  = (raw_win_prob * (1 - swing_weight)) + (50.0 * swing_weight)
            loss_prob = (raw_loss_prob * (1 - swing_weight)) + (50.0 * swing_weight)
        else:
            win_prob  = raw_win_prob
            loss_prob = raw_loss_prob

        win_loss = "WIN" if win_prob > loss_prob else "LOSS"

        # ── EXTRA: Historical Era Comparison ──────────────────────
        era_comparison = []
        for e_name in valid_values['era']:
            temp_enc = enc.copy()
            temp_enc['era_enc'] = encode_cat("era", e_name)
            row_e = scaler3.transform(build_row(temp_enc, M3_FEATURES))
            prob_e = model3.predict_proba(row_e)[0][1] * 100
            era_comparison.append({"era": e_name, "prob": round(prob_e, 2)})
        
        return jsonify({
            "success": True,
            "safe_swing":       safe_swing,
            "safe_prob":        safe_prob,
            "swing_prob":       swing_prob,
            "predicted_turnout": pred_turnout,
            "male_turnout":      pred_male_turnout,
            "female_turnout":    pred_female_turnout,
            "win_loss":         win_loss,
            "win_prob":         round(win_prob, 2),
            "loss_prob":        round(loss_prob, 2),
            "era_comparison":   era_comparison
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/valid-values")
def get_valid_values():
    return jsonify(valid_values)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*55)
    print("  BHARATVOTE LIVE PREDICTION SERVER")
    print(f"  Open: http://localhost:{port}")
    print("="*55 + "\n")
    try:
        from waitress import serve
        print(f"  [INFO] Running on production-ready Waitress server on port {port}...")
        serve(app, host="0.0.0.0", port=port)
    except ImportError:
        print("  [WARNING] Waitress not installed. Running on development server...")
        app.run(debug=True, host="0.0.0.0", port=port)
