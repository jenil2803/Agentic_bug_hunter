"""
Soham's Work - Main Orchestrator

Coordinates all agents to perform bug detection on datasets.
"""

import asyncio
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import time

from soham.bug_detector import BugDetector
from vedant.bug_explainer import BugExplainer
from vedant.code_parser import parse_code_snippet
from jenil.vector_db import BugDatabase
from jenil.documentation import DocumentationGenerator

from common.logger import get_logger
from common.csv_utils import read_dataset_csv, write_output_csv, append_result_to_csv
from common.config import PROJECT_ROOT, OUTPUT_DIR

logger = get_logger("orchestrator")


class BugHunterOrchestrator:
    """Main orchestrator for the bug hunting system"""
    
    def __init__(self):
        """Initialize all components"""
        logger.info("Initializing Bug Hunter Orchestrator...")
        
        self.bug_detector = BugDetector()
        self.bug_explainer = BugExplainer()
        self.database = BugDatabase()
        self.doc_generator = DocumentationGenerator()
        
        logger.info("Orchestrator initialized successfully")
    
    async def analyze_single_snippet(
        self,
        code_id: str,
        code_snippet: str,
        context: str = "",
        correct_code: str = "",
        expected_explanation: str = ""
    ) -> Dict:
        """
        Analyze a single code snippet
        
        Args:
            code_id: Unique identifier for the code
            code_snippet: The C++ code to analyze
            context: Additional context about the code
            correct_code: Correct version (for reference)
            expected_explanation: Expected bug description (for reference)
            
        Returns:
            Dictionary with ID, Bug Line, and Explanation
        """
        logger.info(f"Analyzing snippet {code_id}...")
        
        try:
            # Parse the code first
            parsed_info = parse_code_snippet(code_snippet)
            logger.debug(f"Parsed {code_id}: {parsed_info['line_count']} lines, "
                        f"{len(parsed_info['function_calls'])} function calls")
            
            # Detect bugs
            detection_result = await self.bug_detector.detect_bug(
                code_id=code_id,
                code_snippet=code_snippet,
                context=context,
                correct_code=correct_code,
                explanation=expected_explanation
            )
            
            # If bug detected, generate explanation
            if detection_result.has_bug and detection_result.bug_line:
                logger.info(f"Bug detected in {code_id} at line {detection_result.bug_line}")
                
                explanation = await self.bug_explainer.explain_bug(
                    code_snippet=code_snippet,
                    bug_line=detection_result.bug_line,
                    bug_type=detection_result.bug_type or "Unknown",
                    context=context,
                    correct_code=correct_code
                )
                
                # Store in database
                self.database.add_bug_result(
                    code_id=code_id,
                    code_snippet=code_snippet,
                    bug_line=detection_result.bug_line,
                    explanation=explanation,
                    metadata={
                        'bug_type': detection_result.bug_type,
                        'confidence': detection_result.confidence,
                        'context': context
                    }
                )
                
                return {
                    'ID': code_id,
                    'Bug Line': detection_result.bug_line,
                    'Explanation': explanation
                }
            
            else:
                logger.warning(f"No bug detected in {code_id}")
                return {
                    'ID': code_id,
                    'Bug Line': 0,
                    'Explanation': "No bug detected"
                }
        
        except Exception as e:
            logger.error(f"Error analyzing {code_id}: {e}")
            return {
                'ID': code_id,
                'Bug Line': -1,
                'Explanation': f"Error during analysis: {str(e)}"
            }
    
    async def run_bug_detection(
        self,
        csv_path: str,
        output_filename: str = None
    ) -> List[Dict]:
        """
        Run bug detection on a CSV dataset with real-time CSV writing
        
        Args:
            csv_path: Path to input CSV file
            output_filename: Optional custom output filename
            
        Returns:
            List of detection results
        """
        logger.info(f"Starting bug detection run on {csv_path}")
        start_time = time.time()
        
        # Read dataset
        dataset = read_dataset_csv(Path(csv_path))
        logger.info(f"Loaded {len(dataset)} code snippets from dataset")
        
        # Always use output.csv as the filename
        output_filename = "output.csv"
        
        # Create output path
        output_path = OUTPUT_DIR / output_filename
        logger.info(f"Results will be written in real-time to: {output_path}")
        
        # Process each snippet
        results = []
        cached_count = 0
        processed_count = 0
        
        for idx, row in enumerate(dataset, 1):
            code_id = row.get('ID', str(idx))
            logger.info(f"Processing snippet {idx}/{len(dataset)} (ID: {code_id})")
            
            # Check if we already have this result cached
            cached_result = self.database.get_cached_result(code_id)
            
            if cached_result:
                logger.info(f"✓ Using cached result for ID {code_id}")
                result = cached_result
                cached_count += 1
            else:
                # Analyze the snippet
                logger.info(f"→ Analyzing new snippet ID {code_id}")
                result = await self.analyze_single_snippet(
                    code_id=code_id,
                    code_snippet=row.get('Code', ''),
                    context=row.get('Context', ''),
                    correct_code=row.get('Correct Code', ''),
                    expected_explanation=row.get('Explanation', '')
                )
                processed_count += 1
            
            # Append result to CSV immediately (real-time writing)
            append_result_to_csv(result, output_path)
            logger.info(f"✓ Result for ID {code_id} written to CSV")
            
            results.append(result)
            
            # Log progress
            if idx % 5 == 0:
                logger.info(f"Progress: {idx}/{len(dataset)} snippets | " +
                          f"Cached: {cached_count}, Processed: {processed_count}")
        
        # Calculate execution time
        execution_time = time.time() - start_time
        logger.info(f"Bug detection completed in {execution_time:.2f} seconds")
        logger.info(f"Summary: {cached_count} cached, {processed_count} newly processed")
        logger.info(f"Final results saved to: {output_path}")
        
        # Generate report
        report_path = self.doc_generator.generate_run_report(
            results=results,
            execution_time=execution_time,
            metadata={
                'input_file': csv_path,
                'total_snippets': len(dataset),
                'bugs_detected': sum(1 for r in results if r['Bug Line'] > 0),
                'cached_results': cached_count,
                'newly_processed': processed_count
            }
        )
        logger.info(f"Report generated: {report_path}")
        
        return results
    
    async def cleanup(self):
        """Cleanup all resources"""
        logger.info("Cleaning up orchestrator resources...")
        await self.bug_detector.cleanup()
        await self.bug_explainer.cleanup()
        logger.info("Cleanup completed")


async def main():
    """Main entry point for bug detection"""
    # Initialize orchestrator
    orchestrator = BugHunterOrchestrator()
    
    try:
        # Run on samples.csv
        samples_path = PROJECT_ROOT / "samples.csv"
        
        if samples_path.exists():
            logger.info(f"Running bug detection on {samples_path}")
            results = await orchestrator.run_bug_detection(str(samples_path))
            
            # Print summary
            print("\n" + "="*80)
            print("BUG DETECTION SUMMARY")
            print("="*80)
            print(f"Total snippets analyzed: {len(results)}")
            print(f"Bugs detected: {sum(1 for r in results if r['Bug Line'] > 0)}")
            print(f"Results saved to: {PROJECT_ROOT / 'output'}")
            print("="*80 + "\n")
        else:
            logger.error(f"Samples file not found: {samples_path}")
    
    finally:
        await orchestrator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
