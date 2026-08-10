# 회의록 SSOT 하네스 — 설계 v1

## 배경

Karpathy의 LLM wiki 구조(https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)를 참고해, 팀이 관리하는 회의록 SSOT 하네스를 설계하고 있습니다.

### Karpathy LLM Wiki 핵심 원리

- **3층 구조**:
  1. Raw sources (원본 회의록 — 변경 불가)
  2. Wiki (구조화된 마크다운 — 변경 가능, cross-reference 포함)
  3. Schema (설정/메타데이터, 워크플로우 정의)

- **핵심 파일**:
  - `index.md` — 모든 항목을 카테고리/상태별로 나열 (한 줄 요약)
  - `log.md` — 시간순 기록 (ingest, 상태 변경, maintenance)

- **기본 워크플로우**:
  - **Ingest**: 새 회의록 추가 → 각 항목(결정/보류/액션)을 해당 폴더로 분류
  - **Query**: 특정 주제의 결정·보류 항목 검색 → 답변 합성 (인용) → 결과 기록
  - **Lint**: 무결성 체크 (orphan 항목, 중복 액션, 다다다 진행 중 액션, 깨진 cross-ref)

---

## 회의록 SSOT에 이 원리를 어떻게 적용할 건가

**목적**:
1. 팀이 회의록을 직접 관리 (SSOT)
2. 다음 회의 아젠다를 뽑을 때 이전 결정·보류 항목을 참고

**특징**:
- 회의는 "정보 소스"이지 "최종 문서"가 아님 → 원본은 녹음/노트 형태이고, 위키는 구조화·정리된 마크다운
- 결정과 액션은 분리 (무엇을 하기로 했는가 vs 누가 언제까지 할 것인가)
- 이력은 추적하되, 최신 상태만 운영 중심으로 봄

---

## 확정된 사항

### 폴더 구조 (확정)

```
wiki-harness/
├── raw-sources/
│   └── 회의록/
│       ├── 2026-04-16-제품주간회의.md
│       ├── 2026-05-14-제품주간회의.md
│       └── ...
├── wiki/
│   ├── decisions/
│   ├── pending/
│   ├── action_items/
│   ├── rejected/
│   ├── index.md
│   └── log.md
└── handover/
    └── 01-ssot-design-handover.md
```

### 폴더 분류 (확정)

| 폴더 | 용도 | 특징 |
|------|------|------|
| `decisions/` | 확정 결정사항 | SSOT의 핵심. "### 결정" 섹션의 항목들. 한 번 여기 들어오면 이력 유지. 번복 시 새 파일 추가. |
| `pending/` | 보류 항목 | "다음 회의에서 재논의", "논의 보류" 같은 항목들. 다음 회의 아젠다 후보의 원천. |
| `action_items/` | 액션 아이템 | 담당자·마감일이 붙은 실행 과제. `[ ] 담당자 — 업무 설명 (~마감일)` 형식. |
| `rejected/` | 기각/대체된 항목 | 검토했지만 선택되지 않은 항목 (예: A안 vs B안 중 B안 선택 시 A안은 rejected). |

---

## Raw Sources (SSOT 원천 데이터)

### 원칙
- **변경 불가**: 원본 회의록은 한 번 적재되면 수정하지 않음 (감사 추적)
- **단일 출처**: `C:\wiki-harness\raw-sources\회의록\` 폴더가 모든 회의의 유일한 원천
- **진실 공급원**: Wiki의 모든 items는 이곳을 인용함

### 파일 이름 규약

```
YYYY-MM-DD-주제.md
예: 2026-04-16-제품주간회의.md
```

**Frontmatter** (원본 회의록 — SSOT 스키마):

```yaml
---
# 필수 필드
회의일: YYYY-MM-DD
주제: 회의 이름
참석자:
  - 이름 (직책)
  - 이름 (직책)

# 선택 필드 (출처 추적용)
출처: Notion | 직접작성 | 메일 | 기타
출처_url: https://... (해당하면)
적재일: YYYY-MM-DD
노트: 추가 context (선택사항)
---
```

**필드 설명**:
- `회의일`: 실제 회의가 열린 날짜
- `주제`: 회의 이름 (파일명에도 포함)
- `참석자`: YAML 리스트 형식 (수정 불가)
- `출처`: 원본이 어디서 왔는지 (감사용)
- `적재일`: 이 파일이 raw-sources에 언제 들어왔는지
- 나머지는 optional

### Wiki 페이지 (decisions, pending, action_items, rejected)

**파일 이름**: 
```
[영역]-[YYYY-MM-DD]-[간단한설명].md
예: 
  - 결제-2026-04-16-PG사선정.md
  - 온보딩-2026-06-25-3단계이탈률개선.md
