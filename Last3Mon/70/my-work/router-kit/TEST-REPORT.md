# 테스트 보고서 · router-kit (멀티 Agent 라우터 템플릿 · 답장 모듈 · 버전)

- 날짜: 2026-10-22 (70일차 과제 5번)
- 사용한 CLI 에이전트: claude (Claude Code)
- 워크플로우 파일 (`my-work/router-kit/`): `rk-hr.json`, `rk-trip.json`, `rk-build-reply.json`(`modBuildReply01`), `rk-build-reply-v2.json`(`modBuildReply02`), `rk-reply-test.json`, `rk-reply-v2-test.json`
- 템플릿: `templates/n8n-router/`(v1), `templates/n8n-router-v2/`(v2) · 값 파일: `values/hr.yaml`, `values/trip.yaml` · 렌더 도구: `render.py`
- 실행 위치: `Last3Mon/70` · 명령: `uv run tools/flow.py test my-work/router-kit/cases/<파일>.json --repeat 3`

## 1. 내가 쓴 테스트

| 파일 | 웹훅 | 케이스 | 무엇을 확인하나 (업무 규칙) |
| --- | --- | --- | --- |
| `cases/rk-hr.json` | `rk-hr` | 7 | 68일차 HR 라우터 테스트 그대로: 복합 3업무 · 남의 연차 숨김 · 잔여 부족 거절 · 날짜 없음 → 입력 필요 · 범위 밖 · 빈 요청 400 · 규정에 없는 질문 |
| `cases/rk-trip.json` | `rk-trip` | 8 | 68일차 출장 라우터 테스트 그대로: 복합(규정 100,000원 · 출장비 290,000원 · 일정 등록) · 서울 180,000원 · 10박 팀장 결재 · 날짜 없음 2종 · 지난 날짜 거절 · 범위 밖 · 빈 요청 |
| `cases/rk-hr-basic.json`, `cases/rk-trip-basic.json` | 각 라우터 | 3 + 3 | **템플릿이 함께 만든** 기본 테스트: 빈 요청 400 · user 없음 400 · 범위 밖 → 담당자 연결 (v2는 첫 줄 요약 · `summary`도) |
| `cases/rk-reply.json` | `rk-reply` | 4 | 모듈 v1: 순서 섞인 결과 → index 순 · 아이콘 · 다음 할 일 줄 · 여러 줄 답 들여쓰기 · 결과 없음 |
| `cases/rk-reply-v2.json` | `rk-reply-v2` | 4 | 모듈 v2: 첫 줄 처리 요약 · `summary` 개수 · v1 첫 줄이 **없어야** 함 · 나머지는 v1과 같음 |
| `tests/test_render.py` (pytest) | — | 16 | 렌더 값 검사: 원본과 같음 · 경로 모양 5종 · 이미 쓰는 경로(파일 · n8n) · 갈래 표 오류 · 경고 · 빠진 값 · 따옴표 · 줄바꿈 · `{{ }}`가 든 값 |

## 2. 실패와 고친 내용

| 실패한 것 | 처음 결과 | 원인 | 고친 곳 | 고친 뒤 |
| --- | --- | --- | --- | --- |
| `rk-trip` 복합 3업무 | 21/24 (복합 케이스 3번 모두 실패) | 템플릿 탓이 아님. 68일차 `a3-trip-policy` Agent가 n8n에서 꺼져 있었음 (404 not registered). 꺼진 업무만 `담당자 연결`, 나머지 두 업무는 접수 번호까지 68일차와 같음 → **장애 격리 확인** | 사람 확인 후 그 Agent를 publish만 다시 (내용 · 이름 그대로) | 24/24 |
| `cases/rk-reply.json`을 v2 모듈에 보냄 | 3/4 | 일부러 한 시험: v2는 `reply` 첫 줄이 바뀜 → v1을 기대하는 곳이 깨짐 | v1을 고치지 않고 새 id `modBuildReply02` · 템플릿 v2로 분리 | v1 12/12 · v2 12/12 (둘 다 그대로 동작) |
| n8n 목록에서 router-kit 이름이 튐 ("이상한 것 · 훅이 적다") | — | 이름이 `70-<번호> · <이모지>` 목록 규칙과 달랐음. 웹훅 수는 설계대로 (라우터 · 시험 각 1, 모듈 0) | 라우터는 값 파일 `name`을 고쳐 **다시 렌더**, 모듈 · 시험은 이름만 → `70-7`~`70-12` | 테스트 그대로 통과 |
| `render.py --check` 처음 실행 | 실패 (exit 1) | 템플릿이 **새로 만드는** 기본 테스트 파일을 "없음 = 실패"로 셈 | 새 파일은 "새로 생길 파일"로 알림 | 원본과 같음 |

