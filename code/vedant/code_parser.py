"""
Vedant's Work - Code Parsing Utilities

Utilities for parsing and analyzing C++ code snippets.
"""

import re
from typing import List, Dict, Tuple
from common.logger import get_logger

logger = get_logger("code_parser")


class CodeParser:
    """Utilities for parsing C++ code"""
    
    @staticmethod
    def count_lines(code: str) -> int:
        """Count number of lines in code"""
        return len(code.strip().split('\n'))
    
    @staticmethod
    def extract_function_calls(code: str) -> List[str]:
        """
        Extract function calls from C++ code
        
        Returns:
            List of function names called in the code
        """
        # Pattern to match function calls: word followed by (
        pattern = r'\b(\w+)\s*\('
        matches = re.findall(pattern, code)
        
        # Filter out keywords
        cpp_keywords = {'if', 'for', 'while', 'switch', 'return', 'sizeof'}
        function_calls = [m for m in matches if m not in cpp_keywords]
        
        return function_calls
    
    @staticmethod
    def extract_api_patterns(code: str) -> List[str]:
        """
        Extract RDI API patterns from code
        
        Returns:
            List of RDI API method chains
        """
        # Pattern for rdi.* chains
        pattern = r'rdi\.[a-zA-Z_]\w*(?:\([^)]*\))?(?:\.[a-zA-Z_]\w*(?:\([^)]*\))?)*'
        matches = re.findall(pattern, code)
        return matches
    
    @staticmethod
    def find_line_with_pattern(code: str, pattern: str) -> List[int]:
        """
        Find line numbers containing a specific pattern
        
        Args:
            code: The code to search
            pattern: Regex pattern to find
            
        Returns:
            List of line numbers (1-indexed)
        """
        lines = code.split('\n')
        matching_lines = []
        
        for idx, line in enumerate(lines, 1):
            if re.search(pattern, line):
                matching_lines.append(idx)
        
        return matching_lines
    
    @staticmethod
    def extract_parameters(code: str, function_name: str) -> List[Tuple[int, List[str]]]:
        """
        Extract parameters from function calls
        
        Args:
            code: The code to analyze
            function_name: Name of the function to find
            
        Returns:
            List of tuples: (line_number, [parameters])
        """
        lines = code.split('\n')
        results = []
        
        for idx, line in enumerate(lines, 1):
            # Simple parameter extraction (doesn't handle nested parentheses perfectly)
            pattern = rf'{function_name}\s*\(([^)]+)\)'
            match = re.search(pattern, line)
            
            if match:
                params_str = match.group(1)
                params = [p.strip() for p in params_str.split(',')]
                results.append((idx, params))
        
        return results
    
    @staticmethod
    def normalize_code(code: str) -> str:
        """
        Normalize code by removing extra whitespace and comments
        
        Args:
            code: Raw code string
            
        Returns:
            Normalized code
        """
        # Remove single-line comments
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        
        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove extra blank lines
        lines = [line.rstrip() for line in code.split('\n')]
        lines = [line for line in lines if line.strip()]
        
        return '\n'.join(lines)
    
    @staticmethod
    def get_code_context(code: str, line_number: int, context_lines: int = 2) -> str:
        """
        Get surrounding context for a specific line
        
        Args:
            code: Full code
            line_number: Target line (1-indexed)
            context_lines: Number of lines before/after to include
            
        Returns:
            Code snippet with context
        """
        lines = code.split('\n')
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        
        context = lines[start:end]
        return '\n'.join(context)
    
    @staticmethod
    def identify_rdi_block(code: str) -> Tuple[int, int]:
        """
        Identify RDI_BEGIN() and RDI_END() block boundaries
        
        Returns:
            Tuple of (start_line, end_line) or (-1, -1) if not found
        """
        lines = code.split('\n')
        start_line = -1
        end_line = -1
        
        for idx, line in enumerate(lines, 1):
            if 'RDI_BEGIN' in line and start_line == -1:
                start_line = idx
            if 'RDI_END' in line and end_line == -1:
                end_line = idx
        
        return (start_line, end_line)


# Convenience function
def parse_code_snippet(code: str) -> Dict:
    """
    Parse a code snippet and extract useful information
    
    Returns:
        Dictionary with parsed information
    """
    parser = CodeParser()
    
    return {
        'line_count': parser.count_lines(code),
        'function_calls': parser.extract_function_calls(code),
        'api_patterns': parser.extract_api_patterns(code),
        'rdi_block': parser.identify_rdi_block(code),
        'normalized_code': parser.normalize_code(code)
    }
