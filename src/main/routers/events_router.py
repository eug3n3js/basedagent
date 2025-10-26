import time
from fastapi import APIRouter, Depends
from dto import DepositEvent, SpendEvent
from utils.auth_utils import get_access_data
from dto import AccessData
from services import NotificationService

events_router = APIRouter(prefix="/events")


@events_router.get("/all")
async def get_all_user_events(
    current_user: AccessData = Depends(get_access_data),
    notification_service: NotificationService = Depends(NotificationService.get_instance)
) -> list[DepositEvent | SpendEvent]:
    all_events: list[DepositEvent | SpendEvent] = list()
    deposit_events = await notification_service.get_user_deposit_events(current_user.wallet_address)
    spend_events = await notification_service.get_user_spend_events(current_user.wallet_address)
    all_events.extend(deposit_events)
    all_events.extend(spend_events)
    all_events.sort(key=lambda x: x.timestamp)
    await notification_service.clear_user_events(current_user.wallet_address)
    return all_events
