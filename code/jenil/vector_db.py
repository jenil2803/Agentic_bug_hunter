"""
Jenil's Work - Vector Database Manager

Manages ChromaDB for storing and retrieving bug detection history.
"""

import chromadb
from chromadb.config import Settings
from datetime import datetime
from typing import List, Dict, Optional
from common.config import VECTOR_DB_PATH
from common.logger import get_logger

logger = get_logger("vector_db")


class BugDatabase:
    """Vector database for bug detection history"""
    
    def __init__(self, persist_directory: str = str(VECTOR_DB_PATH)):
        """Initialize the vector database"""
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="bug_detections",
            metadata={"description": "Bug detection results and history"}
        )
        
        logger.info(f"Vector database initialized at {persist_directory}")
    
    def add_bug_result(
        self,
        code_id: str,
        code_snippet: str,
        bug_line: int,
        explanation: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add a bug detection result to the database
        
        Args:
            code_id: Unique identifier for the code
            code_snippet: The code that was analyzed
            bug_line: Line number where bug was found
            explanation: Bug explanation
            metadata: Additional metadata
        """
        try:
            doc_metadata = {
                "code_id": code_id,
                "bug_line": bug_line,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # Store in ChromaDB
            self.collection.add(
                ids=[f"bug_{code_id}_{datetime.now().timestamp()}"],
                documents=[explanation],
                metadatas=[doc_metadata]
            )
            
            logger.info(f"Added bug result for {code_id} to database")
        
        except Exception as e:
            logger.error(f"Error adding bug result to database: {e}")
    
    def get_cached_result(self, code_id: str) -> Optional[Dict]:
        """
        Get cached result for a code snippet to avoid re-processing
        
        Args:
            code_id: Unique identifier for the code
            
        Returns:
            Cached result if found, None otherwise
        """
        try:
            results = self.collection.get(
                ids=[code_id],
                include=['metadatas', 'documents']
            )
            
            if results['ids'] and len(results['ids']) > 0:
                metadata = results['metadatas'][0]
                explanation = results['documents'][0]
                
                logger.info(f"Found cached result for ID {code_id}")
                return {
                    'ID': code_id,
                    'Bug Line': metadata.get('bug_line', 0),
                    'Explanation': explanation
                }
            
            return None
        
        except Exception as e:
            logger.debug(f"No cached result for {code_id}: {e}")
            return None
    
    def search_similar_bugs(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Search for similar bugs in history
        
        Args:
            query: Search query (code or explanation)
            n_results: Number of results to return
            
        Returns:
            List of similar bug records
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['ids']:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'explanation': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            logger.info(f"Found {len(formatted_results)} similar bugs")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error searching database: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        try:
            count = self.collection.count()
            return {
                'total_bugs': count,
                'collection_name': self.collection.name
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def clear_database(self):
        """Clear all records from the database"""
        try:
            self.client.delete_collection("bug_detections")
            self.collection = self.client.get_or_create_collection(
                name="bug_detections",
                metadata={"description": "Bug detection results and history"}
            )
            logger.info("Database cleared")
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