```

**Frontmatter** (Wiki 페이지 공통):
```yaml
---
타입: decision | pending | action_item | rejected
출처: 2026-04-16-제품주간회의.md
결정일: YYYY-MM-DD
상태: active | resolved | obsolete
태그: [태그1, 태그2]
owner: 이름
---
```

**Frontmatter 추가 필드**:

| 타입 | 필드 | 설명 |
|------|------|------|
| decision | 결정내용 | 무엇을 결정했는가 |
| pending | 다음논의 | 다음에 언제 다시 다룰지 |
| action_item | 담당자 | 누가 |
| action_item | 마감 | YYYY-MM-DD |
| action_item | 상태 | pending / in_progress / completed / blocked |
| rejected | 대체안 | 대신 선택된 안 (있으면) |

---

## 미해결 질문 (현재 세션에서 결정 필요)

### 1. 결정 번복(revision) 규칙
현재 회의록에서 "연동 완료 목표: 5월 말 → 6월 중순 → 7월 초" 같이 여러 번 변경되는 항목들이 있습니다.

- **Option A**: 한 파일 내에서 변경 이력을 누적 기록 (스포일러 방식)
- **Option B**: 새로운 결정 파일 작성 + 이전 파일을 `obsolete` 상태로 표시
- **선택 기준**: 변경 이력의 중요도? (번복 과정 자체가 인사이트인가?)

### 2. Pending 항목의 재논의 추적
"정산 주기"는 6/11, 7/09 두 회의에서 "다음에 재논의"로 계속 보류됩니다.

- **Option A**: 같은 pending 파일에 `논의일자: [2026-06-11, 2026-07-09, ...]` 형식으로 누적
- **Option B**: 회의 카드 스타일 — 매번 새로운 pending 파일 생성 + 링크로 연결
- **선택 기준**: pending 항목이 얼마나 자주 재등장하는가?

### 3. Action Item 진행 상황 표시
현재 회의록의 체크박스 형식 (`[ ] `, `[x] `)을 wiki 항목 상태와 어떻게 연결할지.

- **Option A**: action_items 폴더의 각 파일에 `상태: pending / in_progress / completed / blocked` 필드 사용
- **Option B**: Obsidian 스타일 dataview로 status별 쿼리 자동화
- **선택 기준**: LLM이 상태를 자동으로 업데이트할 것인가? 수동인가?

### 4. 영역(domain) 분류 체계
회의록을 읽으면 자연스럽게 "결제" "온보딩" "정산" 같은 영역들이 나타납니다.

- **Option A**: 미리 정의된 영역 목록 + 파일 이름에 영역 prefix (예: `결제-2026-04-16-PG사선정.md`)
- **Option B**: 태그 기반 (frontmatter의 `tags: [결제, PG연동]`)
- **선택 기준**: 구조를 먼저 정할 것인가? 아니면 회의록들을 ingest하면서 emerge할 것인가?

### 5. Wiki 페이지 자동 생성 vs 수동 큐레이션
원본 회의록의 각 "## 안건" → decisions/pending/rejected 항목으로 변환하는 방식.

- **Option A**: LLM이 원본 회의록을 읽고 항목들을 자동 추출 + frontmatter 작성
- **Option B**: 수동 큐레이션 (사람이 각 회의 후 중요한 것만 선별해서 작성)
- **선택 기준**: 자동화의 정확도 vs 의도적인 필터링의 가치?

---

---

## Raw Sources 현황 (확정)

**폴더**: `C:\wiki-harness\raw-sources\회의록\`

**적재된 파일** (6개):
- 2026-04-16-제품주간회의.md
- 2026-05-14-제품주간회의.md
- 2026-06-11-제품주간회의.md
- 2026-06-25-온보딩개선회의.md
- 2026-07-09-제품주간회의.md
- 2026-07-23-제품주간회의.md

**Frontmatter 정규화 완료** — 모든 원본이 표준 스키마 준수:
```yaml
---
회의일: YYYY-MM-DD
주제: 회의 이름
참석자:
  - 이름 (직책)
  - ...
출처: Notion | 직접작성 | ...
적재일: YYYY-MM-DD
---
```

---

## 실제 원본 회의록 특성 (기초)

- **기간**: 2026-04-16 ~ 2026-07-23 (3.5개월, 6회)
- **참석 인원**: 4명 (PM, 개발, 디자인, 사업개발)
- **주요 테마**: 
  - 결제 연동 (계획 5월 말 → 최종 8월 중순, 3개월 지연)
  - 온보딩 개선 (A/B 테스트 성공, 이탈률 42% → 27%)
  - 정산 주기 (여전히 보류 상태)
- **패턴**:
  - 결정은 자주 변경 (외부 요인: PG사 연동 지연)
  - Pending 항목이 여러 회의에 걸쳐 재논의
  - Action item의 마감일도 함께 연기됨

---

## 다음 단계

1. **위 5가지 미해결 질문에 팀의 선택 결정**
   - 특히 Q4: "pending 항목이 계속 나타나는 현상을 어떻게 추적할 것인가"가 중요

2. **CLAUDE.md 작성** — 다음 3가지 워크플로우 정의:
   - **ingest**: 새 회의록 읽음 → items 추출 + 각 폴더로 분류
   - **query**: 특정 주제(예: "결제") 또는 상태(예: "pending") 검색 → 답변 합성
   - **lint**: orphan items, stale pending (N회 이상 재논의), broken refs 체크

3. **Wiki 폴더 구조 생성**:
   - `wiki/decisions/`, `wiki/pending/`, `wiki/action_items/`, `wiki/rejected/`
   - `wiki/index.md` (전체 항목 나열)
   - `wiki/log.md` (ingest/상태변경 이력)

4. **첫 ingest 실행** — 기존 6개 회의록을 정해진 스키마에 따라 분류

---

## 참고 자료

- Karpathy LLM Wiki: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- 원칙: "wiki is a persistent, compounding artifact" → 매번 재생성하지 말고, 지속적으로 유지·보수
