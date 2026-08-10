# Wiki-Harness SSOT 워크플로우

회의록 기반 Single Source of Truth 하네스의 운영 가이드입니다.  
**기반 규칙**: `handover/05-rules-do-and-dont.md` 참고

---

## 목차
1. Ingest (회의록 → Wiki) — DO & DON'T 규칙 포함
2. Query (검색 및 합성)
3. Lint (무결성 검사) — 자동 검출

---

## 1. Ingest 워크플로우 (회의록 → Wiki)

### 목표
새 회의록을 raw-sources에 저장한 후, 각 항목을 wiki 폴더로 분류하기.

**핵심 원칙**:
```
모든 회의 안건 → decision/pending/action_item/rejected 중 정확히 하나로 분류
"기타" 섹션 방치 금지 → wiki로 분류 필수
```

---

### Step 1: Raw Source 적재

```
raw-sources/회의록/YYYY-MM-DD-주제.md
```

**필수 Frontmatter**:
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

**✅ DO**: 원본 회의록은 변경 불가 (감사 추적)

---

### Step 2: 수동 큐레이션 (회의 후 같은 날 또는 다음 날)

회의록의 각 안건을 읽고, **4가지 카테고리 중 정확히 하나**로 분류.

---

## A. Decision (결정사항)

### 정의
"우리는 이렇게 하기로 결정했다" — 명확한 선택이 있는 경우

### 파일명
```
wiki/decisions/[영역]-YYYY-MM-DD-[설명].md

예시:
- 결제-2026-05-14-pg사-최종-선정.md
- 온보딩-2026-06-11-3단계-개선-ab테스트.md
```

### Frontmatter
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

### Decision Revision (결정이 변경된 경우)

**✅ DO#3**: 새 파일 생성 + 이전 파일 obsolete 표시

```yaml
# 새 파일
---
타입: decision
결정일: YYYY-MM-DD
상태: active
이전_결정: 파일명.md  # ← 중요!
변경_사유: 구체적인 이유 명시
---

## 변경 사항
| 항목 | 이전 | 현재 | 사유 |
|------|------|------|------|
| ... | ... | ... | ... |
```

**❌ DON'T#3**: 기존 파일을 직접 수정하면 안 됨 (이력 소실)

### 예시 (올바른 것)

```yaml
# 결제-2026-05-14-결제-연동-일정-변경.md
---
타입: decision
출처: raw-sources/회의록/2026-05-14-제품주간회의.md
결정일: 2026-05-14
상태: active
이전_결정: 결제-2026-04-16-pg사-선정-프로세스.md
변경_사유: A사 스펙 문서 미수신으로 인한 재조정
태그: [결제, 일정]
owner: 이지혜
---

# 결제 연동 일정 변경: 5월 말 → 6월 중순

## 변경 사항
| 항목 | 이전 (v1) | 현재 (v2) |
|------|----------|----------|
| 연동 완료 목표 | 5월 말 | 6월 중순 |

## 관련 액션
[[action-2026-05-14-박준서-a사-연동-스펙-문서-확보.md]]
```

---

## B. Pending (보류 항목)

### 정의
"다음 회의에서 다시 다루자", "논의 보류", "아직 결정 미정"

### 파일명
```
wiki/pending/[영역]-YYYY-MM-DD-[설명].md

예시:
- 정산-2026-04-16-정산-주기.md
- 온보딩-2026-05-14-이탈-문제.md
```

### Frontmatter
```yaml
---
타입: pending
출처: raw-sources/회의록/YYYY-MM-DD-주제.md
보류일: YYYY-MM-DD
상태: active | stale
논의일자: [YYYY-MM-DD, YYYY-MM-DD, ...]
재논의_횟수: 숫자
다음_논의: YYYY-MM-DD or "TBD"
태그: [영역1]
owner: 담당자
---
```

### 규칙

**✅ DO#4**: 재논의_횟수와 다음_논의를 명시

```yaml
---
재논의_횟수: 2  # ← 중요! (자동 stale 판정 기준)
다음_논의: "2026-08-06 회의에서 강제 결정"
상태: stale  # ← 2회 이상이면 자동 마킹
---
```

