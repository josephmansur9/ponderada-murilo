"""API de inferência: carrega o modelo treinado e devolve a previsão do fechamento do BTC-USD."""
import json
import os
from datetime import date, timedelta

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

MODELS_DIR = os.getenv("MODELS_DIR", "models")
MODEL_PATH = os.path.join(MODELS_DIR, "model.joblib")
METADATA_PATH = os.path.join(MODELS_DIR, "metadata.json")

# Carrega o artefato uma única vez, na inicialização do container.
model = None
metadata = {}
if os.path.exists(MODEL_PATH) and os.path.exists(METADATA_PATH):
    model = joblib.load(MODEL_PATH)
    with open(METADATA_PATH) as f:
        metadata = json.load(f)

app = FastAPI(title="BTC-USD Predictor")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "trained_at": metadata.get("trained_at"),
    }


@app.get("/predict")
def predict():
    if model is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado. Rode o trainer primeiro.")

    # lag_1 = último fechamento, lag_2 = penúltimo, ... (mesma ordem usada no treino).
    last_closes = metadata["last_closes"]
    features = {f"lag_{i}": last_closes[-i] for i in range(1, metadata["n_lags"] + 1)}
    prediction = model.predict(pd.DataFrame([features]))[0]

    last_day = date.fromisoformat(metadata["last_date"])
    return {
        "date": str(last_day + timedelta(days=1)),
        "predicted_close_usd": round(float(prediction), 2),
        "based_on_last_day": str(last_day),
        "last_close_usd": last_closes[-1],
        "disclaimer": "Previsão experimental, não é recomendação de investimento.",
    }
