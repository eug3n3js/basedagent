import asyncio
import time
import logging
from clients import IndexerClient
from clients import RedisClient
from dto import IndexerConverter
from dto import GraphQLResponse, CreditsDeposited, CreditsDepositedETH, CreditsUsed
from services import NotificationService
from services import UserService

logger = logging.getLogger(__name__)


class IndexerService:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(IndexerService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, indexer_client: IndexerClient, notification_service: NotificationService, redis_client: RedisClient):
        if not hasattr(self, '_initialized'):
            self.indexer_client = indexer_client
            self.notification_service = notification_service
            self.redis_client = redis_client
            self._initialized = True
            self._running = False
            self.last_timestamp = time.time()
            self.recent_event_ttl = 10
    
    @classmethod
    def initialize(cls, indexer_client: IndexerClient, notification_service: NotificationService, redis_client: RedisClient):
        if cls._instance:
            raise RuntimeError("IndexerService is already initialized. Use get_instance() to access it.")
        instance = cls.__new__(cls)
        instance.__init__(indexer_client=indexer_client, notification_service=notification_service, redis_client=redis_client)
        cls._instance = instance
    
    @classmethod
    def get_instance(cls) -> 'IndexerService':
        if cls._instance is None:
            raise RuntimeError("IndexerService not initialized. Call initialize() first.")
        return cls._instance
    
    async def start_periodic_queries(self, interval_seconds: int = 30):
        if self._running:
            return
        
        self._running = True
        while self._running:
            self.last_timestamp = time.time() - interval_seconds * 2
            await self._process_indexer_data()
            await asyncio.sleep(interval_seconds)
            self.recent_event_ttl = interval_seconds * 3

    async def stop_periodic_queries(self):
        self._running = False
    
    async def _process_indexer_data(self):
        try:
            graphql_response = await self.indexer_client.get_credits_data(self.last_timestamp)
            await self._process_deposit_token_events(graphql_response.CreditSystem_CreditsDeposited or [])
            await self._process_deposit_eth_events(graphql_response.CreditSystem_CreditsDepositedETH or [])
            await self._process_spend_events(graphql_response.CreditSystem_CreditsUsed or [])
        except Exception as e:
            logger.error(f"Error processing fetching events {e}")


                
    async def _process_deposit_token_events(self, credit_deposits: list[CreditsDeposited]):
        try:         
            for deposit in credit_deposits:
                if await self.redis_client.check_recent_event_exists(deposit.user, float(deposit.timestamp), "deposit"):
                    continue
                deposit_event = IndexerConverter.from_deposited_to_deposit_event(deposit)
                await self.notification_service.store_deposit_event(deposit_event)
                await self.redis_client.set_recent_event(deposit.user, float(deposit.timestamp), "deposit", self.recent_event_ttl)
                
        except Exception as e:
            logger.error(f"Error processing deposit token events: {e}")

    async def _process_deposit_eth_events(self, credit_deposits: list[CreditsDepositedETH]):
        try:            
            for deposit in credit_deposits:
                if await self.redis_client.check_recent_event_exists(deposit.user, float(deposit.timestamp), "deposit_eth"):
                    continue
                
                deposit_event = IndexerConverter.from_deposited_eth_to_deposit_event(deposit)
                await self.notification_service.store_deposit_event(deposit_event)
                await self.redis_client.set_recent_event(deposit.user, float(deposit.timestamp), "deposit_eth", self.recent_event_ttl)
                
        except Exception as e:
            logger.error(f"Error processing deposit eth events: {e}")
    
    async def _process_spend_events(self, credit_used: list[CreditsUsed]):
        try:
            for credit_used in credit_used:
                if await self.redis_client.check_recent_event_exists(credit_used.user, float(credit_used.timestamp), "spend"):
                    continue
                spend_event = IndexerConverter.from_credits_used_to_spend_event(credit_used)
                await UserService.get_instance().update_balance_by_wallet(spend_event.user, spend_event.amount)
                await self.notification_service.store_spend_event(spend_event)
                await self.redis_client.set_recent_event(credit_used.user, float(credit_used.timestamp), "spend", self.recent_event_ttl)
                
        except Exception as e:
            logger.error(f"Error processing spend events: {e}")
    
