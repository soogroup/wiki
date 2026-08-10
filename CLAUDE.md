# Wiki-Harness SSOT 워크플로우

회의록 기반 Single Source of Truth 하네스의 운영 가이드입니다.

---

## 목차
1. Ingest (회의록 → Wiki)
2. Query (검색 및 합성)
3. Lint (무결성 검사)

---

## 1. Ingest 워크플로우 (회의록 → Wiki)

### 목표
새 회의록을 raw-sources에 저장한 후, 각 항목을 wiki/decisions, pending, action_items, rejected로 분류하기.

### 프로세스

#### Step 1: Raw Source 적재
```
raw-sources/회의록/YYYY-MM-DD-주제.md
```
- **변경 불가** (감사 추적)
- Frontmatter 필수:
  ```yaml
  ---
  회의일: YYYY-MM-DD
  주제: 회의 이름
  참석자:
    - 이름 (직책)
  출처: Notion | 직접작성 | ...
  적재일: YYYY-MM-DD
  ---
  ```

#### Step 2: 수동 큐레이션 (회의 후 같은 날 또는 다음 날)

회의록의 각 안건(agenda item)을 읽고, 다음 분류 기준에 따라 wiki 파일 생성:

**A. Decision (결정사항)**
- **기준**: "우리는 이렇게 하기로 결정했다" 명확한 선택
- **파일명**: `wiki/decisions/[영역]-YYYY-MM-DD-[설명].md`
- **Frontmatter**:
  ```yaml
  ---
  타입: decision
  출처: raw-sources/회의록/YYYY-MM-DD-주제.md
  결정일: YYYY-MM-DD
  상태: active | resolved | obsolete
  태그: [영역1, 영역2]
  owner: 담당자
  ---
  ```
- **예**:
  ```yaml
  # PG사 A사 선정
  ---
  타입: decision
  출처: raw-sources/회의록/2026-05-14-제품주간회의.md
  결정일: 2026-05-14
  상태: active
  태그: [결제, PG연동]
  owner: 이지혜
  ---
  
  ## 결정 내용
  수수료 기준으로 A사 선정 (2.2% vs B사 2.8%, C사 2.5%)
  ```

**B. Decision Revision (결정 번복)**
- **기준**: 이전 결정을 변경하는 새로운 결정
- **파일명**: `wiki/decisions/[영역]-YYYY-MM-DD-[설명]-변경.md` (또는 `_v2.md`, `_v3.md`)
- **이전 파일 상태 업데이트**: `상태: obsolete` 표시
- **예**:
  ```yaml
  # 결제 연동 일정 변경 (5월 말 → 6월 중순)
  ---
  타입: decision
  출처: raw-sources/회의록/2026-05-14-제품주간회의.md
  결정일: 2026-05-14
  상태: active
  이전_결정: 결제-2026-04-16-pg사-선정-프로세스.md
  변경_사유: A사 스펙 문서 미수신으로 인한 일정 재조정
  ---
  ```

**C. Pending (보류 항목)**
- **기준**: "다음 회의에서 다시 다루자", "논의 보류", "아직 결정 미정"
- **파일명**: `wiki/pending/[영역]-YYYY-MM-DD-[설명].md`
- **Frontmatter**:
  ```yaml
  ---
  타입: pending
  출처: raw-sources/회의록/YYYY-MM-DD-주제.md
  보류일: YYYY-MM-DD
  상태: active | stale
  논의일자: [YYYY-MM-DD, YYYY-MM-DD, ...]
  재논의_횟수: 숫자 (0, 1, 2, ...)
  다음_논의: 예정 회의 날짜 또는 "TBD"
  태그: [영역1]
  owner: 담당자
  ---
  ```
