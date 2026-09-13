from abc import ABC, abstractmethod
from typing import Dict, Any

class MathExtractor(ABC):
    """
    Base interface for specialized mathematical document extraction.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the extractor (e.g., 'NougatExtractor')"""
        pass
        
    @abstractmethod
    def load_model(self) -> None:
        """Load any required ML models or resources into memory."""
        pass
        
    @abstractmethod
    def extract_page(self, pdf_path: str, page_num: int) -> Dict[str, Any]:
        """
        Extract mathematical and textual content from a specific page.
        
        Args:
            pdf_path: Path to the PDF document.
            page_num: 1-indexed page number.
            
        Returns:
            Dict containing:
            - 'text': Extracted markdown/LaTeX text
            - 'execution_time_seconds': Time taken to extract
            - 'success': Boolean indicating success
            - 'error': Error message if failed
        """
        pass
