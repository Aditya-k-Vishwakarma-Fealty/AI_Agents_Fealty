"""
Vector search tool for LangChain agents.
Provides ChromaDB operations as tools for semantic search.
"""
from langchain.tools import Tool
from typing import List, Dict, Any
import json
import logging

from app.vectorstore.chroma_client import chroma_client

logger = logging.getLogger(__name__)


class VectorSearchTool:
    """Vector search operations wrapper for LangChain agents."""
    
    def add_resume_embedding(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add resume embedding to ChromaDB.
        
        Args:
            data: Dict with candidate_id, text, metadata
        
        Returns:
            Dict with status and document_id
        """
        try:
            doc_id = chroma_client.add_resume_embedding(
                candidate_id=data["candidate_id"],
                text=data["text"],
                metadata=data.get("metadata")
            )
            
            logger.info(f"Added resume embedding: {doc_id}")
            return {"status": "success", "document_id": doc_id}
        except Exception as e:
            logger.error(f"Error adding resume embedding: {e}")
            return {"status": "error", "message": str(e)}
    
    def add_role_embedding(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add role/JD embedding to ChromaDB.
        
        Args:
            data: Dict with role_id, jd_text, metadata
        
        Returns:
            Dict with status and document_id
        """
        try:
            doc_id = chroma_client.add_role_embedding(
                role_id=data["role_id"],
                jd_text=data["jd_text"],
                metadata=data.get("metadata")
            )
            
            logger.info(f"Added role embedding: {doc_id}")
            return {"status": "success", "document_id": doc_id}
        except Exception as e:
            logger.error(f"Error adding role embedding: {e}")
            return {"status": "error", "message": str(e)}
    
    def search_similar_resumes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find resumes similar to a role.
        
        Args:
            data: Dict with role_id, top_k (optional)
        
        Returns:
            Dict with matching resumes
        """
        try:
            matches = chroma_client.search_similar_resumes(
                role_id=data["role_id"],
                top_k=data.get("top_k", 10)
            )
            
            logger.info(f"Found {len(matches)} similar resumes")
            return {"status": "success", "matches": matches}
        except Exception as e:
            logger.error(f"Error searching similar resumes: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_similarity_score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate similarity score between resume and role.
        
        Args:
            data: Dict with candidate_id, role_id
        
        Returns:
            Dict with similarity score
        """
        try:
            score = chroma_client.get_similarity_score(
                candidate_id=data["candidate_id"],
                role_id=data["role_id"]
            )
            
            logger.info(f"Calculated similarity score: {score}")
            return {"status": "success", "similarity_score": score}
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return {"status": "error", "message": str(e)}


def create_vector_tools() -> List[Tool]:
    """
    Create LangChain tools for vector search operations.
    
    Returns:
        List of LangChain Tool objects
    """
    vector_tool = VectorSearchTool()
    
    tools = [
        Tool(
            name="add_resume_embedding",
            func=lambda data: vector_tool.add_resume_embedding(json.loads(data) if isinstance(data, str) else data),
            description="Add resume embedding to vector database. Input should be JSON with: candidate_id, text, metadata (optional)"
        ),
        Tool(
            name="add_role_embedding",
            func=lambda data: vector_tool.add_role_embedding(json.loads(data) if isinstance(data, str) else data),
            description="Add role/JD embedding to vector database. Input should be JSON with: role_id, jd_text, metadata (optional)"
        ),
        Tool(
            name="search_similar_resumes",
            func=lambda data: vector_tool.search_similar_resumes(json.loads(data) if isinstance(data, str) else data),
            description="Find resumes similar to a role. Input should be JSON with: role_id, top_k (optional, default 10)"
        ),
        Tool(
            name="get_similarity_score",
            func=lambda data: vector_tool.get_similarity_score(json.loads(data) if isinstance(data, str) else data),
            description="Calculate similarity score between resume and role. Input should be JSON with: candidate_id, role_id"
        )
    ]
    
    return tools
