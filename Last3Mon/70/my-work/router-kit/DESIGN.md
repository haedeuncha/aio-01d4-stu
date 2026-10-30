# router-kit 설계

## 1. 같은 것 · 다른 것 (68일차 `a3-hr` ↔ `a3-trip`, 노드별 비교)

두 파일 모두 메모를 뺀 노드 22개, 연결 25개로 모양이 같다.

| 구분 | 노드 | 다른 점 | 템플릿에서 |
| --- | --- | --- | --- |
| **완전히 같음 (10)** | Has message and user? · Reject empty · OpenAI chat model · Has tasks? · Send no tasks · One item per task · Need input · Collect results · All results · Send result | 없음 | 그대로 |
| 이름만 다름 | `HR webhook` ↔ `Trip webhook` | 노드 이름 (표현식 `$('HR webhook')`이 여러 곳에서 이 이름을 씀) | 이름을 `Router webhook`으로 **고정** |
| 이름만 다름 | `Call balance agent` · `balance agent result` … ↔ `Call expense agent` … | 갈래(업무 유형) 이름이 노드 이름에 들어감 | 노드 이름을 갈래 이름과 떼어 냄 (아래 3절) |
| 웹훅 이름 때문만 다름 | `Build reply` | 코드 안의 `$('HR webhook')` 한 곳 | **모듈 `modBuildReply01`**로 뺌 (3단계) |
| 값만 다름 | `Other result` | 안내 문장 ("인사 문의 창구에서는 …" ↔ "출장 준비 비서는 …") | 변수 `other_answer` |
| 값만 다름 | `Split tasks` | 지시문(유형 목록 · 뽑을 칸 · 예시 JSON), 웹훅 이름 | 변수 `split_prompt` |
| 갈래마다 다름 | `Call … agent` | Agent 주소, 보내는 본문 (HR leave: `start · end · kind · half`, 출장 expense: `city · start · end · transport`) | 갈래 설정 표 (아래 3절) |
| 갈래마다 다름 | `… agent result` | `detail`에 담는 칸 (`remaining` ↔ `amount · breakdown`) | Agent 응답에서 `route` · `answer` 말고 나머지를 모두 `detail`로 (설정 불필요) |
| 도메인 규칙 | `Parse tasks` | HR: leave 날짜 검사, `target` 정리 · 출장: 출장 정보(`city · start · end`)를 한 번 뽑아 모든 업무에 붙임, 필수 칸 검사 | 공통 코드 + 갈래 설정 표의 `required`, `shared` (아래 3절) |
| 도메인 규칙 | `Route by lane` | Switch 출력 이름 (`balance · leave · policy` ↔ `policy · expense · schedule`) | 갈래 수를 고정하면 이름만 변수, 아래 3절 B안이면 **같아짐** |

## 2. 변수 (템플릿 v1 · B안으로 정함, `templates/n8n-router/template.yaml`)

| 변수 | 종류 | 예 (HR) | 예 (출장) | 비고 |
| --- | --- | --- | --- | --- |
| `name` | 글자 · 필수 | `router-kit · HR 라우터` | `router-kit · 출장 라우터` | 워크플로우 이름 |
| `path` | 웹훅 경로 · 필수 | `rk-hr` | `rk-trip` | 소문자 · 숫자 · `-`만, 이미 쓰는 경로는 안 됨 |
| `split_prompt` | 여러 줄 글자 · 필수 | 유형 balance · leave · policy · other … | 유형 policy · expense · schedule · other … | 따옴표 · 줄바꿈 많음 → JSON을 읽은 뒤 바꿔야 안전 |
| `other_answer` | 글자 | "인사 문의 창구에서는 …" | "출장 준비 비서는 …" | |
| `lanes` | 표 (갈래마다 한 줄) | 3줄 | 3줄 | 3절 |
| `shared` | 칸 목록 | (없음) | `city`, `start`, `end` | 한 번 뽑아 모든 업무에 붙이는 칸 |
| `example_user` | 글자 · 필수 | 박서연 | 이준호 | 기본 테스트용 (4단계에서 더함) |
| `other_example` | 글자 · 필수 | 월급 언제 들어와? | 부산 가는 KTX 표 예매해 줘 | 기본 테스트의 범위 밖 요청 (4단계에서 더함) |

## 3. 갈래를 어떻게 둘까 (2단계에서 찾은 결정 거리)

