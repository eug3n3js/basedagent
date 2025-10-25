from fastapi import APIRouter, Depends
from dto.models.event_dto import DepositEvent, SpendEvent
from utils.auth_utils import get_access_data
from dto.models.auth_dto import AccessData
from services.notification_service import NotificationService

events_router = APIRouter(prefix="/events")


@events_router.get("/all")
async def get_all_user_events(
    current_user: AccessData = Depends(get_access_data),
    notification_service: NotificationService = Depends(NotificationService.get_instance)
) -> list[DepositEvent | SpendEvent]:
    all_events: list[DepositEvent | SpendEvent] = list()
    print(f"wallet_address: {current_user.wallet_address}")
    deposit_events = await notification_service.get_user_deposit_events(current_user.wallet_address)
    print(f"deposit_events: {deposit_events}")
    spend_events = await notification_service.get_user_spend_events(current_user.wallet_address)
    print(f"spend_events: {spend_events}")
    all_events.extend(deposit_events)
    all_events.extend(spend_events)
    all_events.sort(key=lambda x: x.timestamp)
    await notification_service.clear_user_events(current_user.wallet_address)
    return all_events
