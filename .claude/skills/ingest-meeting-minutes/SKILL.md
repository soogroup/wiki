---
name: ingest-meeting-minutes
description: |
  회의록을 wiki-harness SSOT로 ingest합니다. 회의 안건을 4가지 카테고리(Decision/Pending/Action/Rejected)로 분류하고 
  wiki 파일들을 자동으로 생성하며, 체크리스트로 검증합니다.
  
  사용 시점: 새로운 회의록이 raw-sources에 저장되고 wiki 항목들로 변환해야 할 때 사용하세요.
  특히 PM이 수동 큐레이션을 할 때 각 단계별 프롬프트와 템플릿을 제공합니다.
---

# Wiki-Harness Ingest 스킬

## 개요

회의록 → Wiki 변환의 7단계 워크플로우를 안내합니다.

**Input**: 회의록 파일 (raw-sources/회의록/YYYY-MM-DD-주제.md)  
**Output**: wiki/ 폴더의 분류된 파일들 + wiki/log.md 기록

---

## 7단계 워크플로우

### Step 1: 회의록 읽고 분석하기

회의록 파일의 내용을 분석합니다:
```
1. Frontmatter 확인
   - 회의일, 주제, 참석자, 출처, 적재일

2. 안건(agenda items) 추출
   - "## 안건", "## 논의" 섹션 찾기
   - 각 안건별 내용 정리
```

---

### Step 2: 각 안건을 4가지 카테고리로 분류

**A. Decision (결정사항)**
- 정의: "우리는 이렇게 하기로 결정했다" — 명확한 선택
- 예: "PG사 A사로 선정", "월 1회 정산으로 결정"

**B. Pending (보류 항목)**
- 정의: "다음 회의에서 다시 다룰 것"
- 예: "정산 주기 재논의 필요"

**C. Action Item (액션)**
- 정의: "누가, 언제까지, 무엇을 할 것"이 명확
- 예: "박준서 — PG사 비교표 작성 (~4/23)"

**D. Rejected (기각)**
- 정의: 검토했지만 선택 안 한 것
- 예: "A안은 검토했으나 B안 선택"

**⚠️ 주의**: "## 기타" 섹션의 항목도 반드시 분류

---

### Step 3: 각 항목의 메타데이터 추출

**Decision**:
- 결정 내용 (핵심)
- 사유 (있으면)
- 담당자
- 이전 결정과의 관계? (revision인가?)

**Pending**:
- 보류 주제
- 이전 논의 이력
- 다음 논의 예상 날짜
- 담당자

**Action**:
- 액션 설명
- 담당자 (필수!)
- 마감일
- 의존 결정

**Rejected**:
- 기각 안건
- 대체 선택

---

### Step 4: YAML Frontmatter 생성

**필수 필드**:
```yaml
타입: decision | pending | action_item | rejected
출처: raw-sources/회의록/YYYY-MM-DD-주제.md
상태: [타입별 상태]
태그: [영역1, 영역2]
```

**Decision Frontmatter**:
```yaml
---
타입: decision
출처: raw-sources/회의록/2026-05-14-제품주간회의.md
결정일: 2026-05-14
상태: active | resolved | obsolete
태그: [결제]
owner: 이지혜
이전_결정: (revision이면) 파일명.md
변경_사유: (revision이면) 구체적 이유
---
```

**Pending Frontmatter**:
```yaml
---
타입: pending
출처: raw-sources/회의록/YYYY-MM-DD-주제.md
보류일: YYYY-MM-DD
상태: active | stale
논의일자: [YYYY-MM-DD, ...]
재논의_횟수: 숫자
다음_논의: "YYYY-MM-DD" or "TBD"
태그: [영역1]
owner: 담당자
---
```

**Action Frontmatter**:
```yaml
---
타입: action_item
출처: raw-sources/회의록/YYYY-MM-DD-주제.md
등록일: YYYY-MM-DD
담당자: 이름 (필수!)
마감: YYYY-MM-DD
상태: pending | in_progress | completed | blocked
블로킹_원인: (상태가 blocked이면) 이유
의존_결정: (있으면) 결정 파일명.md
---
```

**Rejected Frontmatter**:
```yaml
---
타입: rejected
출처: raw-sources/회의록/YYYY-MM-DD-주제.md
결정일: YYYY-MM-DD
상태: rejected
대체안: 대신 선택된 항목
---
```

---

### Step 5: Wiki 파일 생성

**파일명 규칙**:
- Decision: `wiki/decisions/[영역]-YYYY-MM-DD-[설명].md`
- Pending: `wiki/pending/[영역]-YYYY-MM-DD-[설명].md`
- Action: `wiki/action_items/action-YYYY-MM-DD-[담당자]-[설명].md`
- Rejected: `wiki/rejected/rejected-YYYY-MM-DD-[설명].md`

**파일 구조**:
```markdown
---
[Frontmatter]
---

# 제목

## 설명 (마크다운)

(필요하면 추가 섹션)
```

---

### Step 6: 최종 체크리스트

```
[ ] 모든 회의 안건이 4가지 카테고리 중 하나로 분류되었나?
[ ] "기타" 섹션에 남은 항목은 없나?
[ ] 모든 파일의 타입 필드가 명시되었나?
[ ] 모든 파일의 출처 필드가 명시되었나?
[ ] 모든 파일의 상태 필드가 명시되었나?
[ ] Action item의 담당자가 명시되었나? (없으면 pending으로)
[ ] Decision revision이 있으면 새 파일로 생성했나?
[ ] Pending의 다음_논의가 구체적 날짜인가?
[ ] Cross-reference가 명시되었나?
```

---

### Step 7: wiki/log.md 기록

```markdown
## YYYY-MM-DD
### Ingest: 회의 이름

**처리 항목**:
- Decisions: N개
- Pending: N개
- Action Items: N개
- Rejected: N개
- **합계**: N개

**특이사항**:
- Decision revision N개 적용
- Stale pending 발견 및 표시

**상태**: ✓ 완료
```

---

## 핵심 규칙

### ✅ DO

1. **모든 안건을 4가지 중 하나로 분류**
2. **담당자 미정은 pending으로 올리기**
3. **Decision revision 시 새 파일 + obsolete 표시**
4. **Pending의 다음_논의는 구체적 날짜 명시**
5. **Cross-reference 명시적 설정**

### ❌ DON'T

1. **"기타" 섹션에 항목 방치**
2. **담당자 없는 action item 생성**
3. **기존 파일 직접 수정**
4. **"다음 회의에서" 같은 모호한 표현**
5. **필수 필드 누락**