- **Stale 규칙**: 재논의_횟수 >= 2이면 자동 `상태: stale` 마킹
- **예**:
  ```yaml
  # 정산 주기 재논의
  ---
  타입: pending
  출처: raw-sources/회의록/2026-06-11-제품주간회의.md
  보류일: 2026-04-16
  상태: stale  # 2회 재논의됨
  논의일자: [2026-06-11, 2026-07-09]
  재논의_횟수: 2
  다음_논의: TBD
  태그: [정산]
  ---
  
  ## 이슈
  4월에 "월 1회"로 결정했지만, 고객사 A에서 "주 1회" 요청 → 재논의 필요
  ```

**D. Action Item (액션 아이템)**
- **기준**: "누가, 언제까지, 무엇을 할 것인가" 명확한 액션
- **파일명**: `wiki/action_items/action-YYYY-MM-DD-[담당자]-[설명].md`
- **Frontmatter**:
  ```yaml
  ---
  타입: action_item
  출처: raw-sources/회의록/YYYY-MM-DD-주제.md
  등록일: YYYY-MM-DD
  담당자: 이름
  마감: YYYY-MM-DD
  상태: pending | in_progress | completed | blocked
  블로킹_원인: (optional) 블로킹 이유
  ---
  ```
- **예**:
  ```yaml
  # A사 연동 스펙 문서 확보
  ---
  타입: action_item
  출처: raw-sources/회의록/2026-05-14-제품주간회의.md
  등록일: 2026-05-14
  담당자: 박준서
  마감: 2026-05-21
  상태: blocked
  블로킹_원인: A사 담당자 응답 지연 (3일째 회신 없음)
  ---
  ```

**E. Rejected (기각/대체된 항목)**
- **기준**: 검토했지만 채택되지 않은 안
- **파일명**: `wiki/rejected/rejected-YYYY-MM-DD-[설명].md`
- **Frontmatter**:
  ```yaml
  ---
  타입: rejected
  출처: raw-sources/회의록/YYYY-MM-DD-주제.md
  결정일: YYYY-MM-DD
  상태: rejected
  대체안: 대신 채택된 항목 (있으면)
  ---
  ```
- **예**:
  ```yaml
  # Q2 중 온보딩 개선 (대신 Q3로 연기)
  ---
  타입: rejected
  출처: raw-sources/회의록/2026-04-16-제품주간회의.md
  결정일: 2026-04-16
  상태: rejected
  대체안: 온보딩은 Q3에 반영하기로 결정 (현재는 결제 연동 우선)
  ---
  ```

#### Step 3: 유지보수 기록

wiki/log.md에 다음 형식으로 기록:

```
## 2026-08-10
### Ingest: 2026-05-14-제품주간회의.md
- decision: 2개 (pg사-최종-선정, 결제-연동-일정-변경)
- pending: 1개 (온보딩-이탈-문제)
- action_items: 2개 (박준서, 최민아)
- total: 5개 항목 추가
- notes: decision revision 패턴 처음 적용 (obsolete 표시)
```

#### Step 4: Index 업데이트

wiki/index.md를 카테고리/상태별로 업데이트:

```markdown
# Wiki Index

## Active Decisions (14)
- 결제
  - [결제-2026-04-16-pg사-선정-프로세스.md](decisions/결제-2026-04-16-pg사-선정-프로세스.md) (obsolete)
  - [결제-2026-05-14-pg사-최종-선정.md](decisions/결제-2026-05-14-pg사-최종-선정.md) (active)
  - ...
  
## Stale Pending (2)
- [정산-주기-재논의](pending/정산-주기-재논의.md) (재논의 2회)
- ...
```

---

## 2. Query 워크플로우 (검색 및 합성)

### 목표
특정 주제나 상태의 항목들을 찾아서 답변을 합성하기.

### 사용 사례

#### Q: "결제 영역에서 현재 진행 중인 것들은?"
```bash
# 파일명 prefix로 검색
ls wiki/decisions/결제-* wiki/action_items/action-*-*결제*.md
grep -r "상태: active" wiki/decisions/결제-*
grep -r "상태: in_progress\|blocked" wiki/action_items/
```

