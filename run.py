"""
Simple wrapper to run the bug hunter
"""
import subprocess
import sys
from pathlib import Path

# Run main.py from code folder
code_dir = Path(__file__).parent / "code"
main_py = code_dir / "main.py"

# Use the same Python interpreter
result = subprocess.run([sys.executable, str(main_py)], cwd=str(code_dir.parent))
sys.exit(result.returncode)
