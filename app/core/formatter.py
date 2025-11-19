"""응답 포맷팅 유틸리티"""
from fastapi.responses import JSONResponse


def create_json_response(status_code: int, message: str, data=None) -> JSONResponse:
    """
    일관된 JSON 응답 형식 생성
    
    Args:
        status_code: HTTP 상태 코드
        message: 응답 메시지
        data: 응답 데이터 (선택)
    
    Returns:
        JSONResponse: 표준화된 JSON 응답
    """
    return JSONResponse(
        status_code=status_code,
        content={"message": message, "data": data}
    )



