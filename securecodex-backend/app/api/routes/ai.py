from fastapi import APIRouter, Depends, HTTPException, status
from app.application.services.ai_service import CodeAnalysisService
from app.schemas.ai import AnalysisRequest, AnalysisResponse
from app.api.dependencies.auth import get_current_user
from app.domain.entities.user import User

from app.api.dependencies.rate_limit import rate_limit

router = APIRouter(prefix="/ai", tags=["AI Analysis"])

@router.post("/analyze", response_model=AnalysisResponse, dependencies=[Depends(rate_limit(limit=5, window=60))])
async def analyze_code(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze code for sensitive data and complexity.
    Suggests an obfuscation strategy and provides risk analysis.
    """
    ai_service = CodeAnalysisService()
    try:
        return await ai_service.analyze_code(request.code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
