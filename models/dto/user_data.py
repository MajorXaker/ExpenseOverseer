from pydantic import BaseModel


class UserData(BaseModel):
    username: str
    user_id: int
