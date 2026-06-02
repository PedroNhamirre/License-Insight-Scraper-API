from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.schemas.license import ErrorResponse, LicenseQuery, LicenseResponse
from app.scraper.engine import (
    LicenseNotFoundError,
    ScraperParseError,
    UpstreamLoginRejectedError,
    UpstreamUnavailableError,
)
from app.services.license_service import LicenseService, get_license_service

router = APIRouter(prefix="/licenses", tags=["Cartas de Conducao"])


def _mask_code(code: str) -> str:
    if len(code) <= 4:
        return "****"
    return f"{code[:2]}***{code[-2:]}"


@router.post(
    "/consult",
    response_model=LicenseResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar carta de conducao",
    description=(
        "Consulta informacoes de uma carta de conducao e eventuais multas no portal externo. "
        "A operacao e assincrona, resiliente a falhas temporarias e retorna erros HTTP claros "
        "quando o site externo esta indisponivel ou muda a estrutura HTML."
    ),
    responses={
        200: {
            "description": "Consulta realizada com sucesso.",
            "content": {
                "application/json": {
                    "example": {
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
                            "pais_de_origem": "Mocambique",
                        },
                        "multas": [],
                    }
                }
            },
        },
        404: {"model": ErrorResponse, "description": "Carta nao encontrada."},
        424: {"model": ErrorResponse, "description": "O portal externo exige uma dependencia humana, como reCAPTCHA."},
        502: {"model": ErrorResponse, "description": "Falha no site externo ou no parser."},
    },
)
async def consult_license(
    payload: LicenseQuery,
    service: LicenseService = Depends(get_license_service),
) -> LicenseResponse:
    try:
        return await service.consult(payload)
    except LicenseNotFoundError as exc:
        logger.warning("License not found for codigo={}: {}", _mask_code(payload.codigo), exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UpstreamLoginRejectedError as exc:
        logger.warning("Upstream login rejected for codigo={}: {}", _mask_code(payload.codigo), exc)
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="O portal externo exige validacao humana/reCAPTCHA para concluir a consulta.",
        ) from exc
    except ScraperParseError as exc:
        logger.error("Unexpected upstream HTML structure for codigo={}: {}", _mask_code(payload.codigo), exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="A estrutura do site externo mudou ou retornou dados invalidos.",
        ) from exc
    except UpstreamUnavailableError as exc:
        logger.error("Upstream unavailable for codigo={}: {}", _mask_code(payload.codigo), exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="O site externo esta indisponivel no momento.",
        ) from exc
