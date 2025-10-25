from typing import Any

from .mcp_providers import MCPProvider, OpenSeaMCPProvider, TweetScoutMCPProvider


class MCPClient:
    def __init__(self):
        self.providers: list[MCPProvider] = []
        self.all_tools = []
        self.total_cost_usd = 0.0
        self.setup_default_providers()
    
    async def initialize_all_providers(self) -> None:
        self.all_tools = []
        
        for provider in self.providers:
            try:
                tools = await provider.get_tools()
                self.all_tools.extend(tools)
                print(f"✅ {provider.get_provider_name()} provider initialized with {len(tools)} tools")
            except Exception as e:
                print(f"❌ Failed to initialize {provider.get_provider_name()}: {e}")
    
    async def execute_tool(self, tool_name: str, tool_args: dict) -> Any:
        for provider in self.providers:
            provider_name = provider.get_provider_name()
            if tool_name.startswith(f"{provider_name}_"):
                try:
                    tool_cost = provider.get_tool_cost(tool_name)
                    result = await provider.execute_tool(tool_name, tool_args)
                    self.total_cost_usd += tool_cost
                    print(f"💰 Tool {tool_name} cost: ${tool_cost:.4f} (Total: ${self.total_cost_usd:.4f})")
                    
                    return result
                except Exception as e:
                    return f"Error executing {tool_name}: {e}"
        
        return f"No provider found for tool: {tool_name}"
    
    def get_all_tools(self) -> list[dict]:
        return self.all_tools.copy()
    
    def get_total_cost(self) -> float:
        return self.total_cost_usd
    
    async def setup_default_providers(self):
        self.providers.append(OpenSeaMCPProvider())
        self.providers.append(TweetScoutMCPProvider())
        await self.initialize_all_providers()
