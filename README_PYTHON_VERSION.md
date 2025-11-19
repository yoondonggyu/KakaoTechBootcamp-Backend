# Python 버전 관리 가이드

## 현재 설정

- **Python 버전**: 3.13.5
- **패키지 관리**: pip + conda
- **가상환경**: 프로젝트별 독립 환경 권장

## 권장 설정 (프로덕션)

### 옵션 1: Python 3.11 (안정성 우선) ⭐ 추천

```bash
# Backend용 환경
conda create -n fastapi_backend python=3.11 -y
conda activate fastapi_backend
cd FASTAPI_Project_back
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Model용 환경
conda create -n fastapi_model python=3.11 -y
conda activate fastapi_model
cd FASTAPI_Project_model
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

**장점**:
- 대부분의 라이브러리 완벽 지원
- Docker 이미지 풍부 (python:3.11-slim)
- 배포 환경 안정적
- TensorFlow/Keras 완전 지원

### 옵션 2: Python 3.13 (최신 기능 활용)

```bash
# 현재 설정 그대로 유지
# .python-version 파일로 버전 명시
```

**주의사항**:
- 일부 라이브러리가 아직 미지원일 수 있음
- Docker 이미지 제한적
- 배포 시 호환성 테스트 필수

## Docker 배포 시

### Dockerfile 예시 (Python 3.11)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile 예시 (Python 3.13)

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 버전 확인 방법

```bash
# Python 버전 확인
python --version

# 설치된 패키지 확인
pip list

# 가상환경 목록
conda env list
```

## 문제 발생 시

### 패키지 호환성 문제
```bash
# 특정 버전으로 재설치
pip install 패키지명==버전

# 캐시 삭제 후 재설치
pip install --no-cache-dir -r requirements.txt
```

### 가상환경 재생성
```bash
conda deactivate
conda remove -n 환경명 --all
conda create -n 환경명 python=3.11 -y
conda activate 환경명
pip install -r requirements.txt
```

## 협업 시 권장사항

1. **Python 버전 통일**: 팀원 모두 같은 버전 사용 (3.11 권장)
2. **requirements.txt 항상 최신화**: `pip freeze > requirements.txt`
3. **가상환경 필수 사용**: base 환경 사용 금지
4. **`.python-version` 파일 커밋**: pyenv 등에서 자동 인식
5. **Docker 사용 권장**: 환경 차이 최소화

