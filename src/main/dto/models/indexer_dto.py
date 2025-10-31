from pydantic import BaseModel, Field
from typing import List, Optional


class CreditsUsed(BaseModel):
    user: str
    amount: float
    useType: int
    entityId: int
    timestamp: float


class CreditsDeposited(BaseModel):
    user: str
    token: str
    tokenAmount: float
    creditsMinted: float
    usdRate: float
    timestamp: float


class CreditsDepositedETH(BaseModel):
    user: str
    ethAmount: float
    creditsMinted: float
    ethUsdRate: float
    timestamp: float


class GraphQLResponse(BaseModel):
    CreditSystem_CreditsUsed: Optional[List[CreditsUsed]] = None
    CreditSystem_CreditsDeposited: Optional[List[CreditsDeposited]] = None
    CreditSystem_CreditsDepositedETH: Optional[List[CreditsDepositedETH]] = None 

