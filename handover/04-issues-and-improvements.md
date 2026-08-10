# 문제점 및 개선 제안

2026-04-16 ~ 2026-05-14 회의록 분석 과정에서 발견된 SSOT 설계의 문제점과 개선 방안

---

## 🔴 Critical Issues (즉시 해결 필요)

### 1. Orphan Items: 담당자 미정 항목이 추적 불가능

**문제**:
```
2026-04-16: "## 기타 - 재무팀에 정산 프로세스 확인 필요 (담당자 미정)"
↓
2026-05-14, 06-11, 07-09, 07-23: 언급 안 됨
→ 상태 불명, 누가 책임인지 불명확
```

**근본 원인**:
1. "담당자 미정"인 항목이 action_items 폴더에 들어갈 수 없음 (담당자 필수)
2. "기타" 섹션에만 있어서 wiki 폴더로 분류 안 됨
3. 상위 회의들에서 재논의되지 않음 (연속성 끊김)

**해결 방안**:
- **Rule 추가** (CLAUDE.md에 이미 반영됨):
  ```
  Rule: 담당자 미정 항목은 pending으로 올려서 
  "2026-XX-XX 회의에서 담당자 결정" 명시
  ```
- **Lint에 자동 검출 추가**:
  ```
  grep -r "담당자.*미정\|담당자.*[^가-힣]" wiki/action_items/
  ```

**영향**: wiki의 SSOT 신뢰도 저하

**상태**: ✓ CLAUDE.md에 Rule#1로 이미 추가됨

---

### 2. Pending 항목의 "무한 보류" 패턴

**문제**:
```
정산 주기:
- 2026-04-16: 월 1회로 결정
- 2026-06-11: "재논의 필요" (고객사 A의 주 1회 요청)
- 2026-07-09: 또 "재논의 필요"
- 2026-07-23: 아젠다에 올리지 않음 (계속 보류)
→ 3회 넘게 언급되었지만 여전히 미결정
```

**근본 원인**:
1. "다음 회의에서 재논의"가 반복되기만 함
2. Pending 파일이 언제 "해결"될지 불명확
3. 재논의 횟수를 추적할 방법 없음
4. "stale"된 항목이 계속 떠다님

**해결 방안** (이미 설계에 추가됨):
- **Pending 파일에 필수 필드 추가**:
  ```yaml
  재논의_횟수: 2
  다음_논의: "2026-08-XX (또는 TBD)"
  상태: stale  # 2회 이상 시 자동 마킹
  ```
- **Lint: Stale Pending 자동 검출**
  ```
  if 재논의_횟수 >= 2:
    상태 = "stale" → owner에게 알림
  ```

**영향**: 의사결정 지연, 조직 혼란

**상태**: ✓ Q#2 (Option A+)로 설계됨

---

## 🟡 Design Issues (설계 미흡)

### 3. Decision Revision의 파일 관리 복잡성

**문제**:
결제 연동 일정이 4단계 변경:
```
v1 (2026-04-16): 5월 말
v2 (2026-05-14): 6월 중순  ← 지금 여기
v3 (2026-06-11): 7월 초 (예상)
v4 (2026-07-23): 8월 중순
```

**현재 설계 (Option B)**:
- 각 버전마다 새 파일 생성 (`_v1.md`, `_v2.md`, ...)
- 이전 파일은 `obsolete` 상태로 표시

**문제점**:
1. **파일이 늘어남** (변경 4번 → 4개 파일)
2. **최신 버전 찾기 어려움** (index.md에서 active만 찾아야 함)
3. **변경 이력 추적 복잡** (모든 파일을 읽어야 변경 과정 파악)
4. **Cross-reference 복잡화** (action item이 어느 버전을 참고하는가?)

**개선 제안**:
```yaml
# 대안 1: 단일 파일 + 버전 히스토리 (Notion 스타일)
---
타입: decision_revision
이력:
  - 버전: 1
    날짜: 2026-04-16
    내용: 5월 말
    사유: 초기 목표
  - 버전: 2
    날짜: 2026-05-14
    내용: 6월 중순
    사유: A사 스펙 미수신
  - 버전: 3 (예상)
    날짜: 2026-06-11
    내용: 7월 초
    사유: 테스트 계정 발급 지연
---
```

