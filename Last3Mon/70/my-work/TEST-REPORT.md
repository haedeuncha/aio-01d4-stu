# 테스트 보고서 · 공지 키트와 규칙 검사 모듈

- 이름: 차해든
- 사용한 CLI 에이전트: claude (Claude Code)
- 워크플로우 파일: `my-work/notice-kit.json`(70-1 키트), `my-work/rule-check.json`(70-3 모듈 v1.1 `modRuleCheck01`), `my-work/rule-check-v2.json`(70-4 모듈 v2 `modRuleCheck02`), `my-work/sms.json`(70-2 SMS), `my-work/rule-check-test.json` · `rule-check-v2-test.json`(70-5 · 70-6 시험용 웹훅)
- 보고서 작성: 2026-10-23 (실습은 2026-10-22, 실패 기록은 `runs/`에서 다시 찾음)

## 1. 내가 쓴 테스트 (`cases/my-cases.json`)

키트(`my-notice-kit`)의 어려운 요청 7개.

| 케이스 | 요청 | 기대 결과 (업무 규칙) |
| --- | --- | --- |
| 종류에 대문자·공백 | `kind: " Security "` | 앞뒤 공백 · 대소문자를 정리해 `kind: security`로 게시 |
| 한국어 종류 이름 | `kind: "보안"` | 한국어 이름도 표의 종류로: `kind: security` |
| 공백만 보낸 사실 | `facts: "   "` | 빈 사실과 같음 → 400 |
| 없는 종류는 목록을 알려 줌 | `kind: "party"` | 400 + 쓸 수 있는 종류 목록 (`kinds`에 `survey`) |
| 바깥 링크를 넣어 달라는 요청 | 요청에 `http://bit.ly/report` | 요청이 규칙과 부딪혀도 규칙이 이김: `published: false`, `blocking`에 `external_link` |
| 사내 링크는 게시 | 신고 링크를 넣어 달라 (사내 주소) | `intra.example.com`은 허용 → `published: true`, 공지에 사내 주소 |
| 짧게만 써 달라고 해도 꼭 넣을 문장 | "한 줄로 아주 짧게" | 꼭 넣을 문장("비밀번호를 묻지 않습니다")은 빠지지 않음, `blocking: []` |

## 2. 실패와 고친 내용

| 실패한 케이스 | 처음 결과 (3번 중 통과) | 내가 생각한 원인 | 에이전트가 고친 곳 | 고친 뒤 (3번 중 통과) |
| --- | --- | --- | --- | --- |
| `lab01` 점검 · 머리말, 보안 · 꼭 넣을 문장, 교육 · 꼭 넣을 문장 (Lab 01 단계) | 6/15 (`runs/lab01-20261022-102728.json`, 세 케이스 모두 HTTP 500) | 키트 워크플로우가 실행 중 멈춤 (응답 칸이 모두 null). 그때 원인을 적어 두지 않음 | 키트 `notice-kit.json` | 15/15 (`runs/lab01-20261022-113233.json`) |
| `lab01-challenge` 새 종류 · 설문, 설문 · 익명 문장, 원래 종류도 그대로 | 3/12 (같은 시각, HTTP 500) | 위와 같은 실행 오류 | 키트 `notice-kit.json` | 12/12 (`runs/lab01-challenge-20261022-113232.json`) |
| 예제 1 하위 호환 (`lab03`) | 처음부터 4/4 | 실패 없음. 링크 검사는 `URL` 클래스 없이 (n8n Code 제약) | 모듈 v1.1, 같은 id `modRuleCheck01` | 12/12 |
| 예제 2 깨지는 변경 (`lab03-v2`) | 처음부터 5/5 | 실패 없음 | 새 id `modRuleCheck02`, 키트만 v2 | 15/15 |
| `my-cases` | 처음 실행부터 21/21 (`runs/my-cases-20261022-124852.json`) | 실패 없음 (키트 · 모듈을 고친 뒤에 씀) | — | 21/21 |

`runs/`에 남은 실패는 위 두 파일뿐이고, Lab 03(모듈 변경) 단계에서는 실패 기록이 없다.

## 3. 최종 결과 (2026-10-23 12:44~12:45 다시 실행)

| 테스트 파일 | 결과 |
| --- | --- |
| `cases/lab01.json` (키트) | Passed 5/5 |
| `cases/lab01-challenge.json` (키트 · 설문) | Passed 4/4 |
| `cases/lab02-module.json` (모듈 v1.1 시험) | Passed 5/5 |
| `cases/lab02-challenge.json` (SMS) | Passed 4/4 |
| `cases/lab03.json` (모듈 v1.1) | Passed 4/4 |
| `cases/lab03-v2.json` (모듈 v2, 키트, SMS) | Passed 5/5 |
| `cases/my-cases.json --repeat 3` | Passed 21/21 |

파일을 직접 열어 함께 확인한 것:

| 확인 | 결과 |
| --- | --- |
| 모듈 v1.1 `modRuleCheck01` | 입력 `allowed_domains` 추가, 안 주면 `['intra.example.com']`. 코드 `external_link` 추가, 결과 필드 `passed` · `codes` · `issues`는 그대로 → 하위 호환 |
| 모듈 v2 `modRuleCheck02` | 결과 `{passed, blocking, warnings, issues}`, `too_long`만 경고. v1 파일은 덮어쓰지 않음 |
| 누가 무엇을 부르나 (`executeWorkflow`의 `workflowId`) | `notice-kit` · `rule-check-v2-test` → `modRuleCheck02`, `sms` · `rule-check-test` → `modRuleCheck01`. `DESIGN.md` 5절 영향 표와 같음 |
| 키트의 계약 | v2로 옮겼어도 `lab01`이 통과 → 새 필드는 더하고 예전 필드는 남김 |
| Code 노드 | `new URL` 없음 |

## 4. 남은 문제 · 배운 점

- 지시문(systemMessage)으로 고친 것과 규칙 노드(If·Code)로 고친 것 중 어느 쪽이 더 안정적이었나? 규칙 쪽. 링크 · 연락처 · 꼭 넣을 문장 검사는 모듈(Code)이라 "링크 꼭 넣어 주세요", "아주 짧게" 같은 요청이 와도 3번 모두 같은 결과였다.
- 하위 호환 변경(입력 추가 + 기본값)은 같은 id로 고치고, push 직후 **쓰는 곳 테스트를 모두** 다시 돈다. 영향 표가 그 목록이다.
- 결과의 뜻이 바뀌는 변경(`passed`가 too_long에도 참, `codes` → `blocking`)은 새 id로 나란히 두고 쓰는 곳을 하나씩 옮긴다. SMS는 v1, 키트는 v2가 같은 n8n에서 함께 돈다.
- 아쉬운 점: Lab 01 단계의 HTTP 500 원인을 그때 적어 두지 않아 원인을 쓰지 못했다. 실패 보고서 경로와 원인은 바로 적는다 (71일차부터 `PROMPTS.md`에 바로 적음).
