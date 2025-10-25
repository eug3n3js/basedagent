from pydantic import BaseModel


class DepositEvent(BaseModel):
    user: str
    token: str
    token_amount: float
    credits_minted: float
    usd_rate: float
    timestamp: float
    event_type: str = "deposit"


class SpendEvent(BaseModel):
    user: str
    amount: float
    use_type: int
    entity_id: int
    timestamp: float
    event_type: str = "spend"
