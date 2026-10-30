# router-kit 실행 계획 (imp-plan)

기준: `SPEC.md` (R1~R6) · 규칙: `AGENTS.md`. 이 계획은 **계속 바꾸는 문서**입니다.

```mermaid
flowchart LR
  S0["0 문서"] --> S1["1 원본 rk-hr"] --> S2["2 같은 것 다른 것"] --> S3["3 모듈 modBuildReply01"] --> S4["4 템플릿 폴더"] --> S5["5 다시 찍어 비교"] --> S6["6 새 업무"] --> S7["7 렌더 도구 다듬기"] --> S8["8 버전 v2"] --> S9["9 보고서"]
```

## 진행 상태

| 단계 | 할 일 | 요구 | 상태 | 확인한 명령 · 결과 |
| --- | --- | --- | --- | --- |
| 0 | SPEC · AGENTS · imp-plan | | ☑ | 문서 3개 |
| 1 | 원본 `rk-hr` (a3-hr 복사, 웹훅만 다름) | R1 | ☑ | `cases/rk-hr.json` 21/21 (`runs/rk-hr-20261022-144201.json`) |
| 2 | `a3-hr` · `a3-trip` 비교 → 변수 후보 표 (`DESIGN.md` 2절) | R3 준비 | ☑ B안으로 정함 | 노드 22 · 연결 25 같은 모양, 같은 노드 10개 · 다른 노드 7개 · 이름만 다른 5쌍 → 갈래 A안/B안 결정 필요 (`DESIGN.md` 3절) |
| 3 | 모듈 `modBuildReply01` + 시험용 웹훅 `rk-reply`, `rk-hr`가 모듈을 부름 | R2 | ☑ | `cases/rk-reply.json` 12/12 (4 × 3) · 회귀 `cases/rk-hr.json` 21/21 (`runs/rk-hr-20261022-144447.json`) |
| 3.5 | 원본 `rk-hr`를 B안 모양으로 (갈래 설정 표 `Lane settings` + `Call agent` 하나 + Switch 3갈래) | R1 회귀 | ☑ | 노드 22 → 19, `cases/rk-hr.json` 21/21 (`runs/rk-hr-20261022-145152.json`) |
| 4 | `templates/n8n-router/` (template.yaml · `[[ path ]].json` · `cases/[[ path ]]-basic.json` · README) | R3 | ☑ | 변수 8개 = 파일에 쓰인 표시 8개 (빠짐 · 남음 없음) · n8n 표현식 `{{` 32개 원본과 같음 · `flow.py check` 오류 없음 |
| 5 | `render.py`: 값 파일로 렌더, `--check`로 원본과 비교 | R4 | ☑ | `values/hr.yaml` → `--check` "원본과 같음", 실제 렌더 후 바이트까지 같음 · 새로 생긴 `cases/rk-hr-basic.json` 9/9 · 따옴표 · 줄바꿈 · `{{ }}`가 든 값도 JSON 안 깨짐 · 빠진 값 5개와 없는 변수를 알려 줌 |
| 6 | 새 업무 라우터 하나를 렌더 → check · push · test | R5 | ☑ | `values/trip.yaml` → `rk-trip.json` 렌더, 손으로 고친 곳 0 (md5 같음) · 68일차 출장 테스트 그대로 24/24 (`runs/rk-trip-20261022-153143.json`) · 기본 9/9 · 접수 번호 · 일정 번호까지 68일차 라우터와 같음 |
| 7 | 렌더 도구: 변수 검사 (필수 · 경로 모양 · 이미 쓰는 경로 · 갈래 표) | R3 숨은 요구 | ☑ | `tests/test_render.py` 16 passed (n8n 검사 포함, 건너뜀 0) · ✘ 오류는 만들지 않음 · ⚠ 경고는 만들고 알림 |
| 8 | v2: `reply` 모양을 바꾸는 모듈 `modBuildReply02` · 템플릿 v2 · 영향 표 (B안이라 갈래 4개는 표 한 줄) | R6 | ☑ | v1 기대를 v2에 보내면 3/4 (깨지는 변경 확인) · `rk-trip`만 v2로 다시 찍음, `rk-hr`는 v1 · 영향 표 테스트 모두 × 3 통과: rk-reply 12/12, rk-reply-v2 12/12, rk-hr 21/21, rk-hr-basic 9/9, rk-trip 24/24, rk-trip-basic 9/9, pytest 16 |
| 9 | `TEST-REPORT.md` · `README.md` · `diagrams/` · SPEC 5절 | | ☑ 사람 확인 대기 | 보고서 · README(새 라우터 찍는 법 3줄) · tflow 흐름도 3개 · SPEC 결과 절 |

