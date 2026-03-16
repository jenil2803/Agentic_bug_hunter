"""
Vedant's Work - Testing Framework

Unit tests for the bug hunter system.
"""

import pytest
import asyncio
from vedant.code_parser import CodeParser, parse_code_snippet
from vedant.bug_explainer import BugExplainer


class TestCodeParser:
    """Tests for code parsing utilities"""
    
    def test_count_lines(self):
        """Test line counting"""
        code = "line1\nline2\nline3"
        assert CodeParser.count_lines(code) == 3
    
    def test_extract_function_calls(self):
        """Test function call extraction"""
        code = """
        rdi.dc().vForce(1.0);
        some_function();
        """
        calls = CodeParser.extract_function_calls(code)
        assert 'vForce' in calls
        assert 'some_function' in calls
    
    def test_extract_api_patterns(self):
        """Test RDI API pattern extraction"""
        code = "rdi.dc().pin(\"A\").vForce(1.0).execute();"
        patterns = CodeParser.extract_api_patterns(code)
        assert len(patterns) > 0
        assert 'rdi.dc' in patterns[0]
    
    def test_find_line_with_pattern(self):
        """Test finding lines with specific patterns"""
        code = "line1\nrdi.begin()\nline3"
        lines = CodeParser.find_line_with_pattern(code, r'rdi\.begin')
        assert 2 in lines
    
    def test_normalize_code(self):
        """Test code normalization"""
        code = "// comment\ncode_line\n\n  \n/* multi\nline\ncomment */\nmore_code"
        normalized = CodeParser.normalize_code(code)
        assert '// comment' not in normalized
        assert '/* multi' not in normalized
        assert 'code_line' in normalized
    
    def test_identify_rdi_block(self):
        """Test RDI block identification"""
        code = "setup\nRDI_BEGIN();\ncode\nRDI_END();\ncleanup"
        start, end = CodeParser.identify_rdi_block(code)
        assert start == 2
        assert end == 4
    
    def test_parse_code_snippet(self):
        """Test complete code snippet parsing"""
        code = "RDI_BEGIN();\nrdi.dc().execute();\nRDI_END();"
        result = parse_code_snippet(code)
        
        assert 'line_count' in result
        assert 'function_calls' in result
        assert 'api_patterns' in result
        assert 'rdi_block' in result


class TestBugExplainer:
    """Tests for bug explanation agent"""
    
    @pytest.mark.asyncio
    async def test_explain_bug_basic(self):
        """Test basic bug explanation"""
        # Skip if no API key
        import os
        if not os.getenv('GEMINI_API_KEY'):
            pytest.skip("GEMINI_API_KEY not set")
        
        explainer = BugExplainer()
        
        code = "rdi.dc().vForce(35 V).vForceRange(30 V).execute();"
        
        explanation = await explainer.explain_bug(
            code_snippet=code,
            bug_line=1,
            bug_type="Range violation",
            context="AVI64 voltage forcing"
        )
        
        assert explanation is not None
        assert len(explanation) > 0
        
        await explainer.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
