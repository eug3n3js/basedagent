import json
import ast
from typing import Any, Dict, List, Optional, Union

from dto import CryptoBalance, NFTItem, UserProfile


def _safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(value)
        return None
    except Exception:
        return None


def _parse_balances(root: Dict[str, Any]) -> List[CryptoBalance]:
    balances: Dict[str, float] = {}
    for entry in root.get("balances", []) or []:
        try:
            currency = entry.get("currency") or {}
            symbol = currency.get("symbol")
            usd_value = _safe_float(entry.get("usdValue"))
            if not symbol or usd_value is None:
                continue
            balances[symbol] = balances.get(symbol, 0.0) + usd_value
        except Exception:
            continue

    result = [CryptoBalance(symbol=sym, usd_total=total) for sym, total in balances.items()]
    result.sort(key=lambda x: x.usd_total, reverse=True)
    return result


def _parse_nfts(root: Dict[str, Any]) -> List[NFTItem]:
    items_root = root.get("items") or {}
    items = items_root.get("items") or []
    nfts: List[NFTItem] = []
    for it in items:
        try:
            collection = it.get("collection") or {}
            chain = it.get("chain") or {}
            collection_name = collection.get("name")
            collection_slug = collection.get("slug")
            image_url = it.get("imageUrl")
            chain_name = chain.get("name")
            if not (collection_name and collection_slug and image_url and chain_name):
                continue
            nfts.append(
                NFTItem(
                    collection_name=collection_name,
                    collection_slug=collection_slug,
                    image_url=image_url,
                    chain_name=chain_name,
                )
            )
        except Exception:
            continue
    return nfts


def _parse_user_data(data: Dict[str, Any]) -> UserProfile:

    if "errors" in data:
        raise MCPResponseError("Invalid address")

    cryptocurrencies = _parse_balances(data)
    nfts = _parse_nfts(data)
    return UserProfile(cryptocurrencies=cryptocurrencies, nfts=nfts)


def json_to_user_profile(json_data: dict) -> UserProfile:
    if isinstance(json_data, dict):
        return _parse_user_data(json_data)