상태: ☐ 아직 · ◐ 하는 중 · ☑ 끝남 · ✖ 막힘

### 단계마다 돌려 보기 (`Last3Mon/70`에서)

```bash
uv run tools/flow.py check my-work/router-kit/<파일>.json
uv run tools/flow.py push  my-work/router-kit/<파일>.json
uv run tools/flow.py test  my-work/router-kit/cases/<케이스>.json --repeat 3
```

- 1단계 기대: `rk-hr` 7/7 × 3 (68일차 `a3-hr`와 같은 케이스, 웹훅만 `rk-hr`)
- 3단계 기대: `rk-reply` 통과 + `rk-hr` 7/7 × 3 (회귀)
- 5단계 기대: `uv run my-work/router-kit/render.py my-work/router-kit/templates/n8n-router my-work/router-kit/values/hr.yaml -o my-work/router-kit --check` → 원본과 같음
- 6단계 기대: 새 라우터 케이스 × 3, 렌더 뒤 손으로 고친 곳 0
- 7단계 기대: `uv run --with pytest --with pyyaml pytest my-work/router-kit/tests -q` 모두 통과

## 변경 기록 (최신이 위)

| 날짜 | 단계 | 바꾼 것 | 왜 |
| --- | --- | --- | --- |
| 2026-10-22 | 9 | `README.md`(처음 보는 사람용)와 `diagrams/`(tflow `--md`)를 더함 | 제출할 때 폴더만 보고도 실행할 수 있게 |
| 2026-10-22 | 8 | 깨지는 변경 = `reply` 첫 줄을 처리 요약으로 + `summary` 칸. 모듈 v2 `modBuildReply02`(`70-11`), 시험 `rk-reply-v2`(`70-12`), 템플릿 `templates/n8n-router-v2/`(모듈 id · 제목 메모 · 기본 테스트만 다름). 출장 값 파일 `name`을 "(템플릿 v2)"로 | v1을 쓰는 `rk-hr`는 그대로 두고 v2를 따로 쓰는 모습을 보이기 위해 · 값 파일은 v1 · v2 공통 |
| 2026-10-22 | 7 | 검사를 ✘ 오류(만들지 않음)와 ⚠ 경고(만들고 알림)로 나눔 · `template.yaml`의 `lanes` 종류를 `lanes`로 바꿔 전용 검사 · 같은 결과 파일을 다시 렌더하는 것은 허용, **다른 파일**이 쓰거나 새 라우터인데 **n8n에 등록된** 경로는 거절 · `--search`(찾을 폴더) · `--no-n8n` 옵션 · 경로 충돌 검사는 다른 오류가 없을 때만 함 | 값을 고쳐 다시 찍기는 막으면 안 됨 · 테스트가 진짜 my-work를 건드리지 않게 |
| 2026-10-22 | 6~7 사이 | n8n 이름을 다른 워크플로우와 맞춤: `70-7 · 🧭` HR 라우터, `70-8 · 🧳` 출장 라우터, `70-9 · 🧩` 모듈, `70-10 · 🧪` 시험. 라우터는 값 파일 `name`을 고쳐 **다시 렌더** (손으로 고치지 않음) → 다시 push · rk-reply 4/4 · rk-hr 7/7 · rk-trip 8/8 | 사람이 "이상한 것 · 훅이 적다"고 봄 → 이름이 목록 규칙과 달라 튀었음 (웹훅 수는 설계대로: 라우터 · 시험 각 1, 모듈 0) |
| 2026-10-22 | 6 | 처음 21/24: 68일차 `a3-trip-policy`(와 `a3-content-schedule`)가 n8n에서 꺼져 있었음 → 사람이 "켜고 다시 테스트"라고 해서 내용은 그대로 두고 publish만 다시 함 → 24/24 | 템플릿 탓이 아님 (꺼진 업무만 담당자 연결, 나머지 두 업무는 정상 = 장애 격리 확인) |
| 2026-10-22 | 6 | 새 업무로 "출장"을 고름 (68일차 손으로 만든 라우터의 테스트를 그대로 풀게 함) | 이미 있는 테스트로 템플릿 결과를 가장 확실하게 확인 |
| 2026-10-22 | 5 | `--check`에서 템플릿이 새로 만드는 파일(기본 테스트)은 실패가 아니라 "새로 생길 파일"로 알림 · 필수 값 검사와 없는 변수 검사는 5단계에 먼저 넣음 (경로 모양 · 이미 쓰는 경로 검사는 7단계) | 원본에 없던 파일 때문에 비교가 실패하면 안 됨 · 빠진 값으로 렌더하면 바로 알아야 함 |
| 2026-10-22 | 4 | 파일 이름도 변수(`[[ path ]].json`)로 · 기본 테스트용 변수 2개(`example_user`, `other_example`)를 더함 → 변수 8개 · `template.yaml`에 `requires.modules: [modBuildReply01]` | 렌더 결과 이름이 웹훅 경로와 같게 · 어느 라우터든 기본 테스트 3개가 함께 나오게 |
| 2026-10-22 | 3.5 | 3.5단계를 새로 넣음: 원본을 B안 모양으로 고치고 회귀 확인. 나누기 프롬프트의 결과 모양을 `{"shared": {}, "tasks": [...]}`로 통일 (출장의 `trip`도 `shared`로) · 업무 칸 정리(이름의 "님", kind · half)는 Agent가 이미 하므로 라우터에서 뺌 | 사람이 B안을 고름 · 템플릿에서 모든 라우터가 같은 Parse 코드를 쓰게 |
| 2026-10-22 | 8 · SPEC R6 | 버전 연습을 "갈래 4개"에서 "reply 모양 바꾸기(`modBuildReply02`)"로 바꿈 | B안에서는 갈래 추가가 깨지는 변경이 아님 |
| 2026-10-22 | 3 | `rk-hr`의 `Build reply` Code를 같은 이름의 모듈 호출 노드로 바꿈 (연결은 그대로) · 모듈 파일 이름 `rk-build-reply.json`, 시험용 `rk-reply-test.json` | 연결을 건드리지 않아 회귀 위험을 줄임 |
| 2026-10-22 | 2 | 비교해 보니 갈래 노드를 **설정 표 하나 + HTTP 노드 하나**로 줄일 수 있음(B안) → 4단계 전에 A안/B안을 사람에게 물음. B안이면 R6 버전 예시를 "갈래 4개"에서 "reply 모양 바꾸기(modBuildReply02)"로 바꿈 | 새 갈래가 표 한 줄이 되면 70일차 키트 방식과 같아짐 |
| 2026-10-22 | 1 | 68일차 `a3-hr`에서 실행 안내 메모(ask.py)를 빼고 복사 · 이름 · 웹훅만 바꿈 | 68일차 과제 파일은 그대로 두기 |
| 2026-10-22 | 0 | 처음 작성 | 5번 과제(라우터 템플릿) 시작 |
