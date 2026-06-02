from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class LicenseQuery(BaseModel):
    codigo: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[A-Za-z0-9._/-]+$",
        description="Numero/codigo da carta de conducao.",
        examples=["123456789"],
    )
    data_nascimento: date = Field(
        description="Data de nascimento associada a carta, no formato ISO YYYY-MM-DD.",
        examples=["1995-06-15"],
    )


class LicenseInfo(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    numero_carta: str | None = None
    nome_completo: str | None = None
    data_nascimento: str | None = None
    telefone: str | None = None
    endereco: str | None = None
    estado_carta: str | None = None
    data_inicio_validade: str | None = None
    data_fim_validade: str | None = None
    classes_carta: str | None = None
    categorias_carta: str | None = None
    doc_number: str | None = None
    pais_de_origem: str | None = None


class DrivingTicket(BaseModel):
    campos: list[str] = Field(default_factory=list, description="Colunas extraidas da tabela de multas.")


class LicenseResponse(BaseModel):
    info_carta: LicenseInfo
    multas: list[DrivingTicket] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    detail: str = Field(examples=["Nao foi possivel consultar a carta de conducao."])
