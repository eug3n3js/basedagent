import asyncio
import time
import logging
from clients.indexer_client import IndexerClient
from dto.converters.indexer_converter import IndexerConverter
from dto.models.indexer_dto import GraphQLResponse, CreditsDeposited, CreditsDepositedETH, CreditsUsed
from services.notification_service import NotificationService
from services.user_service import UserService

logger = logging.getLogger(__name__)


class IndexerService:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(IndexerService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, indexer_client: IndexerClient, notification_service: NotificationService):
        if not hasattr(self, '_initialized'):
            self.indexer_client = indexer_client
            self.notification_service = notification_service
            self._initialized = True
            self._running = False
            self.last_timestamp = time.time()
    
    @classmethod
    def initialize(cls, indexer_client: IndexerClient, notification_service: NotificationService):
        if cls._instance:
            raise RuntimeError("IndexerService is already initialized. Use get_instance() to access it.")
        instance = cls.__new__(cls)
        instance.__init__(indexer_client=indexer_client, notification_service=notification_service)
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
            self.last_timestamp = time.time() - interval_seconds - 2
            await self._process_indexer_data()
            await asyncio.sleep(interval_seconds)

    async def stop_periodic_queries(self):
        self._running = False
    
    async def _process_indexer_data(self):
        try:
            graphql_response = await self.indexer_client.get_credits_data(self.last_timestamp)
            print("graphql_response")
            print(graphql_response)
            await self._process_deposit_token_events(graphql_response.CreditSystem_CreditsDeposited or [])
            await self._process_deposit_eth_events(graphql_response.CreditSystem_CreditsDepositedETH or [])
            await self._process_spend_events(graphql_response.CreditSystem_CreditsUsed or [])
        except Exception as e:
            logger.error(f"Error processing fetching events {e}")


                
    async def _process_deposit_token_events(self, credit_deposits: list[CreditsDeposited]):
        try:         

            for deposit in credit_deposits:
                deposit_event = IndexerConverter.from_deposited_to_deposit_event(deposit)
                await self.notification_service.store_deposit_event(deposit_event)
                
        except Exception as e:
            logger.error(f"Error processing deposit token events: {e}")

    async def _process_deposit_eth_events(self, credit_deposits: list[CreditsDepositedETH]):
        try:            
            for deposit in credit_deposits:
                deposit_event = IndexerConverter.from_deposited_eth_to_deposit_event(deposit)
                await UserService.get_instance().update_balance_by_wallet(deposit.user, deposit.creditsMinted)
                await self.notification_service.store_deposit_event(deposit_event)                
        except Exception as e:
            logger.error(f"Error processing deposit eth events: {e}")
    
    async def _process_spend_events(self, credit_used: list[CreditsUsed]):
        try:
            for credit_used in credit_used:
                spend_event = IndexerConverter.from_credits_used_to_spend_event(credit_used)
                await UserService.get_instance().update_balance_by_wallet(spend_event.user, spend_event.amount)
                await self.notification_service.store_spend_event(spend_event)
        except Exception as e:
            logger.error(f"Error processing spend events: {e}")
    
