"""
OpenAI Client for GUID Formula Classification

Handles OpenAI API calls for classifying accounting policy formulas
with FRS102 standard references.
"""

import asyncio
import openai
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ClassificationRequest:
    """Request object for formula classification."""
    guid: str
    sheet: str
    row_num: int
    formula_text: str
    cell_value: str
    instruction: str
    named_ranges: Dict[str, str]


@dataclass
class ClassificationResult:
    """Result object for formula classification."""
    guid: str
    classification: str
    confidence: Optional[str] = None
    error: Optional[str] = None
    api_response: Optional[str] = None


class OpenAIFormulaClassifier:
    """OpenAI client for classifying accounting policy formulas."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the OpenAI client with configuration."""
        if config_path is None:
            config_path_obj = Path(__file__).parent / "config.yaml"
        else:
            config_path_obj = Path(config_path)
        
        self.config = self._load_config(config_path_obj)
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Validate API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            raise
    
    def _build_prompt(self, request: ClassificationRequest) -> str:
        """Build the prompt for OpenAI API call."""
        # Start with the instruction
        prompt = request.instruction + "\n\n"
        
        # Add context about the accounting policy
        prompt += f"Accounting Policy Context:\n"
        prompt += f"- Sheet: {request.sheet}\n"
        prompt += f"- Row: {request.row_num}\n"
        prompt += f"- GUID: {request.guid}\n\n"
        
        # Add named ranges context if any are referenced in the formula
        if request.named_ranges:
            prompt += "Named Ranges Reference (for formula interpretation):\n"
            for name, description in request.named_ranges.items():
                if name.lower() in request.formula_text.lower():
                    prompt += f"- {name}: {description}\n"
            prompt += "\n"
        
        # Add the formula text
        prompt += f"Formula Text to Classify:\n{request.formula_text}\n\n"
        
        # Add cell value if available
        if request.cell_value and str(request.cell_value).strip():
            prompt += f"Current Cell Value: {request.cell_value}\n\n"
        
        # Add specific formatting instruction
        prompt += "Please respond with only the classification in the exact format specified in the instruction above."
        
        return prompt
    
    async def classify_formula(self, request: ClassificationRequest) -> ClassificationResult:
        """Classify a single formula using OpenAI API."""
        try:
            prompt = self._build_prompt(request)
            
            logger.debug(f"Making OpenAI API call for GUID {request.guid}")
            
            # Make the API call
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.config["openai"]["model"],
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert in UK accounting standards, specifically FRS102. You classify accounting policy text with precise standard references."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=self.config["openai"]["temperature"],
                max_tokens=self.config["openai"]["max_tokens"],
                timeout=self.config["openai"]["timeout"]
            )
            
            # Extract the classification from the response
            classification = response.choices[0].message.content.strip()
            
            logger.debug(f"Successfully classified GUID {request.guid}: {classification}")
            
            return ClassificationResult(
                guid=request.guid,
                classification=classification,
                api_response=classification
            )
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error for GUID {request.guid}: {e}")
            return ClassificationResult(
                guid=request.guid,
                classification=self.config["error_handling"]["default_classification_on_error"],
                error=f"OpenAI API Error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error classifying GUID {request.guid}: {e}")
            return ClassificationResult(
                guid=request.guid,
                classification=self.config["error_handling"]["default_classification_on_error"],
                error=f"Unexpected Error: {str(e)}"
            )
    
    async def classify_formulas_batch(self, requests: List[ClassificationRequest]) -> List[ClassificationResult]:
        """Classify multiple formulas in parallel batches."""
        results = []
        batch_size = self.config["batch_processing"]["batch_size"]
        delay = self.config["batch_processing"]["delay_between_batches"]
        
        logger.info(f"Processing {len(requests)} classification requests in batches of {batch_size}")
        
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i + batch_size]
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(requests)-1)//batch_size + 1}")
            
            # Process batch in parallel
            batch_tasks = [self.classify_formula(request) for request in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle any exceptions in the batch
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Exception in batch processing for GUID {batch[j].guid}: {result}")
                    results.append(ClassificationResult(
                        guid=batch[j].guid,
                        classification=self.config["error_handling"]["default_classification_on_error"],
                        error=f"Batch Processing Error: {str(result)}"
                    ))
                else:
                    results.append(result)
            
            # Delay between batches to respect rate limits
            if i + batch_size < len(requests):
                await asyncio.sleep(delay)
        
        logger.info(f"Completed classification of {len(results)} formulas")
        return results


def create_classification_request(
    guid: str,
    sheet: str,
    row_num: int,
    formula_text: str,
    cell_value: str,
    instruction: str,
    named_ranges: Dict[str, str]
) -> ClassificationRequest:
    """Factory function to create a classification request."""
    return ClassificationRequest(
        guid=guid,
        sheet=sheet,
        row_num=row_num,
        formula_text=formula_text,
        cell_value=cell_value,
        instruction=instruction,
        named_ranges=named_ranges
    )