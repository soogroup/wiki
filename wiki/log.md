# Wiki Log — 작업 기록

모든 ingest, 상태 변경, 유지보수 작업의 이력을 기록합니다.

---

## 2026-08-10 (재처리)

### Ingest: 2026-06-11 제품주간회의 (ingest-meeting-minutes 스킬 테스트)

**회의 정보**:
- 회의일: 2026-06-11
- 주제: 제품주간회의
- 참석자: 이지혜(PM), 박준서(Dev Lead), 김민지(Design)

**처리 항목**:
- Decisions: 2개
  - `결제-2026-06-11-pg사-a사-최종-선정.md` (신규)
  - `결제-2026-06-11-결제-연동-완료-일정-변경.md` (**Decision Revision** - 5월 말 → 6월 중순)
- Action Items: 1개
  - `action-2026-06-11-박준서-a사-스펙-문서-확보.md` (담당자: 박준서, 마감: 2026-06-18)
- Pending: 1개
  - `온보딩-2026-06-11-온보딩-개선-q3-연기.md` (Q3로 연기, 다음_논의: 2026-08-01)
- **합계**: 4개 항목

**특이사항**:
- Decision Revision 패턴 적용 (결제 연동 일정 변경)
- 모든 파일이 DO 5가지 규칙 준수
- DON'T 7가지 항목 없음
- Cross-reference 명시적 설정 완료
- Checklist 8/8 통과

**스킬 검증**:
- ✅ 7-step workflow 모두 완료
- ✅ 4가지 카테고리 분류 완료
- ✅ Frontmatter 필드 모두 명시
- ✅ 출처, 타입, 상태 필드 완비
- ✅ Action item 담당자 명시
- ✅ Pending 다음_논의 구체적 날짜
- ✅ Cross-references [[파일명.md]] 형식

**상태**: ✓ 완료 (ingest-meeting-minutes 스킬 검증됨)

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

## 2026-05-14 Ingest (CLAUDE.md 및 설계 확정 후 처리)

### 작업
2026-05-14 회의록을 CLAUDE.md에 정의된 새로운 워크플로우로 처리

**처리 항목**:
- Decision: 2개
  - `결제-2026-05-14-pg사-최종-선정.md` (신규 선택)
  - `결제-2026-05-14-결제-연동-일정-변경.md` (**Decision Revision** 패턴 첫 적용)
- Pending: 1개
  - `pending-2026-05-14-온보딩-이탈-문제.md` (신규 안건)
- Action Items: 2개
  - `action-2026-05-14-박준서-a사-연동-스펙-문서-확보.md` (blocked)
  - `action-2026-05-14-최민아-온보딩-구간별-이탈률-분석.md` (pending)
- **합계**: 5개 항목 추가

### 핵심 패턴 발견 & 적용

1. **Decision Revision (Q#1 선택 적용)**
   - 이전 파일: `결제-2026-04-16-pg사-선정-프로세스.md` → **obsolete 표시 필요** (별도 task)
   - 새 파일: `결제-2026-05-14-결제-연동-일정-변경.md`
   - 이유: A사 스펙 문서 미수신으로 일정 변경 (5월 말 → 6월 중순)

2. **Cross-Reference 추가**
   - decision과 action_items이 명시적으로 링크됨
   - pending과 action_items의 의존성 표현

3. **Action Item 상태 필드 적용 (Q#3 선택)**
   - `블로킹_원인` 필드로 상태의 원인 명시
   - `상태: blocked` vs `상태: pending` 구분

### 상태

✓ 완료: Wiki 파일 5개 생성
- [ ] TODO: 4월 파일들의 obsolete 표시 및 이전 관계 명시
- [ ] TODO: index.md 업데이트 (2026-05-14 항목 추가)

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
