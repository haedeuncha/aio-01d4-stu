# 릴리스 점검표 · IT 헬프데스크

## 1. 게이트 결과 (Lab 02)

| 릴리스 | 약한 golden (`cases/golden.json`) | 내가 고친 golden (`cases/my-golden.json`) | p95 | 판단 |
| --- | --- | --- | --- | --- |
| 1.0.0 | 6/6 PASS | 9/9 PASS | 3.0초 | 기준선 |
| 1.1.0 | 6/6 PASS | 9/9 PASS | 1.3초 | 출처 번호 릴리스 |
| 1.2.0 | 6/6 PASS | 1/9 FAIL | 1.5초 | 강한 golden에서 차단 |
| 2.0.0 | 6/6 PASS | 9/9 PASS | 1.8초 | 작은 모델 후보 |
| 2.1.0 | 설정 오류 | 0/9 FAIL | 0.0초 | p9 없음, `release broken` |

- 기준선: 1.0.0 VPN `bench -n 5` p50 1.23초 · p95 4.22초, 2.0.0 p50 1.26초 · p95 3.39초. 1.0.0 golden 3회 반복은 18/18, p95 1.8초였다.
- 강한 golden 기준은 통과율 100%, p95 3초 이하로 두었다.
- 2.0.0 판단: 강한 golden 9/9 PASS이고 2.0.0이 더 빠른 후보로 확인되었지만, 바로 전원 배포하지 않고 3단계 카나리로 먼저 시험한다.

## 2. 배포 순서 (Lab 03)

- [x] 후보를 고정(`--set release=`)으로 게이트 → PASS
- [x] 카나리 (`flow.py release helpdesk --canary <후보> --percent <N>`) → 카나리 사용자 답 확인
- [x] 릴리스 점검 (`my-release-check`) → `promote`, `/gates/helpdesk`에 기록 (`recorded: true`)
- [x] 배포 정책을 켠 상태에서 (`--require-gate on`) 점검을 지난 것만 배포되는지
- [x] 배포 (`flow.py release helpdesk <후보>`) → 답의 `version` 확인
- [x] 문제가 생기면 되돌리기 (`flow.py release helpdesk <이전>`, `--no-canary`) → 확인
- [x] `CHANGELOG.md`에 한 줄

## 3. 되돌리기 연습 기록

| 상황 | 한 일 | 걸린 시간 | 확인 방법 |
| --- | --- | --- | --- |
| 1.1.0 배포 → 되돌리기 (Lab 03 예제 1) | `release helpdesk 1.1.0` → `1.0.0` | 약 5초 | `lab03`: 2/2, version 확인 |
| 나쁜 카나리 1.2.0 50% (Lab 03 예제 3): 영향 받은 직원 2/6 | `--no-canary` | 약 2초 | 켠 뒤 4/6 → 끈 뒤 6/6 |
| 정책이 막은 배포 (Lab 03 과제 2) | rollback 1.2.0·미점검 2.0.0 거부 | 약 10초 | HTTP 409 `not gated`, 1.1.0은 배포 |

### Lab 03 점검 결과

- `my-release-check` 1.1.0: 6/6, `promote`, `recorded: true`
- `my-release-check` 1.2.0: 2/6, `rollback`, `recorded: true`
- `my-release-check` 2.0.0: 6/6, `promote`, `recorded: true`
- `release helpdesk --reset` 후 active 1.0.0, canary 없음, 정책 꺼짐
