from ..models import (
    CreditsUsed,
    CreditsDeposited, CreditsDepositedETH
)
from ..models import DepositEvent, SpendEvent
from constants import TOKEN_CA_MAPPING


class IndexerConverter:
    
    @staticmethod
    def convert_token_ca_to_symbol(token_ca: str) -> str:
        return TOKEN_CA_MAPPING.get(token_ca, token_ca)

    @staticmethod
    def from_credits_used_to_spend_event(credits_used: CreditsUsed) -> SpendEvent:
        return SpendEvent(
            user=credits_used.user.lower(),
            amount=credits_used.amount,
            use_type=credits_used.useType,
            entity_id=credits_used.entityId,
            timestamp=credits_used.timestamp
        )
    
    @staticmethod
    def from_deposited_to_deposit_event(credits_deposited: CreditsDeposited) -> DepositEvent:
        token_symbol = IndexerConverter.convert_token_ca_to_symbol(credits_deposited.token)
        return DepositEvent(
            user=credits_deposited.user.lower(),
            token=token_symbol,
            token_amount=credits_deposited.tokenAmount,
            credits_minted=credits_deposited.creditsMinted,
            usd_rate=credits_deposited.usdRate,
            timestamp=credits_deposited.timestamp
        )
    
    @staticmethod
    def from_deposited_eth_to_deposit_event(credits_deposited_eth: CreditsDepositedETH) -> DepositEvent:
        return DepositEvent(
            user=credits_deposited_eth.user.lower(),
            token="ETH",
            token_amount=credits_deposited_eth.ethAmount,
            credits_minted=credits_deposited_eth.creditsMinted,
            usd_rate=credits_deposited_eth.ethUsdRate,
            timestamp=credits_deposited_eth.timestamp
        )
