"""
Jenil's Work - Documentation Generator

Generates comprehensive documentation for the project.
"""

from datetime import datetime
from typing import List, Dict
from pathlib import Path
from common.config import PROJECT_ROOT
from common.logger import get_logger

logger = get_logger("doc_generator")


class DocumentationGenerator:
    """Generates project documentation"""
    
    def __init__(self, output_dir: Path = PROJECT_ROOT / "docs"):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_run_report(
        self,
        results: List[Dict],
        execution_time: float,
        metadata: Dict = None
    ) -> Path:
        """
        Generate a markdown report for a detection run
        
        Args:
            results: List of detection results
            execution_time: Total execution time in seconds
            metadata: Additional metadata about the run
            
        Returns:
            Path to generated report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"run_report_{timestamp}.md"
        
        # Calculate statistics
        total_bugs = len(results)
        unique_bug_types = len(set(r.get('bug_type', 'Unknown') for r in results))
        
        # Generate report content
        report_content = self._build_report_content(
            results, execution_time, total_bugs, unique_bug_types, metadata
        )
        
        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Generated run report: {report_path}")
        return report_path
    
    def _build_report_content(
        self,
        results: List[Dict],
        execution_time: float,
        total_bugs: int,
        unique_bug_types: int,
        metadata: Dict
    ) -> str:
        """Build the markdown report content"""
        lines = [
            "# Bug Detection Run Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Execution Time:** {execution_time:.2f} seconds",
            "",
            "## Summary",
            "",
            f"- **Total Bugs Detected:** {total_bugs}",
            f"- **Unique Bug Types:** {unique_bug_types}",
            f"- **Average Time per Bug:** {execution_time/max(total_bugs, 1):.2f} seconds",
            "",
            "## Detected Bugs",
            ""
        ]
        
        # Add bug details
        for idx, result in enumerate(results, 1):
            lines.extend([
                f"### Bug #{idx}: {result.get('ID', 'Unknown')}",
                "",
                f"- **Line:** {result.get('Bug Line', 'N/A')}",
                f"- **Explanation:** {result.get('Explanation', 'No explanation provided')}",
                ""
            ])
        
        if metadata:
            lines.extend([
                "## Additional Information",
                "",
                *[f"- **{k}:** {v}" for k, v in metadata.items()],
                ""
            ])
        
        return "\n".join(lines)
    
    def generate_architecture_doc(self):
        """Generate architecture documentation"""
        doc_path = self.output_dir / "ARCHITECTURE.md"
        
        content = """# Bug Hunter Architecture

## Overview

The Agentic Bug Hunter is a multi-agent system designed to detect and explain bugs in C++ code, specifically for SmartRDI API usage.

## System Components

### 1. Core Agents (Soham)

#### Bug Detector Agent
- **Purpose:** Analyze C++ code snippets to detect bugs
- **Technology:** PydanticAI + Gemini 2.0 Flash
- **Input:** Code snippet, context, documentation
- **Output:** BugDetectionResult (has_bug, bug_line, confidence, reasoning)

### 2. Explanation System (Vedant)

#### Bug Explainer Agent
- **Purpose:** Generate clear, concise bug explanations
- **Technology:** PydanticAI + Gemini 2.0 Flash
- **Input:** Code, bug location, bug type
- **Output:** Formatted explanation string

#### Code Parser
- **Purpose:** Parse and analyze C++ code structure
- **Technology:** Python regex and string processing
- **Features:**
  - Extract function calls
  - Identify API patterns
  - Find RDI blocks
  - Normalize code

### 3. Data Management (Jenil)

#### Vector Database
- **Purpose:** Store and retrieve bug detection history
- **Technology:** ChromaDB
- **Features:**
  - Persistent storage
  - Similarity search
  - Statistics tracking

#### Documentation Generator
- **Purpose:** Create reports and documentation
- **Output:** Markdown reports, architecture docs

### 4. User Interface (Diti)

#### Web Dashboard
- **Purpose:** Provide user-friendly interface
- **Technology:** React.js + Next.js
- **Features:**
  - Upload CSV datasets
  - View detection results
  - Download CSV reports
  - History visualization

## Data Flow

```
1. User uploads CSV dataset
   ↓
2. Main Orchestrator reads and parses data
   ↓
3. For each code snippet:
   a. MCP Client fetches relevant documentation
   b. Bug Detector analyzes code
   c. If bug found: Bug Explainer generates explanation
   d. Result stored in Vector DB
   ↓
4. Results compiled to CSV
   ↓
5. Report generated and displayed in UI
```

