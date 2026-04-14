import ast
import re
import os
from typing import List, Dict, Any, Tuple
from app.schemas.ai import ComplexityMetrics, AnalysisResponse
from app.core.config import settings

# Optional LLM Integration
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

class CodeAnalysisService:
    """
    AI Module for Smart Code Analysis.
    Detects sensitive patterns, critical functions, and suggests obfuscation levels.
    """

    SENSITIVE_PATTERNS = [
        r"(?i)api_key\s*[:=]\s*['\"]([^'\"]+)['\"]",
        r"(?i)password\s*[:=]\s*['\"]([^'\"]+)['\"]",
        r"(?i)secret\s*[:=]\s*['\"]([^'\"]+)['\"]",
        r"(?i)token\s*[:=]\s*['\"]([^'\"]+)['\"]",
        r"sk-[a-zA-Z0-9]{32,}",  # Generic OpenAI-like keys
        r"AIza[0-9A-Za-z-_]{35}"  # Google API Keys
    ]

    CRITICAL_KEYWORDS = {
        "auth": ["login", "signup", "authenticate", "authorize", "verify_password", "jwt"],
        "payment": ["stripe", "paypal", "checkout", "payment", "transaction", "credit_card"],
        "database": ["db", "session", "execute", "commit", "query", "repository"]
    }

    def __init__(self):
        if HAS_GEMINI and os.getenv("GEMINI_API_KEY"):
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    def detect_sensitive_patterns(self, code: str) -> List[str]:
        """Detect hardcoded secrets using regex."""
        findings = []
        for pattern in self.SENSITIVE_PATTERNS:
            matches = re.findall(pattern, code)
            if matches:
                findings.append(f"Potential secret found matching pattern: {pattern}")
        return findings

    def detect_critical_functions(self, code: str) -> List[str]:
        """Detect critical business logic using AST analysis."""
        critical_found = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    name = node.name.lower()
                    for category, keywords in self.CRITICAL_KEYWORDS.items():
                        if any(kw in name for kw in keywords):
                            critical_found.append(f"Critical {category} function: {node.name}")
        except SyntaxError:
            pass
        return critical_found

    def complexity_analysis(self, code: str) -> ComplexityMetrics:
        """Calculate basic code complexity metrics."""
        lines = code.splitlines()
        function_count = 0
        variable_count = 0
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_count += 1
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    variable_count += 1
        except SyntaxError:
            pass

        return ComplexityMetrics(
            lines_of_code=len(lines),
            function_count=function_count,
            variable_count=variable_count
        )

    def suggest_obfuscation_strategy(self, code: str) -> Tuple[str, List[str]]:
        """Suggest optimal obfuscation level based on analysis."""
        reasons = []
        sensitive = self.detect_sensitive_patterns(code)
        critical = self.detect_critical_functions(code)
        complexity = self.complexity_analysis(code)

        if sensitive:
            reasons.append("Hardcoded sensitive data detected.")
            return "high", reasons
        
        if len(critical) > 3 or complexity.function_count > 10:
            reasons.append("High business logic density or complexity.")
            return "medium", reasons
        
        reasons.append("Low complexity and no sensitive data found.")
        return "low", reasons

    async def get_ai_explanation(self, code: str) -> str:
        """Optional: Get advanced risk analysis from Gemini."""
        if not self.model:
            return "Advanced AI analysis is currently disabled (No API Key or Library)."

        prompt = (
            "Analyze the following code for security risks and suggest obfuscation strategies. "
            "Identify sensitive parts and explain why they need protection.\n\n"
            f"Code:\n{code[:5000]}" # Limit snippet size
        )
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI Analysis failed: {str(e)}"

    async def analyze_code(self, code: str) -> AnalysisResponse:
        """Full analysis pipeline."""
        sensitive = self.detect_sensitive_patterns(code)
        critical = self.detect_critical_functions(code)
        complexity = self.complexity_analysis(code)
        level, reasons = self.suggest_obfuscation_strategy(code)
        
        explanation = await self.get_ai_explanation(code)

        return AnalysisResponse(
            sensitive_findings=sensitive,
            critical_functions=critical,
            complexity=complexity,
            recommended_level=level,
            reasons=reasons,
            ai_explanation=explanation
        )
