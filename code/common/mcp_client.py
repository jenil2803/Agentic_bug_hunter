"""
MCP Client for interacting with the bug documentation server
"""
import httpx
from typing import List, Dict, Optional
from common.config import MCP_SERVER_URL, REQUEST_TIMEOUT
from common.logger import get_logger
from common.rate_limiter import rate_limited

logger = get_logger("mcp_client")


class MCPClient:
    """Client for interacting with the MCP server"""
    
    def __init__(self, server_url: str = MCP_SERVER_URL):
        self.server_url = server_url
        self.client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)
    
    @rate_limited
    async def search_documents(self, query: str) -> List[Dict]:
        """
        Search for relevant documentation using vector similarity
        
        Args:
            query: Search query string
            
        Returns:
            List of documents with text and score
        """
        try:
            logger.debug(f"Searching documents for query: {query[:100]}...")
            
            response = await self.client.post(
                f"{self.server_url}/search_documents",
                json={"query": query}
            )
            response.raise_for_status()
            
            results = response.json()
            logger.info(f"Found {len(results)} relevant documents")
            return results
        
        except httpx.ConnectError as e:
            logger.warning(f"MCP server not available at {self.server_url}. Continuing without documentation context.")
            return []
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    async def get_context_for_code(self, code_snippet: str, context: str = "") -> str:
        """
        Get relevant documentation context for a code snippet
        
        Args:
            code_snippet: The code to analyze
            context: Additional context about the code
            
        Returns:
            Concatenated relevant documentation text
        """
        # Create search query from code and context
        search_query = f"{context}\n\n{code_snippet}" if context else code_snippet
        
        # Search for relevant docs
        docs = await self.search_documents(search_query)
        
        if not docs:
            logger.debug("No documentation context available (MCP server may not be running)")
            return ""
        
        # Take top 3 most relevant documents
        top_docs = sorted(docs, key=lambda x: x.get('score', 0), reverse=True)[:3]
        
        # Concatenate documentation
        context_text = "\n\n".join([doc.get('text', '') for doc in top_docs])
        
        return context_text
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