**장점**:
- 파일 하나로 전체 이력 관리
- 최신 버전 명확
- "왜 변경되었는가"의 맥락 유지

**단점**:
- frontmatter가 복잡해짐
- markdown 스타일이 애매해짐
- 쿼리가 복잡함 (JSON 파싱 필요할 수도)

**상태**: ⏳ Q#1 (Option B) 선택되었으나, 장기적 개선 필요

---

### 4. Action Item과 Decision의 느슨한 결합

**문제**:
```
Decision: "결제 연동 완료 목표: 6월 중순"
  ↓
Action: "박준서 — A사 연동 스펙 확보 (마감: 5/21)"
  ↓
??? Decision이 변경되면 Action 마감도 바뀌어야 하는데?
```

**현황**:
- `결제-2026-05-14-결제-연동-일정-변경.md`에서 A사 스펙 문서를 prerequisite로 명시
- 하지만 `action-2026-05-14-박준서-a사-연동-스펙-문서-확보.md`에는 reverse 링크 없음
- 만약 decision이 "7월 초"로 또 변경되면, action 마감(5/21)을 수동으로 업데이트해야 함

**근본 원인**:
- Decision과 Action이 참조 관계만 있고, tight coupling이 없음
- 마감일 변경을 자동 추적할 방법 없음

**개선 제안**:
```yaml
# Action 파일에 결정 의존성 명시
---
타입: action_item
담당자: 박준서
마감: 2026-05-21
의존_결정: 결제-2026-05-14-결제-연동-일정-변경.md (v2)
마감_조정_규칙: |
  이 액션의 마감은 위 결정의 일정에 -7일로 자동 조정됨
  (스펙 수신 후 개발 착수까지 최소 1주 필요)
---
```

**영향**: 
- 결정 변경시 영향받는 액션 자동 식별
- 마감 충돌 감지

**상태**: ⏳ 향후 개선 필요

---

## 🟠 Process Issues (워크플로우 미흡)

### 5. Cross-Reference 관리의 복잡성

**현황**:
- `[[파일.md]]` 링크 문법 사용 중
- 하지만 깨진 링크 자동 검출 불가능
- 파일이름 변경시 모든 링크 수동 업데이트

**예시**:
```
# pending-2026-05-14-온보딩-이탈-문제.md
[[pending-2026-04-16-온보딩-개선-및-대시보드-개편.md]]
↑ 이 파일이 "대시보드" 아이템 때문에 이름이 바뀌면?
```

**개선 제안**:
1. **정규화된 ID 사용** (파일명 독립적):
   ```yaml
   # 각 파일에 고유 ID
   id: pending-20260416-onboarding-improvement
   
   # 참조는 ID로 (파일명이 아님)
   references: [pending-20260416-onboarding-improvement]
   ```

2. **Lint: 깨진 참조 자동 검출**
   ```bash
   ./lint.sh --rule=broken-refs
   ```

**상태**: ⏳ 향후 개선 필요

---

### 6. Index.md의 자동 생성 필요

**현황**:
- `wiki/index.md`: 수동으로 모든 항목 나열
- 파일을 추가/삭제할 때마다 수동 업데이트

**문제**:
- 파일 추가 후 index 업데이트 빼먹을 수 있음
- 대규모 ingest시 시간 소모

**개선 제안**:
```bash
# 자동 index 생성 스크립트
./scripts/generate-index.sh

# 출력:
# wiki/index.md 자동 생성
# - decisions: 14개 (active 13, obsolete 1)
# - pending: 6개 (active 5, stale 1)
# - action_items: 13개 (completed 1, in_progress 3, pending 9, blocked 0)
# - rejected: 5개
```

**장점**:
- 수동 오류 제거
- 통계 자동 업데이트
- Lint와 연계 가능

**상태**: ⏳ 선택사항 (현재는 수동으로도 관리 가능)

---

