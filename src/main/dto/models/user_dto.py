from dataclasses import dataclass
from datetime import datetime
from typing import List
from pydantic import BaseModel


@dataclass
class UserEntity:
    id: int = None
    wallet_address: str = None
    email: str = None
    remaining_chat_credits: float = 0
    created_at: datetime = None


@dataclass
class CryptoBalance:
    symbol: str
    usd_total: float


@dataclass
class NFTItem:
    collection_name: str
    collection_slug: str
    image_url: str
    chain_name: str


@dataclass
class UserProfile:
    cryptocurrencies: List[CryptoBalance]
    nfts: List[NFTItem]
