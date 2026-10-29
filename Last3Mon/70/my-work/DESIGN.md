# 재사용 설계서 · 공지 키트와 규칙 검사 모듈

- 이름: 실습생
- 사용한 CLI 에이전트: codex

## 1. 복사본 비교 (Lab 01 예제 1)

분석 대상은 `samples/notice-maintenance.json`, `samples/notice-security.json`, `samples/notice-training.json`이다. 세 시나리오는 모두 `facts`를 받아 한국어 공지를 작성하고 규칙 검사 후 게시 여부를 반환한다.

| 노드 | 세 파일에서 같은가 | 다른 것 (점검 · 보안 · 교육) | 통합 방법 |
| --- | --- | --- | --- |
| Notice webhook | 다름 | `sample-maintenance` / `sample-security` / `sample-training` | `my-notice-kit` 하나로 통합 |
| Has facts? | 같음 | 없음 | 그대로 사용 |
| Reject empty | 같음 | 없음 | 그대로 사용 |
| Writer agent | 다름 | 머리말, 필수 문장, 작성 주의사항 | `Kind settings` 표에서 읽기 |
| OpenAI chat model | 같음 | `gpt-4.1-mini`, temperature 0 | 그대로 사용 |
| Build draft | 같음 | 코드펜스 제거 | 그대로 사용 |
| Rule checks | 다름 | 최대 길이 600/500/800, 필수 문장 | 공통 모듈로 분리하고 설정값을 입력 |
| Build result | 다름 | `kind` 하드코딩 | 입력과 검사 결과로 구성 |
| Send result | 같음 | 없음 | 그대로 사용 |

보안 규칙을 하나 고칠 때 복사본 구조에서는 Writer agent와 Rule checks의 최소 2곳, 세 파일 전체에는 최대 6곳을 수정해야 한다.

## 2. 설정 표 (Lab 01)

| kind | 머리말 | 최대 길이 | 꼭 넣을 문장 | 주의 |
| --- | --- | --- | --- | --- |
| maintenance | `[점검 안내]` | 600 | 없음 | 작업 중 사용 불가 항목과 종료 후 조치 |
| security | `[보안 안내]` | 500 | `IT팀은 절대 비밀번호를 묻지 않습니다.` | 피싱과 비밀번호 요구 금지 |
| training | `[교육 안내]` | 800 | `신청은 IT 포털에서 할 수 있습니다.` | 대상·일시·장소·신청 방법 |
| survey | `[설문 안내]` | 500 | `응답은 익명으로 처리됩니다.` | 설문 목적과 마감일 |

새 종류를 추가할 때 수정하는 곳은 `Kind settings` Code 노드 한 곳이다. 표에 없는 종류는 HTTP 400과 `kinds` 목록을 반환한다.

## 3. 모듈 계약 (Lab 02)

| 모듈 | id | 입력 | 결과 | 쓰는 곳 |
| --- | --- | --- | --- | --- |
| 규칙 검사 v1.1 | `modRuleCheck01` | `facts` string, `draft` string, `max_length` number, `required_phrases` array, `allowed_domains` array(선택) | `passed`, `codes`, `issues` | `rule-check-test.json`, `sms.json` |
| 규칙 검사 v2 | `modRuleCheck02` | v1.1 입력과 같음 | `passed`, `blocking`, `warnings`, `issues`, `version` | `rule-check-v2-test.json`, `notice-kit.json` |

## 4. 변경 관리 (Lab 03)

| 변경 | 호환성 | 버전 | 확인 |
| --- | --- | --- | --- |
| 외부 링크 검사 `allowed_domains` 추가 | 하위 호환 | `modRuleCheck01` 유지 | 기존 결과 필드 유지, 기본 허용 도메인 적용 |
| `too_long`을 경고로 변경하고 결과 분리 | 호환되지 않음 | `modRuleCheck02` 신규 | SMS는 v1 유지, 키트만 v2 사용 |

## 5. 영향 표 (Lab 03 과제)

| 모듈 · 버전 | 사용하는 워크플로우 | 다시 실행할 테스트 |
| --- | --- | --- |
| `modRuleCheck01` (v1.1) | `rule-check-test.json`, `sms.json` | `lab03.json`, `lab02-module.json`, `lab02-challenge.json` |
| `modRuleCheck02` (v2.0) | `rule-check-v2-test.json`, `notice-kit.json` | `lab03-v2.json`, `lab01.json`, `lab01-challenge.json`, `my-cases.json` |