#### Q: "정산과 관련해서 왜 자꾸 재논의되나?"
```bash
# pending 파일 읽음
cat wiki/pending/정산-주기-재논의.md
# → 논의일자, 재논의_횟수, 다음_논의 확인
```

#### Q: "박준서 담당 액션의 현황은?"
```bash
grep -r "담당자: 박준서" wiki/action_items/
# 각 파일의 상태 필드 확인 (pending, in_progress, completed, blocked)
```

### 합성 (Synthesis)
- 각 파일의 frontmatter + 본문을 읽어서
- 질문에 맞는 항목들을 모아서
- 인용(cite)과 함께 답변 작성
- 필요시 wiki/log.md에 "Query: ..." 기록

---

## 3. Lint 워크플로우 (무결성 검사)

### 목표
wiki의 데이터 품질 유지. 정기적으로 실행 (매 ingest 후 또는 주 1회).

### 검사 규칙

#### Rule 1: Orphan Items (고아 항목)
```
발견: 이전 회의에서 언급된 항목이 현재 회의에서 미언급
조건: 
  - decision/pending/action_item이 N회 이상 조용히 사라짐
  - 상태가 "active"인데 log.md에 업데이트 기록 없음
액션: 
  - 해당 파일의 상태를 "resolved" 또는 "obsolete"로 표시
  - log.md에 "orphan 정리" 기록
```

#### Rule 2: Stale Pending
```
발견: pending 항목이 2회 이상 "재논의"로 보류됨
조건: pending 파일의 재논의_횟수 >= 2
액션:
  - 자동으로 상태를 "stale"로 마킹
  - owner에게 "결정 필요" 알림 (수동)
  - "다음_논의" 필드를 명시적으로 설정
```

#### Rule 3: Action without Owner (담당자 없는 액션)
```
발견: action_item 파일의 담당자 필드 비어있음
조건: 담당자 == "" 또는 "미정"
액션:
  - 파일을 pending으로 변경 + "담당자 결정"이라는 항목으로 재분류
  - log.md에 "담당자 미정 → pending으로 재분류" 기록
```

#### Rule 4: Decision without Citation (인용 없는 결정)
```
발견: decision 파일의 출처(source) 필드가 없음
조건: 출처 == ""
액션:
  - log.md에 "출처 누락: [파일명]" 기록 → 수동 확인 필요
```

#### Rule 5: Broken References (깨진 참조)
```
발견: decision/pending/action이 참조하는 파일이 없음
조건: 예: "대체안: xxx.md" 인데 xxx.md가 없음
액션:
  - log.md에 "참조 오류: [파일명] → [참조 대상]" 기록
```

#### Rule 6: Inconsistent Status Dates
```
발견: 파일의 상태 변경이 시간순 일관성이 없음
조건: 예: 결정일이 이전 회의 날짜보다 앞인 revision
액션:
  - log.md에 "날짜 순서 오류: [파일명]" 기록
```

### Lint 실행 명령 (의사 코드)

```bash
# 모든 검사 실행
./lint.sh

# 각 규칙별 실행
./lint.sh --rule=orphan
./lint.sh --rule=stale-pending
./lint.sh --rule=no-owner
./lint.sh --rule=no-citation
./lint.sh --rule=broken-refs
./lint.sh --rule=date-order
```

### Lint 결과 기록

lint 실행 후 wiki/log.md에 기록:

```
## 2026-08-10
### Lint Run
- Orphan items: 0
- Stale pending: 1 (정산-주기-재논의.md)
- Actions without owner: 0
- Broken references: 0
- Status: ✓ Pass
```

---

## 참고

- **Karpathy LLM Wiki**: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- **핵심 원칙**: "wiki is a persistent, compounding artifact" → 매번 재생성하지 말고, 지속적 유지보수
- **Frontmatter 스키마**: `handover/01-ssot-design-handover.md` 참고
