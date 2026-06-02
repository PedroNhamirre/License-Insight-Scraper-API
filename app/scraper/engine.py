import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from bs4 import BeautifulSoup, Tag
from fake_useragent import UserAgent
from loguru import logger
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings, settings
from app.schemas.license import DrivingTicket, LicenseInfo, LicenseQuery, LicenseResponse


class ScraperError(Exception):
    """Base exception for scraper failures."""


class LicenseNotFoundError(ScraperError):
    """Raised when the upstream website reports invalid or missing license data."""


class UpstreamUnavailableError(ScraperError):
    """Raised when the upstream website is unavailable or unstable."""


class UpstreamLoginRejectedError(ScraperError):
    """Raised when the upstream portal rejects the login flow before validation."""


class ScraperParseError(ScraperError):
    """Raised when the upstream HTML no longer matches expected selectors."""


class LicenseScraper:
    def __init__(self, app_settings: Settings = settings) -> None:
        self.settings = app_settings
        self._user_agent = UserAgent()

    async def fetch_license(self, query: LicenseQuery) -> LicenseResponse:
        async with self._client() as client:
            await self._login(client, query)
            license_html = await self._get_html(client, str(self.settings.scraper_license_status_url))
            info = self._parse_license_info(license_html)
            tickets_html = await self._get_html(client, str(self.settings.scraper_driving_ticket_url))
            self._enrich_document_info(info, tickets_html)
            tickets = self._parse_tickets(tickets_html)
            return LicenseResponse(info_carta=info, multas=tickets)

    @asynccontextmanager
    async def _client(self) -> AsyncIterator[httpx.AsyncClient]:
        headers = {
            "User-Agent": self._random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.7",
            "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
        }
        proxy = self.settings.scraper_proxy_url
        async with httpx.AsyncClient(
            headers=headers,
            timeout=self.settings.scraper_timeout_seconds,
            proxy=proxy,
            verify=self.settings.scraper_verify_ssl,
            follow_redirects=True,
        ) as client:
            yield client

    def _random_user_agent(self) -> str:
        try:
            return str(self._user_agent.random)
        except Exception as exc:
            logger.warning("fake-useragent failed, using safe fallback: {}", exc)
            return "Mozilla/5.0 (compatible; LicenseInsightBot/1.0)"

    async def _login(self, client: httpx.AsyncClient, query: LicenseQuery) -> None:
        login_page = await self._get_html(client, str(self.settings.scraper_login_page_url))
        csrf_token = self._extract_csrf_token(login_page)
        payload = {
            "n_carta": query.codigo,
            "data_nascimento": query.data_nascimento.isoformat(),
        }
        recaptcha_token = query.recaptcha_token or self.settings.scraper_recaptcha_token
        if recaptcha_token:
            payload["g_recaptcha_response"] = recaptcha_token

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "https://balcaovirtual.inatro.gov.mz",
            "Referer": str(self.settings.scraper_login_page_url),
            "X-Requested-With": "XMLHttpRequest",
        }
        if csrf_token:
            headers["X-CSRF-Token"] = csrf_token

        response = await self._request_with_retry(
            client,
            "POST",
            str(self.settings.scraper_login_url),
            data=payload,
            headers=headers,
        )
        try:
            data = response.json()
        except ValueError as exc:
            raise ScraperParseError("A resposta de login do site externo nao e JSON valido.") from exc

        if data.get("error"):
            message = str(data.get("message") or "Carta de conducao nao encontrada.")
            if data.get("captcha_required"):
                raise UpstreamLoginRejectedError("O portal externo exigiu verificacao reCAPTCHA adicional.")
            if self._is_login_flow_rejection(message):
                raise UpstreamLoginRejectedError(message)
            raise LicenseNotFoundError(message)

    def _is_login_flow_rejection(self, message: str) -> bool:
        normalized = self._normalize(message).lower()
        return any(term in normalized for term in ("requisicao invalida", "recarregue", "captcha"))

    def _extract_csrf_token(self, html: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")
        token = soup.find("meta", attrs={"name": "csrf-token"})
        if not isinstance(token, Tag):
            return None
        content = token.get("content")
        return content.strip() if isinstance(content, str) and content.strip() else None

    async def _get_html(self, client: httpx.AsyncClient, url: str) -> str:
        response = await self._request_with_retry(client, "GET", url)
        return response.text

    async def _request_with_retry(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        **kwargs: object,
    ) -> httpx.Response:
        retryer = AsyncRetrying(
            retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)),
            wait=wait_exponential(
                multiplier=self.settings.scraper_backoff_multiplier,
                min=1,
                max=10,
            ),
            stop=stop_after_attempt(self.settings.scraper_max_retries),
            reraise=True,
        )
        try:
            async for attempt in retryer:
                with attempt:
                    response = await client.request(method, url, **kwargs)
                    response.raise_for_status()
                    return response
        except httpx.HTTPStatusError as exc:
            logger.error("Upstream HTTP error {} for {} {}", exc.response.status_code, method, url)
            raise UpstreamUnavailableError("O site externo retornou um erro HTTP.") from exc
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            logger.error("Upstream network error for {} {}: {}", method, url, exc)
            raise UpstreamUnavailableError("Nao foi possivel conectar ao site externo.") from exc

        raise UpstreamUnavailableError("Nao foi possivel concluir a requisicao ao site externo.")

    def _parse_license_info(self, html: str) -> LicenseInfo:
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find("div", class_="card-body")
        if not isinstance(card, Tag):
            raise ScraperParseError("Card principal da carta nao foi encontrado no HTML externo.")

        labels = {
            "numero_carta": "No da Carta de Conducao:",
            "nome_completo": "Nome completo:",
            "data_nascimento": "Data de nascimento:",
            "telefone": "Telefone:",
            "endereco": "Endereco:",
            "estado_carta": "Estado da carta:",
            "data_inicio_validade": "Data de inicio de validade:",
            "data_fim_validade": "Data de fim de validade:",
            "classes_carta": "Classes da Carta:",
            "categorias_carta": "Categorias da Carta:",
        }
        values = {field: self._find_value(card, label) for field, label in labels.items()}
        return LicenseInfo(**values)

    def _find_value(self, card: Tag, normalized_label: str) -> str | None:
        for title in card.find_all("h5"):
            if self._normalize(title.get_text()) == normalized_label:
                paragraph = title.find_next("p")
                return paragraph.get_text(strip=True) if paragraph else None
        return None

    def _normalize(self, value: str) -> str:
        replacements = {
            "º": "o",
            "í": "i",
            "Í": "I",
            "ç": "c",
            "Ç": "C",
            "ã": "a",
            "Ã": "A",
            "é": "e",
            "É": "E",
        }
        normalized = value.strip()
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        return normalized

    def _enrich_document_info(self, info: LicenseInfo, html: str) -> None:
        soup = BeautifulSoup(html, "html.parser")
        doc_input = soup.find("input", {"id": "dados_utente"})
        if not isinstance(doc_input, Tag):
            return

        raw_value = doc_input.get("value")
        if not isinstance(raw_value, str) or not raw_value:
            return

        try:
            data = json.loads(raw_value)
        except ValueError as exc:
            raise ScraperParseError("Campo dados_utente contem JSON invalido.") from exc

        info.doc_number = data.get("doc_number")
        extra = data.get("extra") if isinstance(data.get("extra"), dict) else {}
        info.pais_de_origem = extra.get("paisDeOrigemDescricao")

    def _parse_tickets(self, html: str) -> list[DrivingTicket]:
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        if not isinstance(table, Tag):
            return []

        tickets: list[DrivingTicket] = []
        for row in table.find_all("tr")[1:]:
            columns = [column.get_text(strip=True) for column in row.find_all("td")]
            if columns:
                tickets.append(DrivingTicket(campos=columns))
        return tickets
