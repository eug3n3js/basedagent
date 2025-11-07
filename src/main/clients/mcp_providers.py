import os
import aiohttp
from typing import Any
from abc import ABC, abstractmethod

from mcp import ClientSession
from mcp.client.sse import sse_client


class MCPProvider(ABC):

    @abstractmethod
    async def get_tools(self) -> list[dict]:
        pass
    
    @abstractmethod
    async def execute_tool(self, tool_name: str, tool_args: dict) -> Any:
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        pass
    
    @abstractmethod
    def get_tool_cost(self, tool_name: str) -> float:
        pass


class OpenSeaMCPProvider(MCPProvider):

    def __init__(self):
        self.server_url = os.getenv("OPENSEA_MCP_URL", "https://mcp.opensea.io/sse")
        self.bearer_token = os.getenv("OPENSEA_BEARER_TOKEN")
        self.tools = []
        self.tool_costs = {
            # "opensea_search_collections": 0.2,
            # "opensea_get_collection": 0.005,
            # "opensea_get_asset": 0.005,
            # "opensea_get_events": 0.01,
        }
    
    async def get_tools(self) -> list[dict]:
        try:
            print(f"🔧 Getting tools from OpenSea MCP...")
            async with sse_client(
                url=self.server_url, 
                headers={'Authorization': f'Bearer {self.bearer_token}'}
            ) as (in_s, out_s):
                async with ClientSession(in_s, out_s) as sess:
                    info = await sess.initialize()
                    print("OpenSea MCP info:", info)
                    mcp_tools = await sess.list_tools()
                    tools_list = mcp_tools.tools if hasattr(mcp_tools, 'tools') else mcp_tools
                    
                    self.tools = [{
                        "type": "function",
                        "function": {
                            "name": f"opensea_{tool.name}",
                            "description": tool.description,
                            "parameters": tool.inputSchema
                        }
                    } for tool in tools_list]
                    print(f"✅ Retrieved {len(self.tools)} tools from OpenSea MCP")
                    return self.tools
        except Exception as e:
            print(f"❌ Error getting OpenSea tools: {e}")
            return []
    
    async def execute_tool(self, tool_name: str, tool_args: dict) -> Any:
        actual_tool_name = tool_name.replace("opensea_", "")
        try:
            async with sse_client(
                url=self.server_url, 
                headers={'Authorization': f'Bearer {self.bearer_token}'}
            ) as (in_s, out_s):
                async with ClientSession(in_s, out_s) as sess:
                    await sess.initialize()
                    result = await sess.call_tool(actual_tool_name, tool_args)
                    return result.content
        except Exception as e:
            return f"❌ OpenSea Error: {e}"
    
    def get_provider_name(self) -> str:
        return "opensea"

    def get_tool_cost(self, tool_name: str) -> float:
        return self.tool_costs.get(tool_name, 0.0)


