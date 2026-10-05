# Predição de BTC-USD com Docker

Atividade ponderada (EC 2026, M7). Um container treina um modelo para prever o fechamento
do Bitcoin (em dólar) no dia seguinte, e um segundo container sobe uma API em Python que
carrega esse modelo e devolve a previsão.

## Documentação

| Documento | Conteúdo |
|---|---|
| [**DEVLOG.md**](DEVLOG.md) | Registro do desenvolvimento: decisões, comandos, testes, dificuldades e evidências |
| [**docs/arquitetura.md**](docs/arquitetura.md) | Diagramas UML (implantação e sequência) e as escolhas da arquitetura |

![Arquitetura](docs/img/arquitetura.svg)

## Estrutura do projeto

```
├── data/
│   ├── download_data.py   # baixa o histórico da Binance e gera o CSV
│   └── btc_usd.csv        # histórico diário de 2018-01-01 a 2026-10-04
├── trainer/               # container 1: treino
│   ├── Dockerfile
│   ├── requirements.txt
│   └── train.py
├── api/                   # container 2: API de inferência (FastAPI)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── models/                # artefato gerado pelo treino (model.joblib + metadata.json)
├── docs/                  # arquitetura e imagens
├── docker-compose.yml
└── DEVLOG.md
```

## Como rodar

Pré-requisito: Docker Desktop aberto.

```bash
docker compose up --build -d     # treina o modelo e depois sobe a API
curl localhost:8000/health       # a API está no ar?
curl localhost:8000/predict      # previsão do fechamento do dia seguinte
docker compose down              # encerra
```

Exemplo de resposta do `/predict`:
```json
{"date":"2026-10-05","predicted_close_usd":86475.51,"based_on_last_day":"2026-10-04","last_close_usd":86530.0,"disclaimer":"Previsão experimental, não é recomendação de investimento."}
```

> As previsões são experimentais e não são recomendação de investimento.
