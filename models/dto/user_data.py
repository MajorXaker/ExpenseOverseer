from pydantic import BaseModel

from core.language.base import Translator
from models.enums.currency import CurrencyEnum


class UserData(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    username: str
    user_id: int
    lang: Translator
    default_currency: CurrencyEnum
