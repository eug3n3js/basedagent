MODEL = "gpt-5-mini"
MULTICALL_DEPTH = 6

GENERATE_CHAT_TITLE_PROMPT = "Generate a title for the chat based on the messages in the chat. Return only the title up to 3 words and 20 characters and in English, no other text."
SYSTEM_PROMPT = "You are a helpful assistant specialized in NFTs and Crypto Tokens. You have access to MCP tools to get accurate information about NFT collections, individual NFTs, and search functionality."

PROMPT1 = "You need to score NFT collection based on the given criteria. Return the score in the range from 0 to 100."
PROMPT2 = "You need to scrape NFT collection based on the given criteria. Return the scraped data in forrmated text with all the details."
PROMPT3 = "You need to score project based on the given criteria. Return the score in the range from 0 to 100."
PROMPT4 = "You need to score X based on the given criteria. Return the score in the range from 0 to 100."
PROMPT5 = "General purpose prompt for any question that is related with crypto and NFTs. If not answer that you can talk only on crypto and NFTs topics."

PROMPT_LIST = [PROMPT1, PROMPT2, PROMPT3, PROMPT4, PROMPT5]

INIT_PROMPT = "Analyze the query and determine the best approach to answer the question. Here is list of all possible prompts: {PROMPT_LIST}. Chose one of the and return its indexs starting from 0."

PROMPT_MAP = {
    "nft_scoring": 0,
    "nft_scrapping": 1,
    "project_scoring": 2,
    "X scoring": 3,
}
