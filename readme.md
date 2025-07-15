## Laboratório de estudos de OpenTelemetry

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Grafana](https://img.shields.io/badge/grafana-%23F46800.svg?style=for-the-badge&logo=grafana&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=Prometheus&logoColor=white)
![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-FFFFFF?&style=for-the-badge&logo=opentelemetry&logoColor=black)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

Este repositório demonstra duas abordagens para instrumentar aplicações FastAPI com observabilidade usando OpenTelemetry: manual e automática. A infraestrutura completa é provisionada via Docker Compose.

---

## 📁 Estrutura do Projeto
````
.
├── fastapi-app/    # FastAPI com instrumentação manual
├── fastapi-auto/   # FastAPI com auto-instrumentação
├── infraestrutura/ # Toda stack de observabilidade - Prometheus, Grafana, Jaeger e OpenTelemetry
└── locust/         # Locust para testes de carga e gerar dados para nosso dashboard
`````

Dentro de cada pasta tem um docker-compose.yaml para subir a aplicação

##  Fastapi-app — Instrumentação Manual

### Descrição
Aplicação FastAPI com instrumentação feita diretamente no código-fonte usando os SDKs do OpenTelemetry.

### Destaques
- Instrumentação de código com `opentelemetry-sdk`.
- Exportação de métricas para Prometheus.
- Exportação de traces para Jaeger.
- Rota de exemplo: `GET /`.

### Componentes
- `app.py`: aplicação com middleware e métricas instrumentadas.
- `otel-collector-config.yaml`: configuração do OTEL Collector.
- `prometheus.yml`: scrape config do Prometheus.


##  Fastapi-auto — Instrumentação Automatica

### Descrição
Aplicação FastAPI com instrumentação feita diretamente no código-fonte usando os SDKs do OpenTelemetry.

### Destaques
- Instrumentação de código com `opentelemetry-sdk`.
- Exportação de métricas para Prometheus.
- Exportação de traces para Jaeger.
- Rota de exemplo: `GET /`.

## 📊 Acessos rápidos
Jaeger: http://localhost:16686

Prometheus: http://localhost:9090

Grafana: http://localhost:3000 (usuário: admin / senha: admin)

Métricas FastAPI (manual): http://localhost:8000/metrics

Métricas FastAPI (automatica): http://localhost:8001/metrics