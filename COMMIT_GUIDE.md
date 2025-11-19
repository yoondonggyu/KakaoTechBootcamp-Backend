# 단계별 커밋 가이드

## 과제 단계별 커밋 전략

### 방법 1: 단계별 브랜치 사용 (권장)

각 단계를 별도 브랜치로 관리하고, 최종적으로 main 브랜치에 병합합니다.

```bash
# 1. Git 초기화
git init
git add .gitignore
git commit -m "chore: 초기 설정 및 .gitignore 추가"

# 2-1 단계: Route만 사용하는 백엔드
git checkout -b step-2-1-route-only
git add main_routes_only.py
git commit -m "feat(2-1): Route만 이용한 백엔드 구현

- Route만 사용하여 모든 로직 구현
- 메모리 기반 데이터 저장소 사용
- 모든 API 엔드포인트 구현 완료"

# 2-2 단계: Route/Controller 구분
git checkout -b step-2-2-route-controller
git add app/
git commit -m "feat(2-2): Route/Controller 구분 구조 구현

- Route 레이어와 Controller 레이어 분리
- 비즈니스 로직을 Controller로 이동
- Route는 요청/응답만 처리하도록 리팩토링"

# 2-3 단계: 커뮤니티 백엔드 완성
git checkout -b step-2-3-community-backend
git add .
git commit -m "feat(2-3): 커뮤니티 백엔드 완성

- API 명세에 맞게 최종 구현
- 예외 처리 및 검증 로직 보완
- RequestValidationError 처리 추가
- 응답 포맷팅 유틸리티 추가"

# 최종 병합
git checkout -b main
git merge step-2-1-route-only
git merge step-2-2-route-controller
git merge step-2-3-community-backend
```

### 방법 2: 단계별 커밋 (단일 브랜치)

하나의 브랜치에서 단계별로 커밋합니다.

```bash
# 1. Git 초기화
git init
git add .gitignore
git commit -m "chore: 초기 설정"

# 2-1 단계
git add main_routes_only.py
git commit -m "feat(2-1): Route만 이용한 백엔드 구현"

# 2-2 단계
git add app/
git commit -m "feat(2-2): Route/Controller 구분 구조 구현"

# 2-3 단계
git add .
git commit -m "feat(2-3): 커뮤니티 백엔드 완성 및 개선사항 추가"
```

### 방법 3: 태그 사용

각 단계를 태그로 표시합니다.

```bash
# 기본 커밋 후
git tag -a v2.1-route-only -m "2-1 단계: Route만 사용"
git tag -a v2.2-route-controller -m "2-2 단계: Route/Controller 구분"
git tag -a v2.3-community-backend -m "2-3 단계: 커뮤니티 백엔드 완성"
```

## 추천 방법

**방법 1 (브랜치 사용)**을 권장합니다:
- 각 단계를 명확히 구분 가능
- 필요시 각 단계로 돌아가기 쉬움
- GitHub에서 브랜치별로 확인 가능



