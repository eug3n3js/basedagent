from dto.models.event_dto import DepositEvent, SpendEvent
from clients.redis_client import RedisClient
from exceptions.redis_exceptions import RedisOperationError


class NotificationService:  
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(NotificationService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, redis_client: RedisClient):
        if not hasattr(self, '_initialized'):
            self.redis_client = redis_client
            self._initialized = True
    
    @classmethod
    def initialize(cls, redis_client: RedisClient):
        if cls._instance:
            raise RuntimeError("NotificationService is already initialized. Use get_instance() to access it.")
        instance = cls.__new__(cls)
        instance.__init__(redis_client=redis_client)
        cls._instance = instance
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("NotificationService not initialized. Call initialize() first.")
        return cls._instance
    
    async def store_deposit_event(self, deposit_event: DepositEvent) -> None:
        try:
            event_data = {
                "event_type": "deposit",
                "data": deposit_event.dict(),
                "timestamp": deposit_event.timestamp
            }
            print(event_data)
            await self.redis_client.store_user_event(deposit_event.user, event_data)
            events_data = await self.redis_client.get_user_deposit_events(deposit_event.user)
            print("get events_data")
            print(events_data)
        except Exception as e:
            raise RedisOperationError(f"Failed to store deposit event: {str(e)}")
    
    async def store_spend_event(self, spend_event: SpendEvent) -> None:
        try:
            event_data = {
                "event_type": "spend",
                "data": spend_event.dict(),
                "timestamp": spend_event.timestamp
            }
            
            await self.redis_client.store_user_event(spend_event.user, event_data)
        except Exception as e:
            raise RedisOperationError(f"Failed to store spend event: {str(e)}")
    
    async def get_user_deposit_events(self, user_wallet: str) -> list[DepositEvent]:
        try:
            return await self.redis_client.get_user_deposit_events(user_wallet)
        except Exception as e:
            raise RedisOperationError(f"Failed to get user deposit events: {str(e)}")
    
    async def get_user_spend_events(self, user_wallet: str) -> list[SpendEvent]:
        try:
            return await self.redis_client.get_user_spend_events(user_wallet)
        except Exception as e:
            raise RedisOperationError(f"Failed to get user spend events: {str(e)}")
    
    async def clear_user_events(self, user_wallet: str) -> None:
        try:
            await self.redis_client.clear_user_events(user_wallet)
        except Exception as e:
            raise RedisOperationError(f"Failed to clear user events: {str(e)}")
    
