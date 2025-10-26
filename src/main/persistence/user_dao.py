from sqlalchemy import select, update


from domain import User
from dto import UserEntity
from exceptions import UserNotFoundError, UserAlreadyExistsError
from utils.db_helper import DatabaseHelper


class UserDAO:
    def __init__(self, db_helper: DatabaseHelper):
        self.db_helper = db_helper

    async def create(self, user: UserEntity) -> UserEntity:
        existing_user = await self.get_by_wallet_address(user.wallet_address)
        if existing_user:
            raise UserAlreadyExistsError(f"User with wallet {user.wallet_address} already exists")
        
        if user.email:
            existing_email = await self.get_by_email(user.email)
            if existing_email:
                raise UserAlreadyExistsError(f"User with email {user.email} already exists")

        user = User(
            wallet_address=user.wallet_address.lower(),
            email=user.email.lower() if user.email else None,
            remaining_chat_credits=user.remaining_chat_credits
        )
        
        async for session in self.db_helper.session_dependency():
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return self._to_entity(user)

    async def update(self, user: UserEntity) -> None:
        async for session in self.db_helper.session_dependency():
            existing_user = await session.get(User, user.id)
            if not existing_user:
                raise UserNotFoundError(f"User with id {user.id} not found")
            if user.email:
                existing_user.email = user.email.lower()
            if user.remaining_chat_credits:
                existing_user.remaining_chat_credits = user.remaining_chat_credits
            await session.commit()

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        async for session in self.db_helper.session_dependency():
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            orm = result.scalar_one_or_none()
            return self._to_entity(orm) if orm else None

    async def get_by_wallet_address(self, wallet_address: str) -> UserEntity | None:
        async for session in self.db_helper.session_dependency():
            result = await session.execute(
                select(User).where(User.wallet_address == wallet_address.lower())
            )
            orm = result.scalar_one_or_none()
            return self._to_entity(orm) if orm else None

    async def get_by_email(self, email: str) -> UserEntity | None:
        async for session in self.db_helper.session_dependency():
            result = await session.execute(
                select(User).where(User.email == email.lower())
            )
            orm = result.scalar_one_or_none()
            return self._to_entity(orm) if orm else None

    @staticmethod
    def _to_entity(user: User) -> UserEntity:
        return UserEntity(
            id=user.id,
            wallet_address=user.wallet_address,
            email=user.email,
            remaining_chat_credits=user.remaining_chat_credits,
            created_at=user.created_at,
        )
