# Wiki 검증 가이드

회의록을 Wiki로 ingest한 후, 두 단계로 검증합니다.

---

## 단계 1️⃣: 기계 검증 (자동 스크립트)

### 목표
Frontmatter, 스키마, 파일명 규칙 자동 검증

### 실행 방법

```bash
python .claude/scripts/validate-wiki.py wiki/
```

### 검증 항목

- ✅ **Frontmatter 검증**: 필수 필드 확인
  - decision: 타입, 출처, 상태, 결정일, owner
  - pending: 타입, 출처, 상태, 보류일, 다음_논의
  - action_item: 타입, 출처, 상태, 담당자, 마감
  - rejected: 타입, 출처, 상태

- ✅ **스키마 검증**: 필드 유효성
  - 타입: decision | pending | action_item | rejected
  - 상태 (타입별 유효값):
    - decision: active | resolved | obsolete
    - pending: active | stale
    - action_item: pending | in_progress | completed | blocked
    - rejected: rejected

- ✅ **파일명 규칙 검증**: 명명 규칙
  - Decision/Pending: `[영역]-YYYY-MM-DD-[설명].md`
  - Action: `action-YYYY-MM-DD-[담당자]-[설명].md`
  - Rejected: `rejected-YYYY-MM-DD-[설명].md`

### 출력 예시

```
============================================================
📋 Wiki 기계 검증 결과
============================================================

📊 통계:
  총 파일 수: 4
  통과 파일: 4
  오류: 0
  경고: 1

⚠️  경고 (1):
  - action-2026-06-11-박준서-a사-스펙-문서-확보.md: 파일명이 규칙과 약간 다릅니다

============================================================
```

### 오류 처리

**오류가 있으면** (exit code 1):
```bash
if [ $? -ne 0 ]; then
  echo "검증 실패! Wiki 파일을 수정하세요"
  exit 1
fi
```

---

## 단계 2️⃣: 컨텐츠 검증 (LLM Review)

### 목표
회의록과 Wiki의 일치성, 누락, 할루시네이션, 액션 추적 검증

### 사용 방법

```
/review-wiki-content를 사용해줄래

회의록: raw-sources/회의록/2026-06-11-제품주간회의.md
Wiki 파일들:
- wiki/decisions/결제-2026-06-11-pg사-a사-최종-선정.md
- wiki/decisions/결제-2026-06-11-결제-연동-완료-일정-변경.md
- wiki/action_items/action-2026-06-11-박준서-a사-스펙-문서-확보.md
- wiki/pending/온보딩-2026-06-11-온보딩-개선-q3-연기.md
```

또는

```
2026-06-11 회의록을 검증해줄래.
경로: raw-sources/회의록/2026-06-11-제품주간회의.md
```

### 검증 항목 (5가지)

| # | 항목 | 설명 | 예시 |
|---|------|------|------|
| 1 | **일치성** | 내용이 회의록과 일치? | 수수료 2.2% 확인 |
| 2 | **할루시네이션** | 없는 정보 추가? | 회의록에 없는 배경 설명 |
| 3 | **누락** | 중요 내용 빠짐? | 결정 사유 생략 |
| 4 | **액션 추적** | 상태 정확? 생명주기 추적? | pending → in_progress 이동 |
| 5 | **참조 정확성** | 링크 유효? | [[파일명.md]] 존재 |

### 검증 결과 포맷

각 Wiki 항목마다:

```
### 1. 일치성: ✅ PASS
내용이 회의록과 일치합니다.

### 2. 할루시네이션: ✅ PASS
회의록에 없는 정보가 추가되지 않았습니다.

### 3. 누락: ⚠️ WARNING
결정 사유가 간단합니다. 권고: "B사/C사 비교" 추가

### 4. 액션 추적: ✅ PASS (또는 N/A)
상태가 정확하고 블로킹 사유가 명시되었습니다.

### 5. 참조 정확성: ✅ PASS
모든 참조가 유효합니다.
```

### 결과 해석

