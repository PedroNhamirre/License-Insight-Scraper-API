import pytest
from httpx import ASGITransport, AsyncClient

from app.schemas.license import LicenseInfo, LicenseQuery, LicenseResponse
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


@pytest.mark.asyncio
async def test_consult_license_endpoint_with_mocked_scraper() -> None:
    app.dependency_overrides[get_license_service] = lambda: MockLicenseService()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/licenses/consult",
            json={"codigo": "123456789", "data_nascimento": "1995-06-15"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "info_carta": {
            "numero_carta": "123456789",
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
