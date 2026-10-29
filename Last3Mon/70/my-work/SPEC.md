# 실제 업무 자동화 공통 SPEC

## 1. 시스템 목표

직원 요청을 받아 AI가 초안을 만들고, 결정적인 검사는 Code 또는 Sub-workflow가 수행한다. 워크플로우마다 입력·출력 계약을 고정해 Agent 교체와 모듈 변경의 영향을 추적한다.

## 2. 공통 입력 계약

| 필드 | 형식 | 필수 | 설명 |
| --- | --- | --- | --- |
| `user` | string | 업무별 | 요청자 또는 직원 식별자 |
| `message` | string | 라우터 | 직원의 자연어 요청 |
| `facts` | string | 공지·SMS | 원문 사실, 날짜·시간 포함 |
| `request` | string | 선택 | 작성 목적이나 추가 요청 |
| `title` | string | 회의록 | 회의 제목 |
| `notes` | string | 회의록 | 회의록 원문 |

## 3. 공통 모듈 계약

### Rule Check v1.1

- ID: `modRuleCheck01`
- 입력: `facts`, `draft`, `max_length`, `required_phrases`, 선택 `allowed_domains`
- 결과: `{passed, codes, issues}`
- 사용처: 공지 검사 시험용 웹훅, SMS
- 원칙: 새 입력은 기본값을 두어 기존 호출을 깨지 않게 한다.

### Rule Check v2

- ID: `modRuleCheck02`
- 입력: v1.1과 동일
- 결과: `{passed, blocking, warnings, issues, version}`
- 사용처: 공지 키트와 v2 시험용 웹훅
- 원칙: 결과 의미가 바뀌므로 기존 ID를 덮어쓰지 않는다.

## 4. 업무별 결과 계약

| 업무 | 성공 결과 | 실패 결과 |
| --- | --- | --- |
| 공지 | `kind`, `route`, `published`, `notice`, `codes` | 누락 입력 400, 없는 종류 400 + `kinds` |
| SMS | `sms`, `published`, `codes` | `facts` 누락 400, 검사 실패 시 `published=false` |
| 라우터 | `count`, `results`, `reply` | Agent 실패 업무만 담당자 연결 |
| 회의록 | `summary`, `actions` | notes 누락 시 입력 필요 |
| 출장비 | `total`, `items`, `route`, `codes` | 증빙·금액 규칙 위반 상세 코드 |

## 5. 노드 설계 규칙

1. Webhook은 POST와 `responseNode`를 사용한다.
2. LLM은 초안·분류를 담당하고, 날짜·길이·개인정보·필수 문장은 Code/모듈이 검사한다.
3. 여러 종류의 차이는 설정 표 한 곳에 둔다.
4. 여러 워크플로우가 쓰는 검사는 Execute Workflow 모듈로 분리한다.
5. HTTP Agent 호출에는 `neverError`와 timeout을 설정한다.
6. 오류도 결과 계약으로 바꾸어 다른 업무의 처리를 계속한다.

## 6. 테스트 기준

- 기본 계약 테스트: 정상 입력과 필수 입력 누락
- 경계 테스트: 길이 초과, 날짜·시간 누락, 개인정보, 외부 링크
- 복합 테스트: 여러 업무가 섞인 요청과 Agent 일부 장애
- 회귀 테스트: 모듈을 바꾼 뒤 모든 사용처를 다시 실행
- 반복 테스트: LLM이 있는 워크플로우는 `--repeat 3`

예시 명령:

```bash
uv run tools/flow.py check my-work/notice-kit.json
uv run tools/flow.py push my-work/rule-check.json my-work/rule-check-test.json
uv run tools/flow.py test cases/lab03-v2.json --repeat 3
```

## 7. 변경 관리

- 입력을 추가할 때는 선택값과 기본값을 둔다.
- 결과 필드를 삭제하거나 의미를 바꾸면 새 모듈 ID를 만든다.
- 영향 표에 사용 워크플로우와 테스트 파일을 기록한다.
- 변경 전·후의 같은 테스트 결과를 비교하고, 실패 보고서 경로를 남긴다.
