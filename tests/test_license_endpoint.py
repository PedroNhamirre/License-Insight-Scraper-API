import pytest
from httpx import ASGITransport, AsyncClient

from app.schemas.license import LicenseInfo, LicenseQuery, LicenseResponse
from app.scraper.engine import UpstreamLoginRejectedError
from app.services.license_service import get_license_service
from main import app


class MockLicenseService:
    async def consult(self, query: LicenseQuery) -> LicenseResponse:
        return LicenseResponse(
            info_carta=LicenseInfo(
                numero_carta=query.codigo,
                nome_completo="Joao Silva",
                data_nascimento=query.data_nascimento.isoformat(),
                estado_carta="Valida",
            ),
            multas=[],
        )


class MockRejectedLoginService:
    async def consult(self, query: LicenseQuery) -> LicenseResponse:
        raise UpstreamLoginRejectedError("Requisicao invalida. Recarregue a pagina.")


@pytest.mark.asyncio
async def test_frontend_is_served() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "License Insight Scraper API" in response.text


@pytest.mark.asyncio
async def test_consult_license_endpoint_with_mocked_scraper() -> None:
    app.dependency_overrides[get_license_service] = lambda: MockLicenseService()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/licenses/consult",
            json={"codigo": "12345678", "data_nascimento": "1995-06-15"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "info_carta": {
            "numero_carta": "12345678",
            "nome_completo": "Joao Silva",
            "data_nascimento": "1995-06-15",
            "telefone": None,
            "endereco": None,
            "estado_carta": "Valida",
            "data_inicio_validade": None,
            "data_fim_validade": None,
            "classes_carta": None,
            "categorias_carta": None,
            "doc_number": None,
            "pais_de_origem": None,
        },
        "multas": [],
    }


@pytest.mark.asyncio
async def test_consult_license_accepts_pt_birth_date_format() -> None:
    app.dependency_overrides[get_license_service] = lambda: MockLicenseService()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/licenses/consult",
            json={"codigo": "12345678", "data_nascimento": "15/06/1995"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["info_carta"]["numero_carta"] == "12345678"
    assert body["info_carta"]["data_nascimento"] == "1995-06-15"


@pytest.mark.asyncio
async def test_consult_license_accepts_11_char_alphanumeric_code() -> None:
    app.dependency_overrides[get_license_service] = lambda: MockLicenseService()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/licenses/consult",
            json={"codigo": "ABC12345678", "data_nascimento": "1995-06-15"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["info_carta"]["numero_carta"] == "ABC12345678"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {"codigo": "12", "data_nascimento": "15/06/1995"},
        {"codigo": "123456789", "data_nascimento": "15/06/1995"},
        {"codigo": "AB123", "data_nascimento": "15/06/1995"},
        {"codigo": "12345678", "data_nascimento": "31/02/1995"},
        {"codigo": "12345678", "data_nascimento": "15-06-1995"},
        {"codigo": "12345678", "data_nascimento": "not-a-date"},
        {"codigo": "12345678<script>", "data_nascimento": "1995-06-15"},
        {"data_nascimento": "1995-06-15"},
        {"codigo": "12345678"},
    ],
)
async def test_consult_license_rejects_invalid_inputs(payload: dict[str, str]) -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/api/v1/licenses/consult", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_consult_license_maps_upstream_login_rejection_to_424() -> None:
    app.dependency_overrides[get_license_service] = lambda: MockRejectedLoginService()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/licenses/consult",
            json={"codigo": "12345678", "data_nascimento": "1995-06-15"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 424
    assert response.json() == {"detail": "O portal externo exige validacao humana/reCAPTCHA para concluir a consulta."}
