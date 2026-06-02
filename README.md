# License Insight Scraper API

API em FastAPI para consulta de informacoes de cartas de conducao e multas, com scraping assincrono, validacao rigorosa, retries, logs estruturados e suporte a Docker.

## Funcionalidades

- API REST com FastAPI e documentacao Swagger em `/docs`.
- Scraper assincrono com HTTPX.
- Retries com backoff exponencial para falhas temporarias.
- Rotacao automatica de User-Agent.
- Suporte a proxy HTTP/SOCKS5 via variavel de ambiente.
- Validacao de entrada e saida com Pydantic v2.
- Logs estruturados com Loguru em stdout.
- Execucao local em 1 comando com venv isolado.
- Docker multi-stage pronto para producao.
- Testes com PyTest e mock do scraper externo.

## Estrutura

```text
.
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── schemas/
│   │   └── license.py
│   ├── scraper/
│   │   └── engine.py
│   └── services/
│       └── license_service.py
├── tests/
│   └── test_license_endpoint.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── main.py
├── requirements.txt
├── run.bat
└── run.sh
```

## Requisitos

- Python 3.11 ou superior.
- Docker e Docker Compose, se preferir executar em container.

## Execucao Local

Linux/macOS:

```bash
sh run.sh
```

Windows:

```bat
run.bat
```

Os scripts criam `.venv`, instalam as dependencias, geram `.env` se necessario e iniciam a API.

## Execucao com Docker

```bash
docker compose up --build
```

## URLs

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`
- Health check: `http://localhost:8000/health`

## Configuracao

As configuracoes sao carregadas de `.env`. Para criar manualmente:

```bash
cp .env.example .env
```

Windows:

```bat
copy .env.example .env
```

### Variaveis de Ambiente

| Variavel | Padrao | Descricao |
| --- | --- | --- |
| `APP_ENV` | `local` | Ambiente da aplicacao: `local`, `development`, `staging` ou `production`. |
| `APP_DEBUG` | `false` | Ativa modo debug. Use `false` em producao. |
| `APP_NAME` | `License Insight Scraper API` | Nome da aplicacao na documentacao. |
| `API_PREFIX` | `/api/v1` | Prefixo das rotas. |
| `ALLOWED_ORIGINS` | `http://localhost:8000,http://localhost:3000` | Origens CORS separadas por virgula. |
| `SCRAPER_LOGIN_URL` | URL oficial | Endpoint externo de login. |
| `SCRAPER_LICENSE_STATUS_URL` | URL oficial | Pagina externa de estado da carta. |
| `SCRAPER_DRIVING_TICKET_URL` | URL oficial | Pagina externa de multas. |
| `SCRAPER_TIMEOUT_SECONDS` | `20` | Timeout das requisicoes externas. |
| `SCRAPER_MAX_RETRIES` | `3` | Numero maximo de tentativas. |
| `SCRAPER_BACKOFF_MULTIPLIER` | `0.8` | Multiplicador do backoff exponencial. |
| `SCRAPER_PROXY_URL` | vazio | Proxy opcional. Exemplo: `http://user:pass@host:8080` ou `socks5://host:1080`. |
| `SCRAPER_VERIFY_SSL` | `true` | Verificacao SSL/TLS. |
| `LOG_LEVEL` | `INFO` | Nivel de logs: `DEBUG`, `INFO`, `WARNING`, `ERROR`. |

## Endpoint Principal

### Consultar Carta

`POST /api/v1/licenses/consult`

Request:

```json
{
  "codigo": "123456789",
  "data_nascimento": "1995-06-15"
}
```

cURL:

```bash
curl -X POST "http://localhost:8000/api/v1/licenses/consult" \
  -H "Content-Type: application/json" \
  -d '{"codigo":"123456789","data_nascimento":"1995-06-15"}'
```

Resposta:

```json
{
  "info_carta": {
    "numero_carta": "123456789",
    "nome_completo": "Joao Silva",
    "data_nascimento": "1995-06-15",
    "telefone": "+258840000000",
    "endereco": "Av. da Liberdade, Beira",
    "estado_carta": "Valida",
    "data_inicio_validade": "2020-01-01",
    "data_fim_validade": "2030-01-01",
    "classes_carta": "A, B",
    "categorias_carta": "Ligeiros, Motociclos",
    "doc_number": "A12345678",
    "pais_de_origem": "Mocambique"
  },
  "multas": []
}
```

Erro 404:

```json
{
  "detail": "Carta de conducao nao encontrada."
}
```

Erro 502:

```json
{
  "detail": "O site externo esta indisponivel no momento."
}
```

## Testes

Linux/macOS:

```bash
.venv/bin/python -m pytest
```

Windows:

```bat
.venv\Scripts\python -m pytest
```

## Producao

- Defina `APP_ENV=production` e `APP_DEBUG=false`.
- Configure `ALLOWED_ORIGINS` apenas com os dominios autorizados.
- Use `SCRAPER_PROXY_URL` quando necessario.
- Monitore latencia, erros `502` e mudancas no HTML do site externo.
