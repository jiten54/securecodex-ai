from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AnalysisRequest(BaseModel):
    code: str = Field(..., max_length=50000, description="Source code to analyze")

class ComplexityMetrics(BaseModel):
    lines_of_code: int
    function_count: int
    variable_count: int

class AnalysisResponse(BaseModel):
    sensitive_findings: List[str]
    critical_functions: List[str]
    complexity: ComplexityMetrics
    recommended_level: str
    reasons: List[str]
    ai_explanation: Optional[str] = None
