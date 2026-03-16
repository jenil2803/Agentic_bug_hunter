from pydantic import BaseModel, Field
from typing import Optional
from common.config import LLM_PROVIDER
from common.logger import get_logger
from common.rate_limiter import rate_limited
from common.mcp_client import MCPClient
from common.huggingface_model import HuggingFaceModel, MultiProviderLLM

logger = get_logger("bug_detector")

def get_model():
    if LLM_PROVIDER == "huggingface":
        logger.info("Using HuggingFace models with fallback")
        return HuggingFaceModel()
    else:
        multi_provider = MultiProviderLLM()
        return multi_provider.get_primary_provider()


class BugDetectionResult(BaseModel):
    has_bug: bool
    bug_line: Optional[int] = None
    bug_type: Optional[str] = None
    confidence: float
    reasoning: str


class BugDetector:
    def __init__(self):
        self.model = get_model()
        self.mcp_client = MCPClient()
        self.use_direct_api = isinstance(self.model, HuggingFaceModel)
        
        if not self.use_direct_api:
            from pydantic_ai import Agent
            self.agent = Agent(
                self.model,
                system_prompt=self._get_system_prompt(),
                output_type=BugDetectionResult,
            )
        else:
            self.agent = None
        
        logger.info("Bug Detector initialized")
    
    def _get_system_prompt(self) -> str:
        return """You are an expert C++ code analyzer specializing in SmartRDI API bugs.

Analyze code for:
- API misuse (wrong functions, parameters, order)
- Range violations
- Logic errors
- Type mismatches

Identify the exact line number where bugs occur and provide confidence scores."""
    
    @rate_limited
    async def detect_bug(
        self,
        code_id: str,
        code_snippet: str,
        context: str = "",
        correct_code: Optional[str] = None,
        explanation: Optional[str] = None
    ) -> BugDetectionResult:
        logger.info(f"Analyzing code snippet {code_id}")
        
        doc_context = await self.mcp_client.get_context_for_code(code_snippet, context)
        prompt = self._build_detection_prompt(code_snippet, context, doc_context, correct_code, explanation)
        
        if self.use_direct_api:
            output_schema = {
                "has_bug": "boolean - Whether a bug was detected",
                "bug_line": "integer or null - Line number where bug is located",
                "bug_type": "string or null - Type of bug detected",
                "confidence": "float - Confidence score (0-1)",
                "reasoning": "string - Reasoning for detection"
            }
            
            response = self.model.generate_structured(
                prompt=prompt,
                system_prompt=self._get_system_prompt(),
                output_schema=output_schema
            )
            detection_result = BugDetectionResult(**response)
        else:
            result = await self.agent.run(prompt)
            detection_result = getattr(result, 'data', getattr(result, 'output', result))
        
        logger.info(f"Detection result for {code_id}: bug={detection_result.has_bug}, line={detection_result.bug_line}")
        return detection_result
    
    def _build_detection_prompt(self, code: str, context: str, doc_context: str, correct_code: Optional[str], explanation: Optional[str]) -> str:
        prompt_parts = [
            "## Analyze this C++ code for bugs\n",
            f"### Context:\n{context}\n" if context else "",
            f"### Code:\n```cpp\n{code}\n```\n",
            f"### Documentation:\n{doc_context}\n" if doc_context else "",
            f"### Correct Version:\n```cpp\n{correct_code}\n```\n" if correct_code else "",
            f"### Expected Bug:\n{explanation}\n" if explanation else "",
            "\nIdentify exact line number, bug type, and confidence level.",
        ]
        return "\n".join(prompt_parts)
    
    async def cleanup(self):
        await self.mcp_client.close()
