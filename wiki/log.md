# Wiki Log — 작업 기록

모든 ingest, 상태 변경, 유지보수 작업의 이력을 기록합니다.

---

## 2026-08-10

### Ingest: 초기 회의록 적재

**작업**: 원본 회의록 6개 (2026-04-16 ~ 2026-07-23) 파싱 및 Wiki 항목 생성

**처리 결과**:
- Decisions: 14개 (결제 8, 온보딩 5, 정산 1)
- Pending: 6개
- Action Items: 13개
- Rejected: 5개
- **합계**: 38개 항목

**상태**:
- 모든 원본 frontmatter 정규화 완료
- Wiki 폴더 구조 생성
- 각 항목별 파일 생성 (frontmatter + 기본 내용)
- index.md, log.md 생성

**미해결 항목** (다음 처리 필요):
1. Pending 재논의 추적 — "정산 주기" 항목은 3회 이상 나타남 (4/16 논의 X, 6/11, 7/09 재논의)
2. Action Item 진행 상황 업데이트 — 마감 지난 항목들 상태 확인
3. Decision revision 이력 — "연동 완료 목표" 같은 변경 사항들을 하나의 파일로 통합할지 검토

---

## 다음 워크플로우

### Query (검색 및 답변 합성)
- 특정 주제(예: "결제") 또는 상태(예: "pending") 검색
- 관련 항목들을 인용하며 답변 작성
- 결과를 새로운 페이지로 기록

### Lint (무결성 체크)
- Orphan 항목 확인 (참조되지 않은 항목)
- Stale pending 확인 (N회 이상 재논의된 항목)
- Broken cross-reference 확인
- Duplicate 확인

---
