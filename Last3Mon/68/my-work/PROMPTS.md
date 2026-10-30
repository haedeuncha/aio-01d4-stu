# Lab 01 요청문

## 예제 2 · 업무 나누기 (결과: lab01 --repeat 3 → 21/21 통과)

```text
AGENTS.md를 먼저 읽고, 아래 조건으로 n8n 워크플로 JSON을 만들어 줘.

- 저장할 파일: my-work/split.json
- 웹훅: POST, 경로 my-split. 직원 요청 문장은 요청 본문의 message 필드.
- 하는 일: 요청 문장을 "업무" 목록으로 나누기만 한다. 아직 다른 Agent는 부르지 않는다.
- 나누는 방법: OpenAI gpt-4.1-mini가 나누고, 그 결과 글자를 Code 노드에서 읽어 목록으로 만든다.

[나누는 기준 — LLM 지시문(systemMessage)에 넣어 줘]
1. 업무 하나 = 한 사람이 한 번에 처리할 수 있는 일. "그리고", "또", "~고"에서 끊기는 경우가 많다.
2. 끊긴 조각이 같은 일을 말하면 하나로 합친다.
3. 업무 순서는 요청 문장에 나온 순서를 그대로 지킨다.
4. 업무 text에는 원문의 중요한 정보(접수번호 T-1002 같은 번호, 증상)를 빼지 말고 남긴다.
5. 유형은 셋 중 하나만 쓴다.
   - it: 사내 IT 문의 (예: 비밀번호, VPN, 프린터, 메일함, 접수번호 처리 상태)
   - meeting: 회의록 관련 (예: 회의록에서 할 일 정리, 회의 요약)
   - other: 위 둘이 맡을 수 없는 일 (예: 회식 장소 추천, 점심 메뉴)
6. 답은 설명 없이 JSON만: {"tasks": [{"type": "it", "text": "..."}]}

[결과를 읽는 Code 노드 — LLM 답을 그대로 믿지 말 것]
- 앞뒤에 다른 글자나 ```json 같은 표시가 붙어도 첫 { 부터 마지막 } 까지만 꺼내서 파싱한다.
- type이 it, meeting, other가 아니면 other로 바꾼다.
- text가 비어 있는 업무는 버린다.
- 파싱에 실패하면 {"count": 0, "tasks": [], "error": "split_failed"}를 돌려준다.
- 최종 결과: {"count": 업무 개수, "tasks": [{"type": "...", "text": "..."}]} (순서 유지)

[빈 요청]
- message가 없거나 공백뿐이면 LLM을 부르지 말고 바로 {"count": 0, "tasks": []}를 돌려준다.
  (cases/lab01.json 마지막 케이스의 기대값을 먼저 읽고, 상태 코드·필드를 그 기대에 맞춰 줘)

[완료 조건]
- 먼저 cases/lab01.json을 읽고 기대 결과에 맞게 만들어 줘.
- uv run tools/flow.py test cases/lab01.json --repeat 3 이 통과해야 한다.
```

## 과제 · 담당 Agent와 빠진 입력

```text
my-work/split.json을 고쳐 줘. LLM 지시문(systemMessage)은 고치지 말고, 결과를 읽는 Code 노드에서 규칙으로 정해 줘.

[1. 담당 Agent — 유형으로 표에서 정한다]
- it → "it-agent"
- meeting → "meeting-agent"
- other → "담당자 연결"
각 업무에 agent 필드로 넣는다.

[2. 빠진 입력 — 요청 본문의 칸이 비었는지만 본다]
- meeting 업무인데 요청 본문의 notes가 없거나 비어 있으면 missing: ["notes"]
- 그 밖에는 missing: []
- 웹훅 본문의 notes를 Code 노드에서 읽을 수 있게 해 줘.

[3. 결과 예시]
{"count": 2, "tasks": [
  {"type": "it", "text": "T-1002 처리 상태 확인", "agent": "it-agent", "missing": []},
  {"type": "meeting", "text": "첨부 회의록에서 할 일 정리", "agent": "meeting-agent", "missing": []}
]}

[4. 완료 조건]
- cases/lab01-challenge.json 을 먼저 읽고 기대에 맞출 것.
- uv run tools/flow.py test cases/lab01-challenge.json --repeat 3 통과
- 원래 테스트 uv run tools/flow.py test cases/lab01.json 도 계속 통과 (기존 필드 count, tasks, type, text는 그대로)
```

### 하나 더 생각하기 (IT Agent는 user가 없으면 400)
- IT 업무인데 user가 비었으면 missing: ["user"]로 미리 표시하는 편이 낫다고 생각함 → Lab 03 과제에서 반영 예정.


## 68일차 전체 n8n 예제 실행

사용자 요청: “지금 68에 대한 예제 내용들을 전부 실행시키려고해”

진행 범위: 기존 split 유지, assistant·supervisor 작성, Lab 01~03 및 제공 과제 테스트, Lab 03 장애 복구, 경계 사례 6개와 측정 보고서. Credential은 AGENTS.md의 기존 OpenAI Credential만 사용.
