# License Insight Scraper API

O portal externo usa reCAPTCHA no fluxo de login. Esta API nao tenta contornar esse mecanismo. Quando a validacao humana for exigida, o endpoint retorna `424 Failed Dependency` e interrompe a consulta de forma segura. Para uso em producao, solicite acesso oficial, whitelisting ou um canal de integracao autorizado ao proprietario do portal.

API em FastAPI para consulta de dados de cartas de conducao e multas, com scraper assincrono, validacao com Pydantic, retries, logs estruturados e Docker.

## Recursos

- API REST com documentacao em `/docs`.
- Frontend simples em `/` para testes locais.
- Scraper assincrono com HTTPX.
- Retries com backoff exponencial.
- Rotacao de User-Agent.
- Suporte a proxy HTTP/SOCKS5.
- Fallback explicito para reCAPTCHA com status `424`.
- Logs estruturados com Loguru.
- Execucao local em 1 comando.
- Docker multi-stage.
- Testes automatizados com PyTest.

## Estrutura

```text
.
├── app/
│   ├── api/routes.py
│   ├── core/config.py
│   ├── core/logging.py
│   ├── schemas/license.py
│   ├── scraper/engine.py
│   └── services/license_service.py
├── frontend/index.html
├── tests/test_license_endpoint.py
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
- Docker Desktop, se for usar Docker.

## Executar Localmente

Windows PowerShell:

```powershell
.\run.bat
```

Linux/macOS:

```bash
sh run.sh
```

Os scripts criam `.venv`, instalam dependencias, criam `.env` se necessario e iniciam a API.

## Executar com Docker

Abra o Docker Desktop e execute:

```bash
docker compose up --build
```

## URLs

- Frontend: `http://localhost:8000/`
- Swagger: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- OpenAPI: `http://localhost:8000/openapi.json`

## Endpoint

`POST /api/v1/licenses/consult`

Request:

```json
{
  "codigo": "12345678",
  "data_nascimento": "15/06/1995"
}
```

Com token reCAPTCHA obtido por fluxo autorizado:

```json
{
  "codigo": "12345678",
  "data_nascimento": "1995-06-15",
  "recaptcha_token": "TOKEN_VALIDO_GERADO_PELO_CLIENTE_AUTORIZADO"
}
```

cURL:

```bash
curl -X POST "http://localhost:8000/api/v1/licenses/consult" \
  -H "Content-Type: application/json" \
  -d '{"codigo":"12345678","data_nascimento":"15/06/1995"}'
```

Resposta de sucesso:

```json
{
  "info_carta": {
    "numero_carta": "12345678",
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

Fallback reCAPTCHA:

```json
{
  "detail": "O portal externo exige validacao humana/reCAPTCHA para concluir a consulta."
}
```

## Formatos Aceitos

- `codigo`: 8 digitos ou 11 caracteres alfanumericos.
- `data_nascimento`: `YYYY-MM-DD` ou `DD/MM/YYYY`.

## Variaveis de Ambiente

| Variavel | Descricao |
| --- | --- |
| `APP_ENV` | Ambiente da aplicacao. |
| `APP_DEBUG` | Modo debug. Use `false` em producao. |
| `API_PREFIX` | Prefixo das rotas. Padrao: `/api/v1`. |
| `ALLOWED_ORIGINS` | Origens CORS separadas por virgula. |
| `SCRAPER_LOGIN_PAGE_URL` | Pagina de login usada para cookies e CSRF. |
| `SCRAPER_LOGIN_URL` | Endpoint AJAX de login. |
| `SCRAPER_LICENSE_STATUS_URL` | Pagina de estado da carta. |
| `SCRAPER_DRIVING_TICKET_URL` | Pagina de multas. |
| `SCRAPER_PROXY_URL` | Proxy HTTP/SOCKS5 opcional. |
| `SCRAPER_RECAPTCHA_TOKEN` | Token reCAPTCHA opcional para integracoes autorizadas. |
| `SCRAPER_TIMEOUT_SECONDS` | Timeout das requisicoes externas. |
| `SCRAPER_MAX_RETRIES` | Numero maximo de tentativas. |
| `LOG_LEVEL` | Nivel de logs. |

## Testes

Windows:

```powershell
.\.venv\Scripts\python -m pytest
```

Linux/macOS:

```bash
.venv/bin/python -m pytest
```

## Integracao Oficial

Para uso comercial ou publico, o caminho recomendado e solicitar ao proprietario do portal um metodo oficial de integracao, como API, credenciais dedicadas, whitelisting, ambiente sandbox ou contrato de dados. Isso evita instabilidade, bloqueios anti-bot e riscos operacionais.
