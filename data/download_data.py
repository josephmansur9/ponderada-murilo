"""Baixa o histórico diário de BTC/USDT da API pública da Binance e salva em CSV.

Uso: python3 data/download_data.py
Não requer chave de API nem bibliotecas externas.
"""
import csv
import json
import os
import urllib.request
from datetime import datetime, timezone

SYMBOL = "BTCUSDT"
INTERVAL = "1d"
START = datetime(2018, 1, 1, tzinfo=timezone.utc)
URL = "https://api.binance.com/api/v3/klines?symbol={s}&interval={i}&startTime={t}&limit=1000"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "btc_usd.csv")


def fetch_all():
    rows = []
    start_ms = int(START.timestamp() * 1000)
    while True:
        with urllib.request.urlopen(URL.format(s=SYMBOL, i=INTERVAL, t=start_ms)) as resp:
            batch = json.load(resp)
        if not batch:
            break
        rows.extend(batch)
        start_ms = batch[-1][0] + 1
        if len(batch) < 1000:
            break
    return rows


def main():
    klines = fetch_all()
    today = datetime.now(timezone.utc).date()
    with open(OUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        for k in klines:
            date = datetime.fromtimestamp(k[0] / 1000, tz=timezone.utc).date()
            if date >= today:  # descarta o candle do dia atual (ainda não fechou)
                continue
            writer.writerow([date.isoformat(), k[1], k[2], k[3], k[4], k[5]])
    print(f"{len(klines)} candles baixados -> {OUT}")


if __name__ == "__main__":
    main()