class TweetScoutMCPProvider(MCPProvider):
    def __init__(self):
        self.api_key = os.getenv("TWEETSCOUT_API_KEY")
        self.base_url = "https://api.tweetscout.io/v2"
        self.tools = []
        self.tool_costs = {
            "tweetscout_get_score": 0.1,
            "tweetscout_get_info": 0.1,
            "tweetscout_get_followers_stats": 0.1,
            "tweetscout_get_top_followers": 0.1,
        }
    
    async def get_tools(self) -> list[dict]:
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "tweetscout_get_score",
                    "description": (
                        "Retrieve the TweetScout popularity score for a given Twitter user handle. "
                        "The score estimates how popular the account is among Influencers, Projects, and VCs. "
                        "Higher scores indicate greater influence. "
                        "If returns User not found 404 means that user was not found."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_handle": {
                                "type": "string",
                                "description": "The Twitter handle (without @) of the account to retrieve the score for."
                            }
                        },
                        "required": ["user_handle"],
                        "additionalProperties": False,
                        "$schema": "http://json-schema.org/draft-07/schema#"
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "tweetscout_get_info",
                    "description": (
                        "Get basic Twitter account information by user handle. "
                        "Retrieve basic information for a specific Twitter account including avatar, banner, "
                        "description, followers count, follows count, account ID, name, registration date, "
                        "screen name, status count, and verification status."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_handle": {
                                "type": "string",
                                "description": "The Twitter handle (without @) of the account to retrieve information for."
                            }
                        },
                        "required": ["user_handle"],
                        "additionalProperties": False,
                        "$schema": "http://json-schema.org/draft-07/schema#"
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "tweetscout_get_followers_stats",
                    "description": (
                        "Get number of followers for each category on TweetScout. "
                        "Get statistics on the number of followers by TweetScout categories: influencers, "
                        "projects and VC employees. This endpoint receives data in real time, so it may take "
                        "some time to respond especially for accounts with a large number of followers. "
                        "If we have information about the account in our database, the response will be quick. "
                        "Otherwise, the request may take longer to process, as we need to gather account information."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_handle": {
                                "type": "string",
                                "description": "The Twitter handle (without @). Either user_handle or user_id is required."
                            },
                            "user_id": {
                                "type": "string",
                                "description": "The Twitter user ID. Either user_handle or user_id is required."
                            }
                        },
                        "required": [],
                        "additionalProperties": False,
                        "$schema": "http://json-schema.org/draft-07/schema#"
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "tweetscout_get_top_followers",
                    "description": (
                        "Get top 20 account followers by TweetScout score. "
                        "This endpoint returns basic account information and score for the top 20 followers "
                        "with the highest score. If speed is more important to you, use the 'from' parameter "
                        "set to 'db' to get data from database only."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_handle": {
                                "type": "string",
                                "description": "The Twitter handle (without @) of the account to get top followers for."
                            },
                            "from": {
                                "type": "string",
                                "description": "Optional. Set to 'db' to get data from database only for faster response.",
                                "enum": ["db"]
                            }
                        },
                        "required": ["user_handle"],
                        "additionalProperties": False,
                        "$schema": "http://json-schema.org/draft-07/schema#"
                    }
                }
            }
        ]
        print(f"✅ Retrieved {len(self.tools)} TweetScout tools")
        return self.tools
    
    async def execute_tool(self, tool_name: str, tool_args: dict) -> Any:
        if tool_name == "tweetscout_get_score":
            return await self._get_tweetscout_score(tool_args)
        elif tool_name == "tweetscout_get_info":
            return await self._get_tweetscout_info(tool_args)
        elif tool_name == "tweetscout_get_followers_stats":
            return await self._get_tweetscout_followers_stats(tool_args)
        elif tool_name == "tweetscout_get_top_followers":
            return await self._get_tweetscout_top_followers(tool_args)
        return f"❌ Unknown TweetScout tool: {tool_name}"
    
    async def _get_tweetscout_score(self, inputs: dict) -> Any:
        user_handle = inputs["user_handle"]
        url = f"{self.base_url}/score/{user_handle}"
        
        headers = {
            "ApiKey": self.api_key, 
            'Accept': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"status": "ok", "data": data}
                    else:
                        error = await response.text()
                        return {"status": "error", "code": response.status, "message": error}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _get_tweetscout_info(self, inputs: dict) -> Any:
        user_handle = inputs["user_handle"]
        url = f"{self.base_url}/info/{user_handle}"
        
        headers = {
            "ApiKey": self.api_key,
            'Accept': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"status": "ok", "data": data}
                    else:
                        error = await response.text()
                        return {"status": "error", "code": response.status, "message": error}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _get_tweetscout_followers_stats(self, inputs: dict) -> Any:
        url = f"{self.base_url}/followers-stats"
        
        params = {}
        if "user_handle" in inputs:
            params["user_handle"] = inputs["user_handle"]
        if "user_id" in inputs:
            params["user_id"] = inputs["user_id"]
        
        if not params:
            return {"status": "error", "message": "Either user_handle or user_id is required"}
        
        headers = {
            "ApiKey": self.api_key,
            'Accept': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"status": "ok", "data": data}
                    else:
                        error = await response.text()
                        return {"status": "error", "code": response.status, "message": error}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _get_tweetscout_top_followers(self, inputs: dict) -> Any:
        user_handle = inputs["user_handle"]
        url = f"{self.base_url}/top-followers/{user_handle}"
        
        params = {}
        if "from" in inputs:
            params["from"] = inputs["from"]
        
        headers = {
            "ApiKey": self.api_key,
            'Accept': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"status": "ok", "data": data}
                    else:
                        error = await response.text()
                        return {"status": "error", "code": response.status, "message": error}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_provider_name(self) -> str:
        return "tweetscout"
    
    def get_tool_cost(self, tool_name: str) -> float:
        return self.tool_costs.get(tool_name, 0.0)