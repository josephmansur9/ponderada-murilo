"""Treina um modelo para prever o fechamento do BTC-USD no dia seguinte (D+1).

Entrada:  data/btc_usd.csv
Saída:    models/model.joblib + models/metadata.json
"""
import json
import os
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

DATA_PATH = os.getenv("DATA_PATH", "data/btc_usd.csv")
MODELS_DIR = os.getenv("MODELS_DIR", "models")
N_LAGS = int(os.getenv("N_LAGS", "7"))
TEST_SIZE = float(os.getenv("TEST_SIZE", "0.2"))


def build_features(closes: pd.Series, n_lags: int) -> pd.DataFrame:
    """Cada linha: fechamentos dos últimos n_lags dias (lag_1 = ontem) -> fechamento de hoje (target)."""
    df = pd.DataFrame({"target": closes})
    for i in range(1, n_lags + 1):
        df[f"lag_{i}"] = closes.shift(i)
    return df.dropna()


def evaluate(y_true, y_pred) -> dict:
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 2),
        "rmse": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 2),
    }


def main():
    raw = pd.read_csv(DATA_PATH, parse_dates=["Date"]).sort_values("Date")
    closes = raw.set_index("Date")["Close"]
    print(f"Dados: {len(closes)} dias ({closes.index.min().date()} a {closes.index.max().date()})")

    df = build_features(closes, N_LAGS)
    feature_cols = [f"lag_{i}" for i in range(1, N_LAGS + 1)]

    # Split cronológico: o teste é sempre o período mais recente (sem embaralhar).
    split = int(len(df) * (1 - TEST_SIZE))
    train, test = df.iloc[:split], df.iloc[split:]
    print(f"Treino: {train.index.min().date()} a {train.index.max().date()} ({len(train)} linhas)")
    print(f"Teste:  {test.index.min().date()} a {test.index.max().date()} ({len(test)} linhas)")

    model = LinearRegression()
    model.fit(train[feature_cols], train["target"])

    metrics = {
        "model": evaluate(test["target"], model.predict(test[feature_cols])),
        # Baseline ingênuo: amanhã fecha igual a hoje. O modelo precisa ser comparado com isso.
        "naive_baseline": evaluate(test["target"], test["lag_1"]),
    }
    print(f"Métricas no teste (USD): {json.dumps(metrics)}")

    # Retreina com todos os dados para a versão final que vai para a API.
    model.fit(df[feature_cols], df["target"])

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODELS_DIR, "model.joblib"))

    metadata = {
        "model_type": "LinearRegression",
        "target": "close do dia seguinte (USD)",
        "n_lags": N_LAGS,
        "features": feature_cols,
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_range": [str(closes.index.min().date()), str(closes.index.max().date())],
        "metrics_test": metrics,
        # Últimos N fechamentos, do mais antigo ao mais recente: entrada usada pela API no GET /predict.
        "last_date": str(closes.index.max().date()),
        "last_closes": [float(c) for c in closes.iloc[-N_LAGS:]],
    }
    with open(os.path.join(MODELS_DIR, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"Artefato salvo em {MODELS_DIR}/model.joblib e {MODELS_DIR}/metadata.json")


if __name__ == "__main__":
    main()