## MCP Integration

The system uses Model Context Protocol (MCP) to access a vector database of SmartRDI documentation:

- **MCP Server:** FastMCP running on port 8003
- **Search Tool:** `search_documents(query)` - Returns relevant docs
- **Embeddings:** BGE-base-en-v1.5 model
- **Storage:** LlamaIndex vector store

## Rate Limiting

To respect API limits:
- Token bucket algorithm
- Max 10 requests per minute (configurable)
- Automatic retry with backoff

## Team Responsibilities

- **Soham:** Core agent architecture, bug detection
- **Vedant:** Explanation generation, code parsing, testing
- **Diti:** Frontend UI, dashboard, visualization
- **Jenil:** Database management, documentation, optimization

## Technology Stack

- **AI/ML:** Google Gemini 2.0 Flash, PydanticAI
- **Vector DB:** ChromaDB, LlamaIndex
- **MCP:** FastMCP server
- **Frontend:** React.js, Next.js, TailwindCSS
- **Backend:** Python 3.10+, asyncio
- **Testing:** pytest

## Configuration

See `common/config.py` for all configurable parameters.

## Future Enhancements

- [ ] Support for more programming languages
- [ ] Real-time code analysis
- [ ] Integration with IDEs
- [ ] Automated fix suggestions
- [ ] Machine learning model fine-tuning
"""
        
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Generated architecture documentation: {doc_path}")
        return doc_path
    
    def generate_api_doc(self):
        """Generate API documentation"""
        doc_path = self.output_dir / "API.md"
        
        content = """# Bug Hunter API Documentation

## Main Orchestrator

### `run_bug_detection(csv_path: str) -> List[Dict]`

Runs bug detection on a CSV dataset.

**Parameters:**
- `csv_path` (str): Path to input CSV file

**Returns:**
- List of dictionaries with keys: `ID`, `Bug Line`, `Explanation`

**Example:**
```python
from soham.orchestrator import BugHunterOrchestrator

orchestrator = BugHunterOrchestrator()
results = await orchestrator.run_bug_detection("samples.csv")
```

## Bug Detector

### `BugDetector.detect_bug()`

Detects bugs in a code snippet.

**Parameters:**
- `code_id` (str): Unique identifier
- `code_snippet` (str): C++ code to analyze
- `context` (str): Additional context
- `correct_code` (Optional[str]): Correct version for reference
- `explanation` (Optional[str]): Expected bug type

**Returns:**
- `BugDetectionResult` object

## Bug Explainer

### `BugExplainer.explain_bug()`

Generates bug explanation.

**Parameters:**
- `code_snippet` (str): The buggy code
- `bug_line` (int): Line number of bug
- `bug_type` (str): Type of bug
- `context` (str): Code context
- `correct_code` (str): Correct version

**Returns:**
- Formatted explanation string

## Vector Database

### `BugDatabase.add_bug_result()`

Stores bug detection result.

**Parameters:**
- `code_id` (str): Unique ID
- `code_snippet` (str): Code analyzed
- `bug_line` (int): Bug line number
- `explanation` (str): Bug explanation
- `metadata` (Optional[Dict]): Additional metadata

### `BugDatabase.search_similar_bugs()`

Searches for similar bugs in history.

**Parameters:**
- `query` (str): Search query
- `n_results` (int): Number of results

**Returns:**
- List of similar bug records

## Code Parser

### `CodeParser.extract_api_patterns(code: str) -> List[str]`

Extracts RDI API patterns from code.

### `CodeParser.identify_rdi_block(code: str) -> Tuple[int, int]`

Identifies RDI_BEGIN() and RDI_END() boundaries.

## MCP Client

### `MCPClient.search_documents(query: str) -> List[Dict]`

Searches documentation using vector similarity.

### `MCPClient.get_context_for_code(code_snippet: str, context: str) -> str`

Gets relevant documentation for a code snippet.

## CSV Utilities

### `read_dataset_csv(csv_path: Path) -> List[Dict]`

Reads input CSV dataset.

### `write_output_csv(results: List[Dict], output_filename: str) -> Path`

Writes results to CSV file.
"""
        
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Generated API documentation: {doc_path}")
        return doc_path
