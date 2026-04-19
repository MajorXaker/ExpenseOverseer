from pydantic import BaseModel

from core.language.base import Translator


class UserData(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    username: str
    user_id: int
    lang: Translator
