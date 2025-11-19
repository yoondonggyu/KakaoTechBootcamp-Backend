#!/bin/bash

echo "🚀 Git 저장소 초기화 및 단계별 커밋 설정"
echo ""

# Git 초기화
git init
echo "✅ Git 저장소 초기화 완료"

# .gitignore 추가
git add .gitignore
git commit -m "chore: 초기 설정 및 .gitignore 추가"
echo "✅ .gitignore 커밋 완료"

# 2-1 단계: Route만 사용
echo ""
echo "📝 2-1 단계 커밋 중..."
git add main_routes_only.py
git commit -m "feat(2-1): Route만 이용한 백엔드 구현

- Route만 사용하여 모든 로직 구현
- 메모리 기반 데이터 저장소 사용
- 모든 API 엔드포인트 구현 완료
- 예외 처리 및 검증 로직 포함"
echo "✅ 2-1 단계 커밋 완료"

# 2-2 단계: Route/Controller 구분
echo ""
echo "📝 2-2 단계 커밋 중..."
git add app/
git commit -m "feat(2-2): Route/Controller 구분 구조 구현

- Route 레이어와 Controller 레이어 분리
- 비즈니스 로직을 Controller로 이동
- Route는 요청/응답만 처리하도록 리팩토링
- 3계층 구조 (Route-Controller-Model) 적용"
echo "✅ 2-2 단계 커밋 완료"

# 2-3 단계: 커뮤니티 백엔드 완성
echo ""
echo "📝 2-3 단계 커밋 중..."
git add API_SPECIFICATION.md COMMIT_GUIDE.md
git commit -m "feat(2-3): 커뮤니티 백엔드 완성 및 개선사항 추가

- API 명세서 작성
- RequestValidationError 처리 추가
- 응답 포맷팅 유틸리티 추가
- 예외 처리 및 검증 로직 보완
- 루트 경로 엔드포인트 추가"
echo "✅ 2-3 단계 커밋 완료"

echo ""
echo "🎉 모든 단계별 커밋 완료!"
echo ""
echo "커밋 내역 확인:"
git log --oneline --graph
