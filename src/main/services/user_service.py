import json

from dto import UserEntity, UserProfile
from persistence import UserDAO
from exceptions import UserNotFoundError, UserEmailAlreadyExistsError, MCPResponseError
from clients import MCPClient
from utils.portfolio_utils import json_to_user_profile


class UserService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(UserService, cls).__new__(cls)
        return cls._instance

    def __init__(self, user_dao: UserDAO):
        if not hasattr(self, '_initialized'):
            self.user_dao = user_dao
            self._initialized = True

    @classmethod
    def initialize(cls, user_dao: UserDAO):
        if cls._instance:
            raise RuntimeError("UserService is already initialized. Use get_instance() to access it.")
        instance = cls.__new__(cls)
        instance.__init__(user_dao=user_dao)
        cls._instance = instance

    @classmethod
    def get_instance(cls) -> 'UserService':
        if cls._instance is None:
            raise RuntimeError("UserService not initialized. Call initialize() first.")
        return cls._instance

    async def get_user_by_id(self, user_id: int) -> UserEntity:
        user = await self.user_dao.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return user

    async def get_user_by_wallet(self, wallet_address: str) -> UserEntity:
        user = await self.user_dao.get_by_wallet_address(wallet_address)
        if not user:
            raise UserNotFoundError(f"User with wallet {wallet_address} not found")
        return user

    async def add_email(self, user_id: int, email: str) -> None:
        user = await self.user_dao.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        if user.email:
            raise UserEmailAlreadyExistsError("User already has set email")
        user.email = email
        await self.user_dao.update(user)

    async def update_balance_by_id(self, user_id: int, delta: float) -> float:
        user = await self.user_dao.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        if delta == 0:
            return user.remaining_chat_credits
        user.remaining_chat_credits += delta
        await self.user_dao.update(user)
        return user.remaining_chat_credits

    async def update_balance_by_wallet(self, wallet_address: str, delta: float) -> float:
        user = await self.user_dao.get_by_wallet_address(wallet_address)
        if not user:
            raise UserNotFoundError(f"User with wallet {wallet_address} not found")
        if delta == 0:
            return user.remaining_chat_credits
        user.remaining_chat_credits += delta
        await self.user_dao.update(user)
        return user.remaining_chat_credits

    @staticmethod
    async def get_user_profile(wallet_address: str) -> UserProfile:
        mcp_client = MCPClient()
        await mcp_client.setup_default_providers()
        try:
            raw_data = await mcp_client.execute_tool(
                "opensea_get_profile",
                {
                    'address': wallet_address,
                    'includes': [
                        'items',
                        'collections',
                        'activity',
                        'listings',
                        'offers',
                        'offers_received',
                        'balances'
                    ]
                }
            )
            data = json.loads(raw_data[0].text)
        except Exception as e:
            raise MCPResponseError(f"Failed to opensea_get_profile: {e}")
        return json_to_user_profile(data)