**❌ DON'T#4**: "다음 회의에서 재논의"만 기록하면 안 됨
```yaml
# ❌ 나쁜 예
다음_논의: "다음 회의에서"  # 언제? 몇 번째?
→ 3번째 회의에서도 또 "다음"이 반복될 수 있음
```

### 예시

```yaml
# 정산-2026-04-16-정산-주기-재논의.md
---
타입: pending
보류일: 2026-04-16
논의일자: [2026-04-16, 2026-06-11, 2026-07-09]
재논의_횟수: 2
상태: stale
다음_논의: "2026-08-06 회의에서 강제 결정"
---

## 배경
- 2026-04-16: "월 1회"로 결정
- 2026-06-11: 고객사 A의 "주 1회" 요청 → 재논의 필요
- 2026-07-09: 또 재논의 (여전히 미결정)

## 상황
3회 논의했지만 미결정 상태 (stale).
다음 회의에서는 강한 의지로 반드시 결정해야 함.
```

---

## C. Action Item (액션 아이템)

### 정의
"누가, 언제까지, 무엇을 할 것인가" 명확한 액션

### 파일명
```
wiki/action_items/action-YYYY-MM-DD-[담당자]-[설명].md

예시:
- action-2026-05-14-박준서-a사-연동-스펙-확보.md
- action-2026-05-14-최민아-온보딩-이탈률-분석.md
```

### Frontmatter
```yaml
---
타입: action_item
출처: raw-sources/회의록/YYYY-MM-DD-주제.md
등록일: YYYY-MM-DD
담당자: 이름 (필수!)
마감: YYYY-MM-DD
상태: pending | in_progress | completed | blocked
블로킹_원인: (선택사항) 블로킹 이유
의존_결정: (선택사항) 결정 파일명
태그: [영역1]
---
```

### 규칙

**✅ DO#2**: 담당자가 없으면 pending으로 올리기

```yaml
# ✅ 좋은 예
담당자: 박준서  # ← 필수!
마감: 2026-05-21
```

**❌ DON'T#1**: 담당자 없는 action item 만들기
```yaml
# ❌ 나쁜 예
담당자: TBD  # or 미정 or ""
→ 책임 불명확, 다음 회의에서 orphan됨
```

### 예시

```yaml
# action-2026-05-14-박준서-a사-연동-스펙-문서-확보.md
---
타입: action_item
출처: raw-sources/회의록/2026-05-14-제품주간회의.md
등록일: 2026-05-14
담당자: 박준서
마감: 2026-05-21
상태: blocked
블로킹_원인: A사 담당자 응답 지연 (3일째 회신 없음)
의존_결정: 결제-2026-05-14-결제-연동-일정-변경.md
---

## 액션 설명
A사 연동을 위한 스펙 문서 확보

## 현황
- 상태: **blocked** (진행 불가)
- 원인: A사 담당자 응답 대기
```

---

## D. Rejected (기각/대체된 항목)

### 정의
검토했지만 채택되지 않은 안 (대체안이 선택된 경우)

### 파일명
```
wiki/rejected/rejected-YYYY-MM-DD-[설명].md
```

### Frontmatter
```yaml
---
타입: rejected
출처: raw-sources/회의록/YYYY-MM-DD-주제.md
결정일: YYYY-MM-DD
상태: rejected
대체안: 대신 채택된 항목 (있으면)
---
```

### 예시

```yaml
# rejected-2026-04-16-q2-중-온보딩-개선.md
---
타입: rejected
출처: raw-sources/회의록/2026-04-16-제품주간회의.md
결정일: 2026-04-16
상태: rejected
대체안: Q3로 연기 (Q2는 결제 연동 우선)
---
```

---

### Step 3: Cross-Reference 설정 (중요!)

**✅ DO#5**: 파일 간 참조 관계를 명시적으로 표현

```yaml
# Decision 파일에서:
이전_결정: 파일명.md
변경_사유: 구체적 이유

# Action 파일에서:
의존_결정: 파일명.md
관련_pending: 파일명.md

# Pending 파일에서:
관련_결정: 파일명.md
관련_action: 파일명.md
```

**❌ DON'T#5**: 암묵적 참고는 링크를 사용하지 않으면 안 됨
```yaml
# ❌ 나쁤 예
(설명에만 "이전 결정과 관련" 등으로 언급)
→ 자동 추적 불가능
```

---

### Step 4: 유지보수 기록

