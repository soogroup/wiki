# Ingest Skill 완성 및 CLAUDE.md 정리

**작성**: 2026-08-10  
**상태**: 완료 ✅  
**Commit**: `12240ba`

---

## 🎯 완성된 것

### 1. Ingest-Meeting-Minutes 스킬 생성

**위치**: `.claude/skills/ingest-meeting-minutes/`

```
ingest-meeting-minutes/
├── SKILL.md                    ✅ 696줄
│   ├── Frontmatter (메타데이터)
│   ├── 7단계 워크플로우
│   ├── 4가지 카테고리 정의
│   ├── Frontmatter 템플릿
│   └── 핵심 규칙 (DO 5가지, DON'T 5가지)
└── evals/evals.json            ✅ 3개 테스트 케이스
    ├── 간단한 분류
    ├── Decision revision 처리
    └── 담당자 미정 → pending 변환
```

**스킬이 하는 일**:
- Step 1: 회의록 분석 (Frontmatter, 안건 추출)
- Step 2: 4가지 카테고리 분류 (Decision/Pending/Action/Rejected)
- Step 3: 메타데이터 추출
- Step 4: Frontmatter 자동 생성
- Step 5: Wiki 파일 자동 생성
- Step 6: 체크리스트 자동 검증
- Step 7: wiki/log.md 자동 기록

**스킬이 적용하는 규칙**:
- ✅ DO#1: 4가지 카테고리 분류 필수
- ✅ DO#2: 담당자 미정 → pending으로 올리기
- ✅ DO#3: Decision revision 시 새 파일 + obsolete 표시
- ✅ DO#4: Pending의 다음_논의는 구체적 날짜 명시
- ✅ DO#5: Cross-reference 명시적 설정

---

### 2. CLAUDE.md 정리

**변경 사항**:
- ❌ Ingest 상세 내용 제거 (278줄 축약)
- ✅ Ingest 개요만 유지
- ✅ 스킬 참고 안내 추가
- ✅ Query & Lint 섹션 유지 (스킬에 없음)

**결과**:
- CLAUDE.md: 간결한 가이드 문서 (중복 제거)
- SKILL.md: 완전한 Ingest 워크플로우
- 유지보수성 ↑

---

## 📚 현재 프로젝트 상태

### 설계 & 규칙 (완료)
| 문서 | 상태 | 내용 |
|------|------|------|
| handover/01-ssot-design | ✅ | SSOT 설계 (5가지 Q 중 3가지 해결) |
| handover/03-decisions-pending | ✅ | 결정 대기 (Q#4a, Q#5 — PM 선택 필요) |
| handover/04-issues-and-improvements | ✅ | 7가지 문제점 + 개선 로드맵 |
| handover/05-rules-do-and-dont | ✅ | DO 5, DON'T 7 (상세 규칙) |
| CLAUDE.md | ✅ | Ingest 정리, Query/Lint 유지 |

### 스킬 (완료)
| 스킬 | 상태 | 역할 |
|------|------|------|
| ingest-meeting-minutes | ✅ | 회의록 → Wiki 자동 변환 |

---

## 🚀 사용 방법

### 이제 PM이 할 일

```
회의록을 ingest해줄래.
경로: raw-sources/회의록/YYYY-MM-DD-주제.md
```

또는

```
/ingest-meeting-minutes를 사용해줄래
```

### 스킬이 자동 처리

1. 회의록 분석 (Frontmatter, 안건)
2. PM이 4가지 분류 선택
3. 메타데이터 추출
4. Frontmatter 생성
5. Wiki 파일 생성 (4가지 폴더)
6. 체크리스트 검증
7. wiki/log.md 기록

---

## 📋 다음 단계

### 즉시 (PM 결정 필요)
- [ ] Q#4a: Domain 분류 — Option A(prefix) vs Option B(태그)
- [ ] Q#5: 자동화 — LLM 자동 vs PM 수동

### 단기 (1주)
- [ ] 2026-06-11 회의록 첫 ingest (스킬 테스트)
- [ ] 나머지 회의록 (06-25, 07-09, 07-23) ingest
- [ ] wiki/log.md 기록 검증

### 중기 (1개월)
- [ ] Lint 자동화 (Error/Warning 검출)
- [ ] Index 자동 생성
- [ ] Frontmatter 정규화

### 장기 (3개월+)
- [ ] Query 자동화
- [ ] LLM 기반 decision revision 감지
- [ ] 외부 도구 (Linear, Notion) 연동

---

## 📊 프로젝트 완성도

| 항목 | 상태 | 설명 |
|------|------|------|
| SSOT 설계 | ✅ | 5가지 Q 해결, 2가지 PM 선택 대기 |
| 규칙 정의 | ✅ | DO 5, DON'T 7 명확화 |
| 워크플로우 | ✅ | Ingest/Query/Lint 정의 |
| Ingest 스킬 | ✅ | 자동화 + 테스트 케이스 준비 |
| CLAUDE.md | ✅ | 중복 제거, 간결화 |
| 운영 준비 | ✅ | 첫 ingest 실행 가능 |

---

## 🎯 프로젝트 상태 요약

**완성 상태**: 약 80% ✅

- ✅ 설계 & 규칙: 완료
- ✅ 스킬 개발: 완료
- ✅ 문서 정리: 완료
- ⏳ PM 선택 대기 (Q#4a, Q#5)
- ⏳ 실제 ingest 운영 시작

**다음 담당자**: PM (이지혜)
- Q#4a, Q#5 최종 선택
- 첫 회의록 ingest 시작

---

*이 문서는 2026-08-10 Ingest 스킬 완성 및 CLAUDE.md 정리를 기록합니다.*
