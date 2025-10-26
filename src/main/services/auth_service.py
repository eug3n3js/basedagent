from .user_service import UserService
from clients import EmailClient, RedisClient
from constants import SIGN_MESSAGE
from dto import UserEntity
from dto import WalletAuthRequest, SendEmailCodeRequest, VerifyEmailCodeRequest, TokenResponse
from exceptions import EmailError
from persistence import UserDAO
from utils.helpers import generate_unique_digit_code
from utils.jwt_utils import create_access_token, decode_jwt
from exceptions import WalletSignatureError, InvalidCredentialsError, InvalidVerificationCodeError
from exceptions import UserAlreadyExistsError
from utils.wallet_utils import verify_signature, is_valid_ethereum_address


class AuthService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AuthService, cls).__new__(cls)
        return cls._instance

    def __init__(self, user_dao: UserDAO, email_client: EmailClient, redis_client: RedisClient):
        if not hasattr(self, '_initialized'):
            self.user_dao = user_dao
            self.email_client = email_client
            self.redis_client = redis_client
            self._initialized = True

    @classmethod
    def initialize(cls, user_dao: UserDAO, email_client: EmailClient, redis_client: RedisClient):
        if cls._instance:
            raise RuntimeError("AuthService is already initialized. Use get_instance() to access it.")
        instance = cls.__new__(cls)
        instance.__init__(user_dao=user_dao, email_client=email_client, redis_client=redis_client)
        cls._instance = instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("AuthService not initialized. Call initialize() first.")
        return cls._instance

    async def authenticate(self, auth_request: WalletAuthRequest) -> TokenResponse:
        if not is_valid_ethereum_address(auth_request.wallet_address):
            raise InvalidCredentialsError("Invalid wallet address format")

        if not verify_signature(
            auth_request.wallet_address,
            SIGN_MESSAGE,
            auth_request.signature
        ):
            raise WalletSignatureError("Invalid wallet signature")

        user = await self.user_dao.get_by_wallet_address(auth_request.wallet_address)
        
        if not user:
            try:
                user = await self.user_dao.create(
                    UserEntity(
                        wallet_address=auth_request.wallet_address,
                    )
                )
            except UserAlreadyExistsError:
                raise UserAlreadyExistsError("User with this wallet address already exists")

        access_token = create_access_token(
            user_id=user.id,
            wallet_address=user.wallet_address,
        )

        payload = decode_jwt(access_token)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            exp=payload["exp"]
        )

    async def send_email_verification_code(self, email_request: SendEmailCodeRequest) -> None:
        existing_user = await self.user_dao.get_by_email(email_request.email)
        if existing_user:
            raise UserAlreadyExistsError("Email is already taken by another user")
        code = generate_unique_digit_code(6)
        await self.email_client.send_verification_code(email_request.email, code)
        await self.redis_client.set_email_verification_code(email_request.email, code, ttl=300)

    async def verify_email_code(self, user_id: int, verification_request: VerifyEmailCodeRequest) -> None:
        stored_code = await self.redis_client.get_email_verification_code(verification_request.email)
        
        if not stored_code or stored_code != verification_request.code:
            raise InvalidVerificationCodeError("Invalid or expired verification code")
        await self.redis_client.delete_email_verification_code(verification_request.email)
        await UserService.get_instance().add_email(user_id, verification_request.email)

    @staticmethod
    async def generate_auth_message() -> str:
        return SIGN_MESSAGE
