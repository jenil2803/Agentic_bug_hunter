from pydantic import BaseModel, Field
from common.config import LLM_PROVIDER
from common.logger import get_logger
from common.rate_limiter import rate_limited
from common.mcp_client import MCPClient
from common.huggingface_model import HuggingFaceModel, MultiProviderLLM

logger = get_logger("bug_explainer")

def get_model():
    if LLM_PROVIDER == "huggingface":
        logger.info("Using HuggingFace models with fallback")
        return HuggingFaceModel()
    else:
        multi_provider = MultiProviderLLM()
        return multi_provider.get_primary_provider()


class BugExplanation(BaseModel):
    explanation: str
    bug_description: str
    correct_approach: str
    documentation_reference: str


class BugExplainer:
    def __init__(self):
        self.model = get_model()
        self.mcp_client = MCPClient()
        self.use_direct_api = isinstance(self.model, HuggingFaceModel)
        
        if not self.use_direct_api:
            from pydantic_ai import Agent
            self.agent = Agent(
                self.model,
                system_prompt=self._get_system_prompt(),
                output_type=BugExplanation,
            )
        else:
            self.agent = None
        
        logger.info("Bug Explainer initialized")
    
    def _get_system_prompt(self) -> str:
        return """You are a technical writer explaining C++ code bugs clearly and concisely.

Provide:
1. What's wrong with the code
2. Why it's wrong (reference documentation)
3. The correct approach

Keep it brief (2-3 sentences max)."""
    
    @rate_limited
    async def explain_bug(
        self,
        code_snippet: str,
        bug_line: int,
        bug_type: str,
        context: str = "",
        correct_code: str = ""
    ) -> str:
        logger.info(f"Generating explanation for bug at line {bug_line}")
        
        doc_context = await self.mcp_client.get_context_for_code(code_snippet, context)
        prompt = self._build_explanation_prompt(code_snippet, bug_line, bug_type, context, doc_context, correct_code)
        
        if self.use_direct_api:
            output_schema = {
                "explanation": "string - Clear bug explanation",
                "bug_description": "string - What the bug does wrong",
                "correct_approach": "string - How to fix it",
                "documentation_reference": "string - Reference to docs"
            }
            
            response = self.model.generate_structured(
                prompt=prompt,
                system_prompt=self._get_system_prompt(),
                output_schema=output_schema
            )
            explanation = BugExplanation(**response)
        else:
            result = await self.agent.run(prompt)
            explanation = getattr(result, 'data', getattr(result, 'output', result))
        
        formatted = self._format_explanation(explanation, bug_type, bug_line)
        logger.info(f"Generated explanation: {formatted[:100]}...")
        return formatted
    
    def _build_explanation_prompt(self, code: str, bug_line: int, bug_type: str, context: str, doc_context: str, correct_code: str) -> str:
        prompt_parts = [
            f"## Explain the bug in this C++ code\n",
            f"### Bug Type: {bug_type}",
            f"### Bug Location: Line {bug_line}",
            f"### Context: {context}\n" if context else "",
            f"### Buggy Code:\n```cpp\n{code}\n```\n",
            f"### Correct Code:\n```cpp\n{correct_code}\n```\n" if correct_code else "",
            f"### Documentation:\n{doc_context}\n" if doc_context else "",
            "\nGenerate a clear, concise explanation.",
        ]
        return "\n".join(prompt_parts)
    
    def _format_explanation(self, explanation: BugExplanation, bug_type: str, bug_line: int) -> str:
        formatted = f"{explanation.bug_description}. {explanation.correct_approach}"
        return " ".join(formatted.split())
    
    async def cleanup(self):
        await self.mcp_client.close()