지시문으로 고친 것은 없다. 라우터의 날짜 · 빠진 칸 검사, 렌더 값 검사는 모두 **규칙(Code · Python)**이라 반복해도 결과가 같았다.

## 3. 최종 결과 (2026-10-22 15:47~15:49, 모두 `--repeat 3`)

| 테스트 파일 | 쓰는 버전 | 결과 | 보고서 |
| --- | --- | --- | --- |
| `cases/rk-hr.json` | 템플릿 v1 · 모듈 v1 | **Passed 21/21** | `runs/rk-hr-20261022-154828.json` |
| `cases/rk-hr-basic.json` | 템플릿 v1 | **Passed 9/9** | `runs/rk-hr-basic-20261022-154833.json` |
| `cases/rk-trip.json` | 템플릿 v2 · 모듈 v2 | **Passed 24/24** | `runs/rk-trip-20261022-154905.json` |
| `cases/rk-trip-basic.json` | 템플릿 v2 | **Passed 9/9** | `runs/rk-trip-basic-20261022-154909.json` |
| `cases/rk-reply.json` | 모듈 v1 | **Passed 12/12** | `runs/rk-reply-20261022-154755.json` |
| `cases/rk-reply-v2.json` | 모듈 v2 | **Passed 12/12** | `runs/rk-reply-v2-20261022-154757.json` |
| `tests/test_render.py` | render.py | **16 passed** | (pytest) |
| `render.py … --check` | v1 · hr / v2 · trip | **원본과 같음** (렌더 뒤 손으로 고친 곳 0) | — |

단계별 기록은 `imp-plan.md` "진행 상태", 결정 이유는 "변경 기록"에 있다.

## 4. 남은 문제 · 배운 점

- **템플릿은 잘 도는 원본에서 뽑는다**: 원본 `rk-hr`가 21/21인 상태에서 하나씩 바꿨기 때문에, 실패할 때마다 어느 단계 탓인지 바로 알 수 있었다 (모듈화 → B안 → 템플릿 → 렌더).
- **흐름을 바꾸는 값은 변수가 아니라 표로**: 갈래마다 노드를 두는 A안이었다면 갈래 추가가 템플릿 v2가 된다. B안(`Lane settings` 표 + `Call agent` 하나)은 갈래 추가가 표 한 줄이다. 70일차 공지 키트 `Kind settings`와 같은 생각.
- **가장 확실한 템플릿 확인 = 이미 있는 테스트를 그대로 풀게 하기**: 손으로 만든 68일차 출장 라우터의 테스트 8개를 템플릿 결과물이 그대로 통과했다.
- **표시 충돌**: n8n 표현식 `{{ }}`와 겹치지 않게 `[[ ]]`를 쓰고, JSON을 읽은 뒤 글자 값 안에서만 바꿔서 따옴표 · 줄바꿈 값도 안전했다.
- 남은 일: tkit TUI(템플릿 목록 · 변수 입력 화면)는 이번 범위 밖 (`render.py` 엔진까지). 값 파일 `values/hr.yaml`을 v2로 옮기면 `rk-hr`도 v2가 된다 (영향 표 참고).
- 테스트 날짜가 2026년 11월 기준이라, 그 뒤에 다시 돌리면 날짜를 앞으로 옮겨야 한다 (68일차와 같음).
