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

### Ingest 스킬 사용

회의록을 wiki로 변환하는 상세 프로세스는 **ingest-meeting-minutes 스킬**에서 제공합니다.

**스킬 위치**: `.claude/skills/ingest-meeting-minutes/SKILL.md`

**사용 방법**:
```
회의록을 ingest해줄래.
경로: raw-sources/회의록/YYYY-MM-DD-주제.md
```

**스킬이 처리하는 것**:
- Step 1~7: 회의록 분석 → 메타데이터 추출 → Wiki 파일 생성
- 4가지 카테고리 분류 (Decision/Pending/Action/Rejected)
- Frontmatter 자동 생성
- 체크리스트 검증
- wiki/log.md 자동 기록

**주의사항** (스킬이 자동으로 처리):
- ✅ 모든 안건을 4가지 중 하나로 분류
- ✅ 담당자 미정 항목은 pending으로 올리기
- ✅ Decision revision 시 새 파일 + obsolete 표시
- ✅ Pending의 다음_논의는 구체적 날짜 명시
- ✅ Cross-reference 명시적 설정

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
