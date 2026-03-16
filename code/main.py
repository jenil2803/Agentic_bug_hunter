"""
Main entry point for the Bug Hunter application
"""

import asyncio
import sys
import codecs
from pathlib import Path

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add code directory to path
code_dir = Path(__file__).parent
sys.path.insert(0, str(code_dir))

from soham.orchestrator import BugHunterOrchestrator
from common.logger import get_logger
from common.config import PROJECT_ROOT

logger = get_logger("main")


async def main():
    """Main application entry point"""
    logger.info("="*80)
    logger.info("AGENTIC BUG HUNTER")
    logger.info("="*80)
    
    # Initialize orchestrator
    orchestrator = BugHunterOrchestrator()
    
    try:
        # Check for samples.csv
        samples_path = PROJECT_ROOT / "samples.csv"
        
        if not samples_path.exists():
            logger.error(f"Dataset not found: {samples_path}")
            print("\nPlease ensure samples.csv is in the project root directory.")
            return
        
        logger.info(f"Dataset found: {samples_path}")
        
        # Run bug detection
        print("\n🔍 Starting bug detection...")
        print("This may take a few minutes depending on the dataset size.\n")
        
        results = await orchestrator.run_bug_detection(str(samples_path))
        
        # Display summary
        bugs_found = sum(1 for r in results if r['Bug Line'] > 0)
        
        print("\n" + "="*80)
        print("✅ BUG DETECTION COMPLETED")
        print("="*80)
        print(f"📊 Total snippets analyzed: {len(results)}")
        print(f"🐛 Bugs detected: {bugs_found}")
        print(f"📁 Results saved to: {PROJECT_ROOT / 'output'}")
        print(f"📄 Report generated in: {PROJECT_ROOT / 'docs'}")
        print("="*80 + "\n")
        
    except KeyboardInterrupt:
        logger.info("Detection interrupted by user")
        print("\n\n⚠️  Detection interrupted. Cleaning up...")
    
    except Exception as e:
        logger.error(f"Error during detection: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
    
    finally:
        await orchestrator.cleanup()
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
