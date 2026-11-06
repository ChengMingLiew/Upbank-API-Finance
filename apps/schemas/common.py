from apps.schemas.up_model import UpModel

class Links(UpModel):
    prev: str | None = None
    next: str | None = None

class Money(UpModel):
    currency_code: str
    value_in_base_units: int

class ResourceRef(UpModel):
    type: str
    id: str