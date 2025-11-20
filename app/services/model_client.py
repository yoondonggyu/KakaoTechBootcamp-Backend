"""
Model API 호출을 위한 클라이언트 서비스.
Model API 서버 포트가 변경되더라도 자동으로 감지하여 연결합니다.
"""
from __future__ import annotations

import os
import socket
from typing import Any, Dict, Optional

import httpx

_CANDIDATE_PORTS = [8002, 8001, 8003, 8082, 8502, 8000]
_MODEL_API_BASE_URL: Optional[str] = None


def _probe_port(port: int) -> bool:
    """포트에서 HTTP 응답이 오는지 확인"""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.3):
            pass
    except OSError:
        return False

    try:
        resp = httpx.get(f"http://127.0.0.1:{port}/", timeout=0.5)
        return resp.status_code < 500
    except Exception:
        return False


def _detect_model_api_port() -> int:
    for port in _CANDIDATE_PORTS:
        if _probe_port(port):
            print(f"✅ Model API 서버 포트 자동 감지: {port}")
            return port

    default_port = 8002
    print(f"⚠️ Model API 서버를 찾지 못했습니다. 기본 포트 {default_port} 사용")
    return default_port


def _build_model_api_base_url(force_refresh: bool = False) -> str:
    global _MODEL_API_BASE_URL

    if not force_refresh and _MODEL_API_BASE_URL:
        return _MODEL_API_BASE_URL

    env_url = os.getenv("MODEL_API_URL")
    if env_url:
        _MODEL_API_BASE_URL = env_url.rstrip("/")
        print(f"ℹ️ MODEL_API_URL 환경 변수를 사용합니다: {_MODEL_API_BASE_URL}")
        return _MODEL_API_BASE_URL

    env_port = os.getenv("MODEL_API_PORT")
    if env_port:
        _MODEL_API_BASE_URL = f"http://localhost:{env_port}/api"
        print(f"ℹ️ MODEL_API_PORT 환경 변수를 사용합니다: {_MODEL_API_BASE_URL}")
        return _MODEL_API_BASE_URL

    port = _detect_model_api_port()
    _MODEL_API_BASE_URL = f"http://localhost:{port}/api"
    return _MODEL_API_BASE_URL


def refresh_model_api_base_url() -> str:
    """외부에서 강제로 재탐색할 때 호출"""
    return _build_model_api_base_url(force_refresh=True)


def get_model_api_base_url() -> str:
    return _build_model_api_base_url()


async def predict_image(file_data: bytes, filename: str = "image.jpg") -> Optional[Dict[str, Any]]:
    """
    이미지 분류 API 호출
    """
    base_url = get_model_api_base_url()
    url = f"{base_url}/predict"
    print(f"🔍 Model API 호출 시도: {url}")

    async def _do_request(target_url: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            content_type = "image/jpeg"
            if filename.lower().endswith(".png"):
                content_type = "image/png"

            files = {"file": (filename, file_data, content_type)}
            print(f"📤 요청 전송 중... (파일 크기: {len(file_data)} bytes, URL: {target_url})")
            response = await client.post(target_url, files=files)
            print(f"📥 응답 받음: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            print(f"✅ Model API 응답 성공: {result}")
            return result

    attempts = 0
    last_error: Optional[Exception] = None

    while attempts < 2:
        try:
            return await _do_request(url)
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            last_error = e
            print(f"⚠️ Model API 연결 실패: {e}. 재탐색 중...")
            refreshed = refresh_model_api_base_url()
            url = f"{refreshed}/predict"
        except httpx.HTTPStatusError as e:
            print(f"⚠️ 이미지 분류 API HTTP 에러: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            last_error = e
            print(f"⚠️ 이미지 분류 API 호출 실패: {type(e).__name__}: {e}")
            return None
        finally:
            attempts += 1

    print(f"❌ Model API 호출 최종 실패: {last_error}")
    return None


async def analyze_sentiment(text: str, explain: bool = False) -> Optional[Dict[str, Any]]:
    """
    감성 분석 API 호출
    """
    base_url = get_model_api_base_url()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{base_url}/sentiment",
                json={"text": text, "explain": explain}
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        print("⚠️ 감성 분석 API 호출 타임아웃 (10초 초과)")
        return None
    except httpx.HTTPStatusError as e:
        print(f"⚠️ 감성 분석 API HTTP 에러: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"⚠️ 감성 분석 API 호출 실패: {e}")
        return None


async def chat_with_model(message: str, model: str = "gemma3:4b") -> Optional[str]:
    """
    채팅 API 호출 (스트리밍 응답 처리)
    """
    base_url = get_model_api_base_url()
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/chat",
                json={"message": message, "model": model},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            content = ""
            async for line in response.aiter_lines():
                if line:
                    import json

                    try:
                        data = json.loads(line)
                        if data.get("type") == "content":
                            content += data.get("content", "")
                    except json.JSONDecodeError:
                        pass
            return content if content else None
    except httpx.TimeoutException:
        print("⚠️ 채팅 API 호출 타임아웃 (60초 초과)")
        return None
    except httpx.HTTPStatusError as e:
        print(f"⚠️ 채팅 API HTTP 에러: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"⚠️ 채팅 API 호출 실패: {e}")
        return None