- **✅ PASS**: 문제 없음, 그대로 유지
- **⚠️ WARNING**: 경미한 문제, 선택적 개선
- **❌ FAIL**: 심각한 문제, 수정 필수

---

## 전체 검증 워크플로우

### 1단계: Ingest 완료

```bash
# 회의록이 wiki로 변환되고 파일 생성됨
ls wiki/decisions/
ls wiki/action_items/
ls wiki/pending/
ls wiki/rejected/
```

### 2단계: 기계 검증

```bash
python .claude/scripts/validate-wiki.py wiki/

# 오류가 없으면 ✅ PASS
# 오류가 있으면 파일 수정 후 재실행
```

### 3단계: 컨텐츠 검증

```
/review-wiki-content를 사용해줄래
경로: raw-sources/회의록/2026-06-11-제품주간회의.md
```

### 4단계: 결과 분석

- FAIL 항목: 즉시 수정
- WARNING 항목: 선택적 개선
- 모두 PASS: Wiki 배포 가능

### 5단계: 최종 커밋

```bash
git add wiki/
git commit -m "Validate and refine wiki items for 2026-06-11 meeting

- Machine validation: 0 errors, 0 warnings
- Content validation: 0 fails, 2 warnings (선택적 개선)
- All items ready for deployment"
```

---

## 예시: 전체 검증 실행

### 회의록: 2026-06-11 제품주간회의

```bash
# 1. Ingest 완료
python .claude/scripts/validate-wiki.py wiki/

# 출력:
# ============================================================
# 📋 Wiki 기계 검증 결과
# ============================================================
# 📊 통계:
#   총 파일 수: 4
#   통과 파일: 4
#   오류: 0
#   경고: 0
# ✅ 모든 파일이 검증을 통과했습니다!

# 2. 컨텐츠 검증
# → /review-wiki-content 스킬 사용
# → 5가지 항목별 PASS/WARNING/FAIL 평가
# → 결과: 0 FAIL, 2 WARNING, 2 PASS

# 3. 커밋
git add wiki/ && git commit -m "Validate wiki items for 2026-06-11"
git push origin master
```

---

## 트러블슈팅

### 오류: "필수 필드 '담당자'가 없습니다"

```
파일: action-2026-06-11-박준서-a사-스펙-문서-확보.md
→ 수정: frontmatter에 "담당자: 박준서" 추가
```

### 오류: "유효하지 않은 상태 'preparing'"

```
파일: action-2026-06-11-...md
상태: preparing  ❌

수정:
상태: pending | in_progress | completed | blocked 중 선택
```

### WARNING: "파일명 규칙을 따르지 않습니다"

```
파일: action-2026-0611-박준서-a사.md  (날짜 형식 오류)
→ 수정: action-2026-06-11-박준서-a사-스펙-문서-확보.md
```

### 컨텐츠 검증 WARNING: "할루시네이션 감지"

```
문제: Wiki에 "완료 기준"이 있는데 회의록에는 없음
조치: 
1) 회의록 재확인 (정말 없는지?)
2) Wiki에서 제거하거나 "[추론된 정보]" 표시
3) 또는 PM과 협의 후 추가
```

---

## 자동화 (선택사항)

### Git Hook 설정 (커밋 전 자동 검증)

```bash
# .git/hooks/pre-commit 생성
#!/bin/bash
python .claude/scripts/validate-wiki.py wiki/
if [ $? -ne 0 ]; then
  echo "Wiki 검증 실패! 파일을 수정하세요"
  exit 1
fi
```

### CI/CD 파이프라인 (선택사항)

```yaml
# .github/workflows/validate-wiki.yml
name: Wiki Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: python .claude/scripts/validate-wiki.py wiki/
```

---

## 다음 단계

1. **기계 검증**: `validate-wiki.py` 스크립트로 자동 검증
2. **컨텐츠 검증**: `/review-wiki-content` 스킬로 수동 검증
3. **수정**: 발견된 문제 해결
4. **재검증**: 필요시 다시 실행
5. **배포**: 모든 검증 통과 후 커밋

---

*Wiki 검증은 데이터 품질을 보장합니다. Ingest 후 필수 단계입니다.*
