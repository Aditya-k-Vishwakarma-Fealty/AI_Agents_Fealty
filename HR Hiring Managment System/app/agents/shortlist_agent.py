"""
Shortlisting Agent - Makes shortlist/reject decisions based on scores.
"""
from typing import Dict, Any, List
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


class ShortlistAgent:
    """Agent for making shortlisting decisions."""
    
    def __init__(self):
        """Initialize the shortlisting agent."""
        self.threshold = settings.shortlist_threshold
    
    def evaluate_candidate(
        self,
        candidate_score: float,
        match_percentage: float,
        threshold: float = None
    ) -> Dict[str, Any]:
        """
        Evaluate if candidate should be shortlisted.
        
        Args:
            candidate_score: Resume score (0-100)
            match_percentage: Match percentage (0-100)
            threshold: Custom threshold (optional, uses default if not provided)
        
        Returns:
            Dict with decision and reasoning
        """
        try:
            effective_threshold = threshold if threshold is not None else self.threshold
            
            # Calculate combined score (average of resume score and match percentage)
            combined_score = (candidate_score + match_percentage) / 2
            
            # Make decision
            if combined_score >= effective_threshold:
                decision = "shortlisted"
                reasoning = f"Candidate meets the threshold with a combined score of {combined_score:.1f} (threshold: {effective_threshold})"
            elif combined_score >= (effective_threshold - 10):
                decision = "hold"
                reasoning = f"Candidate is close to threshold with score {combined_score:.1f}. Consider for waitlist."
            else:
                decision = "rejected"
                reasoning = f"Candidate does not meet threshold. Score: {combined_score:.1f} (threshold: {effective_threshold})"
            
            logger.info(f"Shortlist decision: {decision} (score: {combined_score:.1f})")
            
            return {
                "status": "success",
                "decision": decision,
                "combined_score": combined_score,
                "reasoning": reasoning
            }
        except Exception as e:
            logger.error(f"Error in shortlisting evaluation: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def batch_evaluate(
        self,
        candidates: List[Dict[str, Any]],
        threshold: float = None
    ) -> Dict[str, Any]:
        """
        Evaluate multiple candidates for shortlisting.
        
        Args:
            candidates: List of candidate score data
            threshold: Custom threshold (optional)
        
        Returns:
            Dict with categorized candidates
        """
        try:
            shortlisted = []
            hold = []
            rejected = []
            
            for candidate in candidates:
                result = self.evaluate_candidate(
                    candidate_score=candidate.get("resume_score", 0),
                    match_percentage=candidate.get("match_percentage", 0),
                    threshold=threshold
                )
                
                if result["status"] == "success":
                    candidate_info = {
                        "candidate_id": candidate.get("candidate_id"),
                        "combined_score": result["combined_score"],
                        "reasoning": result["reasoning"]
                    }
                    
                    if result["decision"] == "shortlisted":
                        shortlisted.append(candidate_info)
                    elif result["decision"] == "hold":
                        hold.append(candidate_info)
                    else:
                        rejected.append(candidate_info)
            
            logger.info(
                f"Batch evaluation complete: {len(shortlisted)} shortlisted, "
                f"{len(hold)} on hold, {len(rejected)} rejected"
            )
            
            return {
                "status": "success",
                "shortlisted": shortlisted,
                "hold": hold,
                "rejected": rejected,
                "summary": {
                    "total": len(candidates),
                    "shortlisted_count": len(shortlisted),
                    "hold_count": len(hold),
                    "rejected_count": len(rejected)
                }
            }
        except Exception as e:
            logger.error(f"Error in batch evaluation: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


# Global agent instance
shortlist_agent = ShortlistAgent()