| | A안 · 갈래 3개 고정 (계획대로) | **B안 · 갈래 설정 표 (추천)** |
| --- | --- | --- |
| 모양 | Switch 출력 3개 + other + needs input, 갈래마다 HTTP · Set 노드 | Switch는 `agent` / `other` / `needs input` 3갈래만. HTTP 노드 **하나**가 설정 표의 주소로 부름 |
| 갈래 정보 | `lane1_key`, `lane1_agent`, `lane1_body` … 변수 15개 | `Lane settings` Code 노드의 표: `{ key: { agent, body, required, ask } }` |
| 새 갈래 | 템플릿 v2 (흐름이 바뀌는 깨지는 변경) | **표 한 줄** (70일차 공지 키트 `Kind settings`와 같은 방식) |
| 원본과 다른 점 | 원본과 거의 같은 모양 | 원본 `rk-hr`를 B안 모양으로 한 번 고쳐야 함 (고친 뒤 7 × 3 회귀 통과가 기준) |
| R6 버전 연습 | 갈래 4개 = v2 | 갈래 4개는 v2가 아님 → 다른 깨지는 변경으로 (예: `reply` 모양을 바꾸는 `modBuildReply02`) |

갈래 설정 표 (B안) 예:

```js
const LANES = {
  balance: { agent: 'a3-hr-balance', body: { user: 'user', target: 'target' }, required: [] },
  leave:   { agent: 'a3-hr-leave',   body: { user: 'user', start: 'start', end: 'end', kind: 'kind', half: 'half' },
             required: ['start'], ask: '언제 쉬실지 날짜를 알려 주세요. 예: "11월 6일 연차"' },
  policy:  { agent: 'a3-hr-policy',  body: { question: 'text', user: 'user' }, required: [] },
};
```

`body`는 "Agent가 받는 이름 → 업무에서 꺼낼 칸". `user`는 항상 웹훅 입력에서, 날짜 칸(`start`, `end`, `date`)은 요청 문장에 날짜 표현이 있을 때만 믿는다 (68일차 규칙 그대로, 공통 코드).

## 4. 모듈 계약

| 모듈 | id | 입력 | 결과 | 쓰는 곳 |
| --- | --- | --- | --- | --- |
| 답장 만들기 v1 | `modBuildReply01` (`70-9`) | `user`(글자), `results`(목록: `index · type · text · agent · route · answer · detail`) | `{count, results(index 순), reply}` · 첫 줄 "박서연 님, 요청하신 3가지를 정리했어요." | 템플릿 v1로 찍은 `rk-hr`, 시험 `rk-reply` |
| 답장 만들기 v2 | `modBuildReply02` (`70-11`) | v1과 같음 | `{count, summary, results, reply}` · 첫 줄 "박서연 님 · 3건 처리: ✅ 자동 답변 1 · ❓ 입력 필요 1 · …", `summary` = 처리 상태별 개수 | 템플릿 v2로 찍은 `rk-trip`, 시험 `rk-reply-v2` |

**왜 v2가 새 id인가**: v1 기대(`cases/rk-reply.json`)를 v2에 보내면 첫 케이스가 실패한다 (`reply has none of ['박서연 님, 요청하신 3가지를 정리했어요.']`, 3/4). `reply` 첫 줄을 보는 곳이 깨지는 변경이라 v1을 고치지 않고 `modBuildReply02`를 새로 만들었다 (70일차 AGENTS.md 9절).

## 5. 영향 표 (모듈 · 템플릿 버전마다 다시 돌릴 테스트)

| 바꾼 것 | 쓰는 곳 | 다시 돌릴 테스트 | 마지막 결과 (× 3) |
| --- | --- | --- | --- |
| 모듈 `modBuildReply01` (v1) | `rk-hr`, `rk-reply` | `cases/rk-reply.json`, `cases/rk-hr.json`, `cases/rk-hr-basic.json` | 12/12 · 21/21 · 9/9 |
| 모듈 `modBuildReply02` (v2) | `rk-trip`, `rk-reply-v2` | `cases/rk-reply-v2.json`, `cases/rk-trip.json`, `cases/rk-trip-basic.json` | 12/12 · 24/24 · 9/9 |
| 템플릿 `n8n-router` v1 | `rk-hr` (`values/hr.yaml`) | `render.py templates/n8n-router values/hr.yaml --check` + 위 v1 테스트 | 원본과 같음 |
| 템플릿 `n8n-router-v2` | `rk-trip` (`values/trip.yaml`) | `render.py templates/n8n-router-v2 values/trip.yaml --check` + 위 v2 테스트 | 원본과 같음 |
| `render.py` (값 검사) | 모든 템플릿 | `tests/test_render.py` | 16 passed |
| 68일차 `a3-*` Agent (부르는 쪽) | `rk-hr`, `rk-trip` (`Lane settings` 표) | `cases/rk-hr.json`, `cases/rk-trip.json` | 위와 같음 |

- 값 파일은 v1 · v2 템플릿에 **똑같이** 쓸 수 있다 (변수가 같음). `rk-hr`를 v2로 옮기려면 `render.py templates/n8n-router-v2 values/hr.yaml`로 다시 찍고, v2 테스트(`reply` 첫 줄 요약)를 돌린다.
