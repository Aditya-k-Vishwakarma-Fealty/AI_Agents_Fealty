"""
ChromaDB client for vector storage and similarity search.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


class ChromaClient:
    """ChromaDB client wrapper for managing resume and role embeddings."""
    
    def __init__(self):
        """Initialize ChromaDB client with persistent storage."""
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=settings.chroma_persist_directory,
                anonymized_telemetry=False
            )
        )
        self._init_collections()
    
    def _init_collections(self):
        """Initialize or get existing collections."""
        try:
            # Resume collection
            self.resumes_collection = self.client.get_or_create_collection(
                name=settings.chroma_collection_resumes,
                metadata={"description": "Resume embeddings for candidate matching"}
            )
            
            # Roles collection
            self.roles_collection = self.client.get_or_create_collection(
                name=settings.chroma_collection_roles,
                metadata={"description": "Job description embeddings for role matching"}
            )
            
            logger.info("ChromaDB collections initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB collections: {e}")
            raise
    
    def add_resume_embedding(
        self,
        candidate_id: int,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add resume embedding to ChromaDB.
        
        Args:
            candidate_id: Candidate ID
            text: Resume text content
            metadata: Additional metadata (skills, experience, etc.)
        
        Returns:
            str: Document ID in ChromaDB
        """
        try:
            doc_id = f"resume_{candidate_id}"
            
            # Prepare metadata
            meta = metadata or {}
            meta["candidate_id"] = candidate_id
            meta["type"] = "resume"
            
            # Add to collection
            self.resumes_collection.add(
                documents=[text],
                metadatas=[meta],
                ids=[doc_id]
            )
            
            logger.info(f"Added resume embedding for candidate {candidate_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Error adding resume embedding: {e}")
            raise
    
    def add_role_embedding(
        self,
        role_id: int,
        jd_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add role/JD embedding to ChromaDB.
        
        Args:
            role_id: Role ID
            jd_text: Job description text
            metadata: Additional metadata (required skills, experience, etc.)
        
        Returns:
            str: Document ID in ChromaDB
        """
        try:
            doc_id = f"role_{role_id}"
            
            # Prepare metadata
            meta = metadata or {}
            meta["role_id"] = role_id
            meta["type"] = "role"
            
            # Add to collection
            self.roles_collection.add(
                documents=[jd_text],
                metadatas=[meta],
                ids=[doc_id]
            )
            
            logger.info(f"Added role embedding for role {role_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Error adding role embedding: {e}")
            raise
    
    def search_similar_resumes(
        self,
        role_id: int,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find resumes similar to a role.
        
        Args:
            role_id: Role ID to match against
            top_k: Number of top matches to return
        
        Returns:
            List of matching resumes with scores
        """
        try:
            # Get role embedding
            role_doc_id = f"role_{role_id}"
            role_result = self.roles_collection.get(ids=[role_doc_id])
            
            if not role_result["documents"]:
                logger.warning(f"Role {role_id} not found in ChromaDB")
                return []
            
            role_text = role_result["documents"][0]
            
            # Search for similar resumes
            results = self.resumes_collection.query(
                query_texts=[role_text],
                n_results=top_k
            )
            
            # Format results
            matches = []
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    matches.append({
                        "candidate_id": results["metadatas"][0][i].get("candidate_id"),
                        "similarity_score": 1 - results["distances"][0][i],  # Convert distance to similarity
                        "document_id": doc_id
                    })
            
            logger.info(f"Found {len(matches)} similar resumes for role {role_id}")
            return matches
        except Exception as e:
            logger.error(f"Error searching similar resumes: {e}")
            raise
    
    def get_similarity_score(
        self,
        candidate_id: int,
        role_id: int
    ) -> float:
        """
        Calculate similarity score between a resume and role.
        
        Args:
            candidate_id: Candidate ID
            role_id: Role ID
        
        Returns:
            float: Similarity score (0-1)
        """
        try:
            resume_doc_id = f"resume_{candidate_id}"
            role_doc_id = f"role_{role_id}"
            
            # Get role text
            role_result = self.roles_collection.get(ids=[role_doc_id])
            if not role_result["documents"]:
                logger.warning(f"Role {role_id} not found")
                return 0.0
            
            role_text = role_result["documents"][0]
            
            # Query resume collection
            results = self.resumes_collection.query(
                query_texts=[role_text],
                n_results=100,  # Get more to ensure we find the specific candidate
                where={"candidate_id": candidate_id}
            )
            
            # Find the specific candidate in results
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    if doc_id == resume_doc_id:
                        similarity = 1 - results["distances"][0][i]
                        logger.info(f"Similarity score for candidate {candidate_id} and role {role_id}: {similarity}")
                        return similarity
            
            logger.warning(f"Could not calculate similarity for candidate {candidate_id} and role {role_id}")
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating similarity score: {e}")
            raise
    
    def delete_resume(self, candidate_id: int):
        """Delete resume embedding from ChromaDB."""
        try:
            doc_id = f"resume_{candidate_id}"
            self.resumes_collection.delete(ids=[doc_id])
            logger.info(f"Deleted resume embedding for candidate {candidate_id}")
        except Exception as e:
            logger.error(f"Error deleting resume embedding: {e}")
            raise
    
    def delete_role(self, role_id: int):
        """Delete role embedding from ChromaDB."""
        try:
            doc_id = f"role_{role_id}"
            self.roles_collection.delete(ids=[doc_id])
            logger.info(f"Deleted role embedding for role {role_id}")
        except Exception as e:
            logger.error(f"Error deleting role embedding: {e}")
            raise


# Global ChromaDB client instance
chroma_client = ChromaClient()
