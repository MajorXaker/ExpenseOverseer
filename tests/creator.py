import random

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

import models.db_models as m


class Creator:
    user_counter = 0

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(
        self,
        full_name: str = None,
        external_id: int = None,
        username: str = None,
    ):
        if not full_name:
            self.user_counter += 1
            full_name = f"user_{random.randint(0, 1000)}"

        if not external_id:
            external_id = random.randint(0, 1000)

        user_id = await self.session.scalar(
            sa.insert(m.InternalUser)
            .values(
                {
                    m.InternalUser.name: full_name,
                    m.InternalUser.external_id: external_id,
                    m.InternalUser.username: username,
                }
            )
            .returning(m.InternalUser.id)
        )

        return user_id