`wiki/log.md`에 매 ingest 후 기록:

```
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
- Orphan items 정리

**상태**: ✓ 완료 / ⏳ 진행중
```

---

### 최종 체크리스트 (Ingest 완료 전)

```
[ ] 모든 회의 안건이 4가지 카테고리 중 하나로 분류되었나?
[ ] "기타" 섹션에 남은 항목은 없나?
[ ] 모든 파일의 타입 필드가 명시되었나?
[ ] 모든 파일의 출처 필드가 명시되었나?
[ ] 모든 파일의 상태 필드가 명시되었나?
[ ] Action item의 담당자가 명시되었나? (없으면 pending으로)
[ ] Decision revision이 있으면 새 파일로 생성했나?
[ ] Pending 항목의 다음_논의가 구체적 날짜인가?
[ ] Cross-reference가 명시되었나?
[ ] wiki/log.md에 기록했나?
```

---

## 2. Query 워크플로우 (검색 및 합성)

### 목표
특정 주제나 상태의 항목들을 찾아서 답변을 합성하기.

### 사용 사례

#### Q: "결제 영역에서 현재 진행 중인 것들은?"

```bash
# 파일명 prefix로 검색
ls -la wiki/decisions/결제-* wiki/action_items/action-*결제*

# Active 항목만 필터
grep -l "상태: active" wiki/decisions/결제-*
grep -l "상태: in_progress\|blocked" wiki/action_items/

# 결과 읽기
cat wiki/decisions/결제-2026-05-14-*.md
```

#### Q: "정산과 관련해서 왜 자꾸 재논의되나?"

```bash
# Pending 파일 읽기
cat wiki/pending/정산-*.md

# → 논의일자, 재논의_횟수, 다음_논의 확인
grep -A3 "재논의_횟수\|다음_논의" wiki/pending/정산-*.md
```

#### Q: "박준서 담당 액션의 현황은?"

```bash
# 담당자별 검색
ls wiki/action_items/action-*박준서*

# 상태별 필터
grep "상태:" wiki/action_items/action-*박준서*.md
```

### 합성 (Synthesis)

1. 각 파일의 frontmatter + 본문 읽기
2. 질문에 맞는 항목들 모으기
3. 인용(cite)과 함께 답변 작성
4. 필요시 `wiki/log.md`에 "Query: ..." 기록

---

## 3. Lint 워크플로우 (무결성 검사)

### 목표
wiki의 데이터 품질 유지. 매 ingest 후 또는 주 1회 실행.

---

### Error 규칙 (즉시 수정)

#### Error#1: 담당자 없는 Action Item

```bash
# 검출
grep -r "담당자.*:\s*$\|담당자.*미정\|담당자.*TBD" wiki/action_items/

# 조치
→ 해당 파일을 pending으로 이동
→ 새 pending 파일: "YYYY-MM-DD-담당자-결정-필요.md"
```

**연관 규칙**: DO#2 (담당자 없는 액션 금지)

---

#### Error#2: 타입 필드 미표시

```bash
# 검출
for file in wiki/**/*.md; do
  grep -q "^타입:" "$file" || echo "Missing type: $file"
done

# 조치
→ 모든 파일의 frontmatter에 "타입: decision|pending|action_item|rejected" 추가
```

**연관 규칙**: DON'T#6

---

#### Error#3: 출처 필드 미명시

```bash
# 검출
grep -rL "^출처:" wiki/

# 조치
→ 모든 파일에 "출처: raw-sources/회의록/YYYY-MM-DD-주제.md" 추가
```

**연관 규칙**: DON'T#7

---

#### Error#4: 상태 필드 미표시

```bash
# 검출
grep -rL "^상태:" wiki/

# 조치
→ decision/pending/action_item/rejected에 맞는 상태 설정
  - decision: active | resolved | obsolete
  - pending: active | stale
  - action_item: pending | in_progress | completed | blocked
  - rejected: rejected
```

---

#### Error#5: 중복 Active Decision

```bash
# 검출
# 같은 주제 (prefix)의 파일이 2개 이상 active인 경우
for prefix in $(ls wiki/decisions/ | cut -d- -f1 | sort -u); do
  count=$(grep -l "상태: active" wiki/decisions/${prefix}-* | wc -l)
  [[ $count -gt 1 ]] && echo "ERROR: Multiple active for $prefix"
done

# 조치
→ 이전 버전을 "obsolete"로 표시
→ 이전_결정 필드로 연결
```

