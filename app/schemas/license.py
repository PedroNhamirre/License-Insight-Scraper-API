from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LicenseQuery(BaseModel):
    codigo: str = Field(
        min_length=8,
        max_length=11,
        pattern=r"^[A-Za-z0-9]+$",
        description="Numero da carta com 8 digitos ou codigo alfanumerico com 11 caracteres.",
        examples=["12345678"],
    )
    data_nascimento: date = Field(
        description="Data de nascimento associada a carta. Aceita YYYY-MM-DD ou DD/MM/YYYY.",
        examples=["1995-06-15", "15/06/1995"],
    )
    recaptcha_token: str | None = Field(
        default=None,
        min_length=20,
        description="Token reCAPTCHA obtido por fluxo autorizado no cliente, quando exigido pelo portal externo.",
        exclude=True,
    )

    @field_validator("data_nascimento", mode="before")
    @classmethod
    def parse_birth_date(cls, value: object) -> object:
        if not isinstance(value, str) or "/" not in value:
            return value

        try:
            day, month, year = value.split("/")
            return date(int(year), int(month), int(day))
        except ValueError as exc:
            raise ValueError("data_nascimento deve estar em YYYY-MM-DD ou DD/MM/YYYY") from exc

    @field_validator("codigo")
    @classmethod
    def validate_code_shape(cls, value: str) -> str:
        code = value.strip().upper()
        if code.isdigit() and len(code) == 8:
            return code
        if not code.isdigit() and len(code) == 11:
            return code
        raise ValueError("codigo deve ter 8 digitos ou 11 caracteres alfanumericos")

    @field_validator("recaptcha_token", mode="before")
    @classmethod
    def empty_recaptcha_token_to_none(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


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