## 🟢 Minor Issues (개선 권장)

### 7. Frontmatter 필드 일관성

**현황**:
- Decision: `타입`, `출처`, `결정일`, `상태`, `태그`, `owner`
- Pending: `타입`, `출처`, `보류일`, `상태`, `논의일자`, `재논의_횟수`, `다음_논의`, `태그`, `owner`
- Action: `타입`, `출처`, `등록일`, `담당자`, `마감`, `상태`, `블로킹_원인`, `태그`

**문제**:
- 필드명이 일관성 없음 (`담당자` vs `owner`)
- 날짜 필드가 다름 (`결정일` vs `보류일` vs `등록일`)
- 어떤 필드는 선택, 어떤 필드는 필수인지 불명확

**개선 제안**:
```yaml
# 통일된 Frontmatter 스키마
---
# 필수 필드 (모든 타입)
타입: decision | pending | action_item | rejected | decision_revision
출처: raw-sources/회의록/YYYY-MM-DD-주제.md
상태: active | resolved | obsolete | stale | completed | blocked | pending | in_progress
태그: [영역1, 영역2]

# 조건부 필수 필드
owner: "이름" (decision, pending, action_item)
담당자: "이름" (action_item만)

# 공통 선택 필드
참고: "추가 context"
우선순위: high | medium | low (optional)
---
```

**상태**: ⏳ CLAUDE.md 개선 필요

---

## 📈 Improvement Roadmap

### Phase 1: 즉시 (1주)
- [ ] Q#4a, Q#5 PM 결정
- [ ] CLAUDE.md 최종 확정
- [ ] Lint 규칙 5가지 구현 (orphan, stale, no-owner, no-citation, broken-refs)

### Phase 2: 단기 (1개월)
- [ ] 나머지 회의록 4개 ingest (06-11, 06-25, 07-09, 07-23)
- [ ] Decision revision 문제 재검토 (단일 파일 vs 다중 파일)
- [ ] Action-Decision coupling 개선 방안 검토

### Phase 3: 중기 (3개월)
- [ ] Index 자동 생성 스크립트 구현
- [ ] Frontmatter 스키마 정규화
- [ ] Cross-reference ID 시스템 도입

### Phase 4: 장기 (6개월+)
- [ ] Query 자동화 (특정 주제 검색 → 답변 자동 합성)
- [ ] LLM 기반 decision revision 감지
- [ ] wiki ↔ Notion/Linear 양방향 동기화

---

## 📊 우선순위 요약

| 문제 | 심각도 | 영향범위 | 해결시간 | 우선순위 |
|------|--------|---------|---------|---------|
| Orphan items | 🔴 높음 | SSOT 신뢰도 | 30분 | **P1** |
| Stale pending | 🔴 높음 | 의사결정 | 30분 | **P1** |
| Decision revision 복잡성 | 🟡 중간 | 파일 관리 | 2시간 | **P2** |
| Action-Decision coupling | 🟡 중간 | 마감 관리 | 3시간 | **P2** |
| Cross-reference 관리 | 🟠 낮음 | 파일 유지보수 | 4시간 | **P3** |
| Index 자동화 | 🟠 낮음 | 편의성 | 2시간 | **P3** |
| Frontmatter 일관성 | 🟢 매우낮음 | 스타일 | 1시간 | **P4** |

---

## 결론

**지금까지 성과**:
- ✓ 5가지 미해결 Q 중 3가지 명확히 해결 (Q#1, Q#2, Q#3)
- ✓ 2가지는 조직 정책으로 분리 (Q#4a, Q#5)
- ✓ 신규 문제점 4가지 발견 (Q#4b, orphan, stale pending 등)
- ✓ CLAUDE.md 워크플로우 정의 완료
- ✓ 첫 ingest (2026-05-14) 실증 완료

**다음 단계**:
1. PM 결정 수렴 (Q#4a, Q#5)
2. Lint 규칙 구현 (P1: orphan, stale)
3. 나머지 회의록 ingest (06-11 이후)

---

*작성: 2026-08-10*
*상태: [프로젝트 진행 중]*
