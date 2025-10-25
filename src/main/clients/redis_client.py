import json
import os
from typing import Any
import redis.asyncio as redis
from exceptions.redis_exceptions import RedisConnectionError, RedisOperationError
from dto.models import MessageEntity
from dto.models.message_dto import MessageRole
from datetime import datetime
from dto.models.event_dto import DepositEvent, SpendEvent


class RedisClient:
    def __init__(self):
        self._redis: redis.Redis | None = None

    async def connect(self):
        try:
            self._redis = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                password=os.getenv("REDIS_PASSWORD"),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            await self._redis.ping()
        except Exception as e:
            raise RedisConnectionError(f"Failed to connect to Redis: {str(e)}")

    async def disconnect(self):
        if self._redis:
            await self._redis.close()

    async def set_email_verification_code(self, email: str, code: str, ttl: int = 300) -> bool:
        
        redis_key = f"email_verification:{email}"
        return await self._redis.set(redis_key, code, ex=ttl)

    async def get_email_verification_code(self, email: str) -> str | None:
        redis_key = f"email_verification:{email}"
        return await self._redis.get(redis_key)

    async def delete_email_verification_code(self, email: str) -> bool:
        redis_key = f"email_verification:{email}"
        return await self._redis.delete(redis_key)
    
    async def add_chat_message(self, chat_id: int, message_entity) -> bool:
        try:
            redis_key = f"chat_messages:{chat_id}"
            
            message_data = {
                "id": message_entity.id,
                "content": message_entity.content,
                "role": message_entity.role.value
                if hasattr(message_entity.role, 'value') else str(message_entity.role),
                "chat_id": message_entity.chat_id,
                "created_at": message_entity.created_at.isoformat() if message_entity.created_at else None
            }
            message_json = json.dumps(message_data)
            
            await self._redis.lpush(redis_key, message_json)
            
            await self._redis.ltrim(redis_key, 0, 19)
            
            await self._redis.expire(redis_key, 300)
            
            return True
        except Exception as e:
            raise RedisOperationError(f"Failed to add chat message: {str(e)}")
    
    async def get_chat_messages(self, chat_id: int) -> list[dict[str, Any]]:
        try:
            redis_key = f"chat_messages:{chat_id}"
            
            messages_json = await self._redis.lrange(redis_key, 0, -1)
            
            messages = []
            for message_json in messages_json:
                try:
                    message_data = json.loads(message_json)
                    messages.append(message_data)
                except json.JSONDecodeError:
                    continue
            
            return messages
        except Exception as e:
            raise RedisOperationError(f"Failed to get chat messages: {str(e)}")
    
    async def get_chat_message_entities(self, chat_id: int) -> list[MessageEntity]:
        try:

            redis_key = f"chat_messages:{chat_id}"
            
            messages_json = await self._redis.lrange(redis_key, 0, -1)
            
            message_entities = []
            for message_json in messages_json:
                try:
                    message_data = json.loads(message_json)
                    
                    message_entity = MessageEntity(
                        id=message_data.get("id"),
                        content=message_data.get("content", ""),
                        role=MessageRole(message_data.get("role", "user")),
                        chat_id=message_data.get("chat_id", chat_id),
                        created_at=datetime.fromisoformat(message_data.get("created_at")) if message_data.get("created_at") else None
                    )
                    message_entities.append(message_entity)
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    print(f"❌ Error parsing cached message: {e}")
                    continue
            
            return message_entities
        except Exception as e:
            raise RedisOperationError(f"Failed to get chat message entities: {str(e)}")
    
    async def clear_chat_messages(self, chat_id: int) -> bool:
        try:
            redis_key = f"chat_messages:{chat_id}"
            result = await self._redis.delete(redis_key)
            return result > 0
        except Exception as e:
            raise RedisOperationError(f"Failed to clear chat messages: {str(e)}")
    
    async def get_chat_messages_count(self, chat_id: int) -> int:
        try:
            redis_key = f"chat_messages:{chat_id}"
            return await self._redis.llen(redis_key)
        except Exception as e:
            raise RedisOperationError(f"Failed to get chat messages count: {str(e)}")
    
    async def extend_chat_messages_ttl(self, chat_id: int, ttl_seconds: int = 300) -> bool:
        try:
            redis_key = f"chat_messages:{chat_id}"
            result = await self._redis.expire(redis_key, ttl_seconds)
            return result
        except Exception as e:
            raise RedisOperationError(f"Failed to extend chat messages TTL: {str(e)}")
    
    async def store_user_event(self, user_wallet: str, event_data: dict) -> None:
        try:
            event_type = event_data.get("event_type", "unknown")
            type_events_key = f"user_events:{user_wallet}:{event_type}"
            is_first_event = not await self._redis.exists(type_events_key)
            await self._redis.lpush(type_events_key, json.dumps(event_data))
        
            type_limits = {
                "deposit": 50, 
                "spend": 50,   
                "unknown": 50  
            }
            
            limit = type_limits.get(event_type, 20)
            
            await self._redis.ltrim(type_events_key, 0, limit - 1)
            
            if is_first_event:
                await self._redis.expire(type_events_key, 1800) 
            
        except Exception as e:
            raise RedisOperationError(f"Failed to store user event: {str(e)}")
    
    async def _get_user_events_by_type(self, user_wallet: str, event_type: str) -> list[dict[str, Any]]:
        try:
            type_events_key = f"user_events:{user_wallet}:{event_type}"
            
            events_json = await self._redis.lrange(type_events_key, 0, -1)
            events = []
            for event_json in events_json:
                try:
                    event_data = json.loads(event_json)
                    events.append(event_data)
                except json.JSONDecodeError:
                    continue
            
            return events
        except Exception as e:
            raise RedisOperationError(f"Failed to get user events by type: {str(e)}")

    async def get_user_deposit_events(self, user_wallet: str) -> list[DepositEvent]:
        try:
            events = await self._get_user_events_by_type(user_wallet, "deposit")
            return [DepositEvent(**event["data"]) for event in events]
        except Exception as e:
            raise RedisOperationError(f"Failed to get user deposit events: {str(e)}")
    
    async def get_user_spend_events(self, user_wallet: str) -> list[SpendEvent]:
        try:
            events = await self._get_user_events_by_type(user_wallet, "spend")
            return [SpendEvent(**event["data"]) for event in events]
        except Exception as e:
            raise RedisOperationError(f"Failed to get user spend events: {str(e)}")
    
    async def clear_user_events(self, user_wallet: str) -> None:
        try:
            event_types = ["deposit", "spend", "unknown"]
            for event_type in event_types:
                type_events_key = f"user_events:{user_wallet}:{event_type}"
                await self._redis.delete(type_events_key)
        except Exception as e:
            raise RedisOperationError(f"Failed to clear user events: {str(e)}")

