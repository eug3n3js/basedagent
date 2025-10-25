import json
import os
import openai
from openai.types.chat import ChatCompletion

from .redis_client import RedisClient
from .mcp_client import MCPClient
from constants import MODEL, MULTICALL_DEPTH, SYSTEM_PROMPT, INIT_PROMPT, PROMPT_LIST, \
    GENERATE_CHAT_TITLE_PROMPT
from exceptions import LLMClientError


class LLMClient:
    def __init__(self, 
                 mcp_client: MCPClient,
                 chat_id: int,
                 redis_client: RedisClient):
        self.openai_client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.chat_id = chat_id
        self.mcp_client = mcp_client
        self.redis_client = redis_client

    async def get_ai_response(self, 
                              user_message: str, 
                              prompt_index: int = None) -> str:
        if prompt_index is None:
            prompt_index = await self.classification_prompt(user_message)
        
        chat_history = await self._get_chat_history()
        
        messages = [{
            "role": "system",
            "content": SYSTEM_PROMPT
        }]

        messages.extend(chat_history)

        messages.append({
            "role": "user",
            "content": user_message
        })
        messages.append({
            "role": "system",
            "content": PROMPT_LIST[prompt_index]
        })

        for i in range(MULTICALL_DEPTH):
            if i == MULTICALL_DEPTH - 1:
                tools = None
            else:
                tools = self.mcp_client.get_all_tools()
            response = await self._make_ai_request(messages, tools)
            print(f"AI Response {i}: {response.choices[0].message}")
            message = response.choices[0].message
            if message.tool_calls:
                tool_results = []
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    tool_result = await self.mcp_client.execute_tool(tool_name, tool_args)
                    tool_results.append(f"Tool: {tool_name} Result: {tool_result}")
        
                messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [{
                        "id": tc.id, 
                        "type": tc.type, 
                        "function": {
                            "name": tc.function.name, 
                            "arguments": tc.function.arguments
                        }
                    } for tc in message.tool_calls]
                })
                for i, tool_call in enumerate(message.tool_calls):
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_results[i]
                        if i < len(tool_results) else f"Tool {tool_call.function.name} result: None"
                    })
            else:
                return message.content or "No response generated"
    
    async def _get_chat_history(self) -> list[dict[str, str]]:
        try:
            cached_message_entities = await self.redis_client.get_chat_message_entities(self.chat_id)
            chat_history = []
            for message_entity in cached_message_entities:
                chat_history.append({
                    "role": message_entity.role.value
                    if hasattr(message_entity.role, 'value') else str(message_entity.role),
                    "content": message_entity.content
                })
            
            return chat_history
        except Exception as e:
            print(f"❌ Error getting chat history from Redis: {e}")
            return []

    async def classification_prompt(self, user_message: str) -> int:
        messages = list()
        messages.extend(await self._get_chat_history())
        messages.append({
            "role": "system",
            "content": INIT_PROMPT.format(PROMPT_LIST=PROMPT_LIST)
        })
        messages.append({
            "role": "user",
            "content": user_message
        })

        response = await self._make_ai_request(messages)
        try:
            return int(response.choices[0].message.content)
        except Exception as e:
            return -1

    async def _make_ai_request(self, messages: list[dict], tools: list[dict] = None) -> ChatCompletion:
        request_params = {
            "model": MODEL,
            "messages": messages,
            "temperature": 1
        }
        if tools:
            request_params["tools"] = tools
            request_params["tool_choice"] = "auto"
        try:
            return await self.openai_client.chat.completions.create(**request_params)
        except Exception as e:
            raise LLMClientError(f"Failed to make AI request: {str(e)}") from e

    async def generate_chat_title(self, message: str) -> str:
        messages = list()
        messages.append({
            "role": "system",
            "content": GENERATE_CHAT_TITLE_PROMPT
        })
        messages.append({
            "role": "user",
            "content": message
        })
        response = await self._make_ai_request(messages)
        return response.choices[0].message.content