**연관 규칙**: DO#3 (새 파일 + obsolete 표시)

---

### Warning 규칙 (검토 필요)

#### Warning#1: Stale Pending (2회 이상 재논의)

```bash
# 검출
grep -B2 "재논의_횟수: [2-9]" wiki/pending/*.md | grep "파일명"

# 검증
→ 해당 파일의 상태가 "stale"인가?
→ 다음_논의가 명시되었나?

# 조치
→ 상태: stale로 자동 마킹 (안 되어 있으면)
→ 다음_논의를 명확한 날짜로 설정
```

**연관 규칙**: DO#4

---

#### Warning#2: Pending with "TBD" (30일 이상)

```bash
# 검출
# 다음_논의: TBD 상태인데 30일 이상 지난 pending
for file in wiki/pending/*.md; do
  보류일=$(grep "보류일:" "$file" | cut -d' ' -f2)
  지난날수=$(($(date +%s) - $(date -d "$보류일" +%s)) / 86400)
  [[ $지난날수 -gt 30 ]] && grep -q "다음_논의: TBD" "$file" && \
    echo "WARNING: Stale pending $file (${지난날수}d)"
done

# 조치
→ 다음_논의 날짜 명시
→ 또는 상태를 "resolved" 또는 "obsolete"로 변경
```

---

#### Warning#3: Orphan Items

```bash
# 검출
# 이전 회의에 언급되었는데 현재 회의에서 미언급된 항목
# (log.md 기반으로 수동 검토 필요)

# 조치
→ 해당 항목의 상태를 "resolved" 또는 "obsolete"로 변경
→ log.md에 "orphan 항목 정리" 기록
```

**연관 규칙**: DO#1 (모든 항목 추적)

---

#### Warning#4: Broken References

```bash
# 검출
grep -rh "\[\[.*\.md\]\]" wiki/ | while read ref; do
  file=$(echo "$ref" | grep -o "\[\[.*\.md\]\]" | tr -d '[]')
  [[ ! -f "wiki/$file" ]] && echo "WARNING: Broken ref: $ref"
done

# 조치
→ 파일명 수정 또는 참조 제거
```

**연관 규칙**: DO#5 (명시적 cross-reference)

---

### Lint 실행 (자동화 권장)

```bash
#!/bin/bash
# lint.sh

echo "=== Lint: Error Checks ==="
grep -r "담당자.*:\s*$" wiki/action_items/ && echo "ERROR: Found unassigned actions"
grep -rL "^타입:" wiki/ && echo "ERROR: Missing type field"
grep -rL "^출처:" wiki/ && echo "ERROR: Missing source field"

echo "=== Lint: Warning Checks ==="
grep -B2 "재논의_횟수: [2-9]" wiki/pending/*.md | grep "^파일" && \
  echo "WARNING: Found stale pending items"

echo "=== Lint Summary ==="
echo "✓ Lint completed"
```

---

## 최종 체크리스트

### 팀 전체 (매 ingest 후)

```
[ ] 모든 회의 안건이 분류되었나?
[ ] Error 규칙 5가지를 모두 만족하는가?
[ ] Warning 규칙 4가지를 검토했나?
[ ] wiki/log.md에 기록했나?
[ ] index.md를 업데이트했나? (선택사항)
```

### 각 항목별 (파일 생성 시)

**필수**:
- [ ] 타입 필드
- [ ] 출처 필드
- [ ] 상태 필드
- [ ] 담당자 (action_item만)

**조건부**:
- [ ] Decision revision: 이전_결정 + 변경_사유
- [ ] Pending: 다음_논의 (구체적 날짜) + 재논의_횟수
- [ ] Action: 담당자 + 마감 + 의존_결정 (있으면)

---

## 참고

- **설계 문서**: `handover/01-ssot-design-handover.md`
- **DO & DON'T 규칙**: `handover/05-rules-do-and-dont.md`
- **문제점 및 개선안**: `handover/04-issues-and-improvements.md`
- **Karpathy LLM Wiki**: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

---

*마지막 수정: 2026-08-10*
*상태: [운영 중]*
