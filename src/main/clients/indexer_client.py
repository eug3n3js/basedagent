import os

import aiohttp

from dto import GraphQLResponse
from exceptions import IndexerConnectionError, IndexerQueryError


class IndexerClient:
    
    def __init__(self):
        self.endpoint = os.getenv("GRAPHQL_ENDPOINT")
        self.session: aiohttp.ClientSession | None = None
    
    async def _make_graphql_request(self, query: str, variables: dict) -> dict:
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.post(
                self.endpoint,
                json={"query": query, "variables": variables},
                timeout=aiohttp.ClientTimeout(total=2)
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            raise IndexerConnectionError(f"Failed to connect to GraphQL endpoint: {str(e)}")
        except Exception as e:
            raise IndexerQueryError(f"GraphQL query failed: {str(e)}")
    
    async def get_credits_data(self, from_timestamp: float) -> GraphQLResponse:
        query = """
        query ($from: numeric!) {
          CreditSystem_CreditsUsed(where: { timestamp: { _gte: $from } }, order_by: { timestamp: desc }) {
            user
            amount
            useType
            entityId
            timestamp
          }

          CreditSystem_CreditsDeposited(where: { timestamp: { _gte: $from } }, order_by: { timestamp: desc }) {
            user
            token
            tokenAmount
            creditsMinted
            usdRate
            timestamp
          }

          CreditSystem_CreditsDepositedETH(where: { timestamp: { _gte: $from } }, order_by: { timestamp: desc }) {
            user
            ethAmount
            creditsMinted
            ethUsdRate
            timestamp
          }
        }
        """
        
        variables = {"from": from_timestamp}
        
        try:
            response_data = await self._make_graphql_request(query, variables)
            data = response_data.get("data", {})
            print(data)
            return GraphQLResponse(**data)
        except Exception as e:
            raise IndexerQueryError(f"Failed to parse GraphQL response: {str(e)}")
    
    async def close(self):
        if self.session:
            await self.session.close()
