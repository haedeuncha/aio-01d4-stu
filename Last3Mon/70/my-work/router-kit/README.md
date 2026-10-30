# router-kit · 멀티 Agent 라우터를 찍어 내는 템플릿

68일차에 손으로 만든 HR · 출장 라우터를 70일차 방식(같은 것은 **모듈**로, 다른 것은 **설정 표 · 변수**로, 깨지는 변경은 **새 버전**으로)으로 정리했다.
이제 새 업무 라우터는 **값 파일 하나**로 만든다.

| 문서 | 내용 |
| --- | --- |
| [SPEC.md](SPEC.md) | 요구 R1~R6 (모두 ☑) · 숨은 요구 · 범위 밖 |
| [imp-plan.md](imp-plan.md) | 단계 0~9 진행 상태 · 변경 기록 (계속 바꾼 계획) |
| [DESIGN.md](DESIGN.md) | 같은 것 · 다른 것 비교, A안/B안, 변수, 모듈 계약, **영향 표** |
| [TEST-REPORT.md](TEST-REPORT.md) | 테스트 수치 · 실패와 고친 점 |
| [AGENTS.md](AGENTS.md) · [PROMPTS.md](PROMPTS.md) | 이 폴더 규칙 · 요청문 기록 |
| `diagrams/*.md` | tflow로 뽑은 흐름도 (VS Code 미리보기) |

## 새 라우터 찍는 법 (3줄)

```bash
cd ~/aio-01d4-stu/Last3Mon/70 && R=my-work/router-kit
cp $R/values/trip.yaml $R/values/my.yaml   # name · path · split_prompt · lanes · … 고치기
uv run $R/render.py $R/templates/n8n-router-v2 $R/values/my.yaml -o $R   # 값 검사 → rk-<path>.json + 기본 테스트
```

그다음 `flow.py check` → `push` → `test cases/<path>-basic.json --repeat 3`. 렌더한 파일은 손으로 고치지 않는다 (값 파일을 고쳐 다시 렌더).

새 업무 종류(갈래)는 값 파일 `lanes`에 **한 줄**:

```yaml
lanes:
  policy:  {agent: a3-trip-policy, body: {question: text, user: user, city: city}, required: []}
  expense: {agent: a3-trip-expense, body: {user: user, city: city, start: start, end: end|start}, required: [city, start],
            ask: '출장 도시와 날짜를 알려 주세요.'}
```

`body`의 꺼낼 곳: `user`(웹훅 입력) · `text`(업무 문장) · 칸 이름 · `a|b`(앞이 비면 뒤) · `body.칸`(웹훅 본문) · `'{칸} 글자'`(끼워 넣기)

## 폴더

```text
router-kit/
├── templates/n8n-router/        템플릿 v1 (답장 모듈 v1) · template.yaml · [[ path ]].json · cases/[[ path ]]-basic.json
├── templates/n8n-router-v2/     템플릿 v2 (답장 모듈 v2: 첫 줄 처리 요약 · summary)
├── values/hr.yaml · trip.yaml   값 파일 (v1 · v2 공통)
├── render.py                    렌더 + 값 검사 (--check: 원본과 비교)
├── rk-hr.json                   70-7  HR 라우터 (템플릿 v1로 찍음)
├── rk-trip.json                 70-8  출장 라우터 (템플릿 v2로 찍음)
├── rk-build-reply.json          70-9  모듈 modBuildReply01 (v1)
├── rk-build-reply-v2.json       70-11 모듈 modBuildReply02 (v2)
├── rk-reply-test.json · rk-reply-v2-test.json   70-10 · 70-12 모듈 시험용 웹훅
├── cases/                       테스트 (rk-hr · rk-trip · *-basic · rk-reply · rk-reply-v2)
├── tests/test_render.py         렌더 값 검사 테스트 (pytest)
└── diagrams/                    흐름도
```

## 한 번에 다시 확인

```bash
cd ~/aio-01d4-stu/Last3Mon/70 && R=my-work/router-kit
uv run tools/flow.py push $R/rk-build-reply.json $R/rk-build-reply-v2.json $R/rk-reply-test.json $R/rk-reply-v2-test.json $R/rk-hr.json $R/rk-trip.json
for c in rk-reply rk-reply-v2 rk-hr rk-hr-basic rk-trip rk-trip-basic; do uv run tools/flow.py test $R/cases/$c.json --repeat 3; done
uv run --with pytest --with pyyaml pytest $R/tests -q
```

- 라우터는 68일차 `a3-*` Agent를 부른다 (꺼져 있으면 그 업무만 `담당자 연결`).
- 모듈을 먼저 push해야 라우터가 부를 수 있다 (`template.yaml`의 `requires.modules`).
