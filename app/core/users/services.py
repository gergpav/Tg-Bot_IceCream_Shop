from dataclasses import dataclass

from app.core.users.constants import RolesEnum
from app.core.users.repositories import UserRepository


@dataclass
class UserService:
    repository: UserRepository

    async def register_visitor(self, id: int) -> None:
        await self.repository.create_user_if_not_exists(id)

    async def get_user_ids_for_role(self, role: RolesEnum) -> list[int]:
        match role:
            case RolesEnum.waiter:
                return await self.repository.get_waiter_user_ids()
            case _:
                raise ValueError("Unable to fetch user ids for role", role)

    async def get_waiter_user_ids(self) -> list[int]:
        return await self.get_user_ids_for_role(RolesEnum.waiter)

