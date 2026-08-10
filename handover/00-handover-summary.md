# Wiki-Harness SSOT 최종 핸드오버

**작성**: 2026-08-10  
**상태**: 운영 시작 준비 완료  
**담당**: PM (이지혜), 팀

---

## 🎯 핵심 요약

### 프로젝트 목표
Karpathy의 LLM Wiki 원리를 기반으로, 팀 회의록의 SSOT(Single Source of Truth) 하네스 구축.

### 완성된 것
- ✅ 설계 완료 (5가지 미해결 Q 중 3가지 해결, 2가지는 PM 선택 대기)
- ✅ 규칙 정의 완료 (DO 5가지, DON'T 7가지)
- ✅ 워크플로우 정의 완료 (Ingest, Query, Lint)
- ✅ 첫 ingest 처리 완료 (2026-05-14 회의록)
- ✅ 자동 검출 규칙 정의 (Error 5가지, Warning 4가지)

### 대기 중인 것
- ⏳ Q#4a (Domain 분류): Option A(prefix) vs Option B(태그) — PM 선택 필요
- ⏳ Q#5 (자동화): LLM 자동 vs PM 수동 — PM 선택 필요

---

## 📋 운영 규칙 (핵심)

### DO (해야 할 규칙) — 5가지

| # | 규칙 | 목적 | 연관 문서 |
|---|------|------|---------|
| DO#1 | 모든 항목을 4가지 카테고리로 분류 | 추적 가능성 | 05, CLAUDE.md |
| DO#2 | 담당자 미정 → pending으로 올리기 | 담당자 명확화 | 05, CLAUDE.md |
| DO#3 | 결정 변경 시 새 파일 + obsolete | 이력 보존 | 05, CLAUDE.md |
| DO#4 | Pending에 재논의_횟수 + 날짜 명시 | stale pending 감지 | 05, CLAUDE.md |
| DO#5 | Cross-reference 명시적 설정 | 파일 간 관계 추적 | 05, CLAUDE.md |

### DON'T (하지 말아야 할 규칙) — 7가지

| # | 규칙 | 이유 |
|---|------|------|
| DON'T#1 | 담당자 없는 action item | 책임 불명확 |
| DON'T#2 | "기타" 섹션에 방치 | wiki 분류 안 됨 |
| DON'T#3 | 파일 덮어쓰기 (결정 변경) | 이력 소실 |
| DON'T#4 | "다음 회의 재논의"만 기록 | 무한 보류 |
| DON'T#5 | 암묵적 참고 (링크 없음) | 관계 추적 불가 |
| DON'T#6 | 타입 필드 미표시 | 자동화 불가 |
| DON'T#7 | 출처 미명시 | 추적 불가 |

---

## 🗂️ 파일 구조 및 필드

### Decision (결정사항)

```
파일명: wiki/decisions/[영역]-YYYY-MM-DD-[설명].md

Frontmatter (필수):
- 타입: decision
- 출처: raw-sources/회의록/YYYY-MM-DD-주제.md
- 결정일: YYYY-MM-DD
- 상태: active | resolved | obsolete
- 태그: [영역1]
- owner: 담당자

Revision인 경우 추가:
- 이전_결정: 파일명.md
- 변경_사유: 구체적 이유
```

### Pending (보류 항목)

```
파일명: wiki/pending/[영역]-YYYY-MM-DD-[설명].md

Frontmatter (필수):
- 타입: pending
- 출처: raw-sources/회의록/YYYY-MM-DD-주제.md
- 보류일: YYYY-MM-DD
- 상태: active | stale
- 논의일자: [YYYY-MM-DD, ...]
- 재논의_횟수: 숫자 (← 중요!)
- 다음_논의: YYYY-MM-DD or "TBD" (← 구체적으로!)
- 태그: [영역1]
- owner: 담당자
```

**자동 규칙**:
- `재논의_횟수 >= 2` → `상태: stale` (자동 마킹)

### Action Item (액션)

```
파일명: wiki/action_items/action-YYYY-MM-DD-[담당자]-[설명].md

Frontmatter (필수):
- 타입: action_item
- 출처: raw-sources/회의록/YYYY-MM-DD-주제.md
- 등록일: YYYY-MM-DD
- 담당자: 이름 (필수! 없으면 pending으로)
- 마감: YYYY-MM-DD
- 상태: pending | in_progress | completed | blocked

선택사항:
- 블로킹_원인: (상태가 blocked인 경우)
- 의존_결정: (결정에 의존하는 경우)
```

### Rejected (기각 항목)

```
파일명: wiki/rejected/rejected-YYYY-MM-DD-[설명].md

Frontmatter (필수):
- 타입: rejected
- 출처: raw-sources/회의록/YYYY-MM-DD-주제.md
- 결정일: YYYY-MM-DD
- 상태: rejected
- 대체안: 대신 선택된 항목
```

---

## 🔍 Lint 규칙 (자동 검출)

### Error 규칙 (즉시 수정) — 5가지

```bash
Error#1: 담당자 없는 action item
  검출: grep -r "담당자.*:\s*$" wiki/action_items/
  조치: pending으로 이동 + "담당자 결정" 항목 추가

Error#2: 타입 필드 미표시
  검출: grep -rL "^타입:" wiki/
  조치: 모든 파일에 "타입:" 필드 추가

Error#3: 출처 필드 미명시
  검출: grep -rL "^출처:" wiki/
  조치: "출처: raw-sources/..." 추가

Error#4: 상태 필드 미표시
  검출: grep -rL "^상태:" wiki/
  조치: 적절한 상태 설정

Error#5: 중복 active decision
  검출: 같은 주제(prefix)의 파일이 2개 이상 active
  조치: 이전 버전을 "obsolete"로 표시
```

### Warning 규칙 (검토 필요) — 4가지

```
Warning#1: Stale pending (2회 이상 재논의)
  확인: 상태가 "stale"인가? 다음_논의 날짜가 명시되었나?

Warning#2: Pending with "TBD" (30일 이상 보류)
  확인: 다음_논의를 구체적 날짜로 변경했나?

Warning#3: Orphan items
  확인: 이전에 나왔는데 최근에 언급 안 된 항목?
  조치: 상태를 "resolved" 또는 "obsolete"로 변경

Warning#4: Broken references
  확인: [[파일.md]] 링크가 존재하는가?
  조치: 파일명 수정 또는 링크 제거
```

---

## 📊 영역(Domain) 분류

### 확정된 영역 (현재 운영)

| 영역 | 첫 등장 | 상태 | 파일명 prefix |
|------|--------|------|--------------|
| 결제 | 04-16 | 진행 중 | `결제-*` |
| 온보딩 | 04-16 | 완료 | `온보딩-*` |
| 정산 | 04-16 | 보류 | `정산-*` |
| 채용 | 07-23 | 신규 | `채용-*` |

**현재 방식**: Option A (파일명 prefix)  
**대안**: Option B (자유 태그) — **Q#4a에서 PM 선택 필요**

---

## 🚀 Ingest 체크리스트

### 회의 후 PM이 할 일 (1-2시간)

```
Step 1: Raw Source 적재
[ ] 회의록을 raw-sources/회의록/YYYY-MM-DD-주제.md로 저장
[ ] Frontmatter 필드 5가지 확인 (회의일, 주제, 참석자, 출처, 적재일)

Step 2: 수동 큐레이션
[ ] 모든 회의 안건을 4가지 카테고리 중 하나로 분류
  [ ] Decision: 명확한 선택이 있는가?
  [ ] Pending: 다음에 다시 다룰 것인가?
  [ ] Action: "누가, 언제까지, 무엇"이 명확한가?
  [ ] Rejected: 검토했지만 선택 안 한 것인가?
[ ] "기타" 섹션에 남은 항목 없는가?

Step 3: 각 항목별 파일 생성
Decision:
  [ ] 파일명: [영역]-YYYY-MM-DD-[설명].md
  [ ] Frontmatter 필수 필드 5가지
  [ ] Decision revision인가? → 새 파일 생성 + obsolete 표시
  [ ] Cross-reference (이전_결정, 관련_action 등)

Pending:
  [ ] 다음_논의가 구체적 날짜인가? (또는 "TBD")
  [ ] 재논의_횟수가 기록되었나?
  [ ] 2회 이상이면 상태: stale?

Action:
  [ ] 담당자가 명시되었나? (없으면 pending으로 올리기)
  [ ] 마감일이 설정되었나?
  [ ] 의존_결정이 있으면 명시되었나?

Rejected:
  [ ] 대체안이 명시되었나?

Step 4: Cross-reference 검증
[ ] 파일 간 참조 관계가 명시적으로 표현되었나?
[ ] [[파일명.md]] 링크가 유효한가?

Step 5: Lint 검사
[ ] Error 규칙 5가지 확인 (타입, 출처, 상태, 담당자, 중복)
[ ] Warning 규칙 4가지 검토 (stale, orphan, broken, TBD)

Step 6: 기록
[ ] wiki/log.md에 ingest 기록
  - 처리 항목 개수
  - Decision revision 개수
  - 특이사항
```

---

## 🔄 Query 워크플로우

### 자주 묻는 질문들

```
Q: "결제 영역에서 현재 진행 중인 것들은?"
→ ls wiki/decisions/결제-* && grep "상태: active" wiki/decisions/결제-*

Q: "박준서 담당 액션의 현황은?"
→ ls wiki/action_items/action-*박준서* && cat 각 파일의 상태

Q: "정산이 왜 계속 재논의되나?"
→ cat wiki/pending/정산-*.md && grep "재논의_횟수\|다음_논의"
```

---

## 📚 참고 문서

| 문서 | 내용 | 대상 |
|------|------|------|
| **01-ssot-design-handover.md** | 설계 완정, 5가지 Q 해결 상태 | PM, 팀 |
| **03-decisions-pending.md** | Q#4a, Q#5 상세 비교 (PM 선택 필요) | PM |
| **04-issues-and-improvements.md** | 문제점 7가지, 개선 로드맵 | 팀 |
| **05-rules-do-and-dont.md** | DO 5가지, DON'T 7가지 상세 규칙 | 팀 |
| **CLAUDE.md** | Ingest/Query/Lint 워크플로우 (규칙 통합) | 팀 |
| **wiki/log.md** | ingest 기록 (지속 업데이트) | 팀 |

---

## ⚠️ 주의사항

### DO#3: Decision Revision은 필수
```
❌ 나쁜 예: 기존 파일을 직접 수정
✅ 좋은 예: 새 파일 생성 + 이전_결정 + obsolete 표시

→ 이력이 남아야 "왜 변경되었는가" 추적 가능
```

### DO#4: Pending의 "TBD" 위험
```
❌ 나쁜 예: 
  다음_논의: "다음 회의에서"
  재논의_횟수: 필드 없음

✅ 좋은 예:
  다음_논의: "2026-08-06" or "TBD"
  재논의_횟수: 2 (자동 stale 마킹)
```

### 담당자 미정 금지
```
❌ 나쁜 예:
# action-2026-05-14-담당자미정-뭔가.md
담당자: TBD

✅ 좋은 예:
# pending-2026-05-14-담당자-결정.md
주제: 뭔가 — 담당자 지정 필요
다음_논의: 2026-05-21
```

---

## 🎬 다음 단계

### 즉시 (1주)
- [ ] **PM**: Q#4a, Q#5 선택
- [ ] **팀**: CLAUDE.md 숙지
- [ ] **팀**: 체크리스트 확인

### 단기 (1개월)
- [ ] 2026-06-11 회의록 ingest (규칙 기반)
- [ ] 나머지 회의록 (06-25, 07-09, 07-23) ingest
- [ ] Lint Error/Warning 자동 검출 스크립트 구현

### 중기 (3개월)
- [ ] Decision revision 문제 재검토 (단일 파일 + 버전 히스토리 검토)
- [ ] Action-Decision coupling 개선
- [ ] Index 자동 생성

### 장기 (6개월+)
- [ ] LLM 기반 Query 자동화
- [ ] 외부 도구 (Linear, Notion) 양방향 동기화

---

## 💼 역할별 책임

### PM (이지혜)
- 회의 후 ingest 처리 (1-2시간/회의)
- Q#4a, Q#5 선택 결정
- wiki/log.md 기록

### 팀 (개발, 디자인, 사업개발)
- 회의 중 명확한 의사결정 (decision vs pending)
- 담당자 명확히 하기 (action item)
- ingest 검수 (error/warning 체크)

### 시스템
- Lint 자동 검출 (Error 5가지, Warning 4가지)
- wiki/index.md 자동 생성 (향후)

---

## 📞 문의 & 피드백

이 규칙들은 **2026-08-10에 도출**되었으며, 실제 운영 경험에 따라 개선됩니다.

**문제가 있으면**:
1. handover/04-issues-and-improvements.md 참고
2. CLAUDE.md의 해당 섹션 재검토
3. 새로운 규칙이 필요하면 05-rules-do-and-dont.md 업데이트

---

## 최종 체크리스트

프로젝트 시작 전 확인:

```
설계:
[ ] 5가지 Q 중 Q#1, Q#2, Q#3 이해했나?
[ ] Q#4a, Q#5를 PM이 선택했나?

규칙:
[ ] DO 5가지를 이해했나?
[ ] DON'T 7가지를 이해했나?
[ ] Lint Error/Warning 5+4가지를 이해했나?

파일 구조:
[ ] 4가지 카테고리 (decision/pending/action/rejected) 확인?
[ ] 각 카테고리의 필드를 확인했나?

워크플로우:
[ ] CLAUDE.md를 읽었나?
[ ] ingest 체크리스트를 확인했나?

준비:
[ ] github.com/soogroup/wiki를 clone했나?
[ ] 첫 회의록 ingest 예정 회의 정했나?
```

---

**최종 상태**: ✅ 운영 시작 준비 완료

모든 규칙, 워크플로우, 문서가 완성되었습니다.  
**2026-06-11 회의록부터 이 규칙들을 적용하여 운영하면 됩니다.**

---

*핸드오버 작성*: 2026-08-10  
*담당자*: 이지혜 (PM)  
*팀*: 박준서, 최민아, 강태우
