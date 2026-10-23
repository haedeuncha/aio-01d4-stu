# 71일차 요청문 기록

- CLI 에이전트: claude (Claude Code)

## Lab 01 예제 1 · 정답표

- 에이전트 없이 문서(`data-api/data/docs/`)를 직접 읽고 `RAG-EVAL.md` 1절을 채움.

## Lab 01 예제 2 · 색인과 검색

```text
두 워크플로우를 만들어 줘. 계약은 AGENTS.md 3절, 노드는 5절.

1. my-work/index.json (웹훅 my-index)
   - 문서: GET http://data-api:8800/docs 로 목록 → 문서마다 GET /docs/<name>
   - 청크: Code 에서 본문을 "## " 섹션마다 하나씩. 청크 글 앞에 문서 제목을 붙인다.
     본문 chunking 이 숫자면 그 글자 수로 자른다 (기본 section, Lab 03에서 씀).
   - 함께 저장: source(문서 name), title, 청크 번호 (Default Data Loader 메타데이터)
   - 저장: 메모리 Vector Store (insert, memoryKey my_policy_docs, clearStore true) + OpenAI Embeddings text-embedding-3-large
   - 결과: { indexed_chunks, chunking }

2. my-work/search.json (웹훅 my-search)
   - question 이 없으면 400
   - 같은 저장소에서 load, topK = 본문 top_k (없으면 3), 메타데이터 포함
   - 저장소가 비어도 멈추지 않게: Always Output Data, 다음 Code 에서 document 가 있는 항목만
   - 결과: { question, hits: [{ rank, source, title, score(소수 셋째 자리), text }], top_score, indexed }

기대 결과는 cases/lab01.json. push · test까지 해 줘.
```

- 결과: `indexed_chunks` 25 · `lab01` **18/18** (`--repeat 3`, `runs/lab01-20261023-104244.json`)

## Lab 01 과제 · 섹션까지 출처, 개수는 요청에서

```text
my-work/index.json 의 Make chunks 에서 청크마다 section(그 청크의 "## " 제목 글자)을 정하고,
Loader 메타데이터에 section 을 더해 줘.
my-work/search.json 의 hits 에 section 을 더해 줘 (없으면 빈 글자).
top_k 는 본문에서 받는다 (기본 3).
cases/lab01-challenge.json, cases/lab01.json 둘 다 통과.
```

- 결과: `lab01-challenge` **12/12** (`runs/lab01-challenge-20261023-104927.json`) · `lab01` 그대로 **18/18** (`runs/lab01-20261023-104937.json`)
- 섹션 제목은 검색할 때 글에서 찾지 않고 **색인할 때** 메타데이터로 저장 → 검색은 꺼내기만. 글자 수로 자를 때는 섹션이 없으므로 빈 글자.

## Lab 02 예제 1 · 발췌로만 답하고 출처 붙이기

```text
my-work/policy-qa.json 을 만들어 줘. 계약은 AGENTS.md 3절 규정 Q&A. question 없으면 400.
1. 같은 메모리 저장소(my_policy_docs)에서 load, topK 3, 메타데이터 포함, Always Output Data.
2. Code "Build context": 청크를 [1] [2] [3] 번호 붙인 발췌로, hits(source, title, score), top_score.
3. AI Agent(gpt-4.1-mini, Tool 없음): 발췌로만, 한국어 3문장 이내, 사실마다 [번호],
   없으면 정확히 "규정에서 답을 찾지 못했습니다."
4. Code "Build answer": [번호] → [문서 제목], cited = 인용한 번호의 source, route "자동 답변". 범위 밖 번호는 버린다.
기대 결과 cases/lab02.json 앞 네 케이스. push · test까지.
```

- 검색 노드를 Q&A 안에 다시 둠 (검색을 쓰는 곳이 여기 하나라서 HTTP로 부르지 않음).
- 결과: 앞 네 케이스 + 질문 없음 **15/15**, 점심 메뉴만 3/3 실패 (예제 2에서 고칠 곳, `runs/lab02-20261023-105133.json`)

## Lab 02 예제 2 · 관련 없으면 담당자 연결

```text
my-work/policy-qa.json 을 고쳐 줘.
1. Build context 에 min_score = 본문 min_score (없으면 0.33), relevant = top_score >= min_score.
2. If "Relevant?" 를 Build context 뒤에 둔다.
3. relevant 가 아니면 LLM 을 부르지 않고 route "담당자 연결",
   answer "규정에서 답을 찾지 못했습니다. IT 문의 창구로 연결해 드릴게요.", cited [].
4. 결과 모양(route, answer, sources, cited, top_score)은 두 길 모두 같게.
기대 결과 cases/lab02.json 전부. push · test까지.
```

- 0.33 근거: 내 Lab 01 기록 규정 질문 0.46~0.75, 규정 밖 0.20~0.26 (AGENTS.md 3절 범위와 같음).
- 결과: `lab02` **18/18** (`runs/lab02-20261023-110217.json`). `min_score: 0.9`로 보내면 규정 질문도 담당자 연결 (본문 값이 먹는지 확인).

## Lab 02 과제 · 점수는 높은데 규정에 답이 없을 때

고치기 전 `lab02-challenge` **2/8** (`runs/lab02-challenge-20261023-110439.json`). 실제 "모른다" 답 모양: "명시되어 있지 않습니다", "포함되어 있지 않습니다", "내용은 없습니다", "찾을 수 없습니다", "찾지 못했습니다" (정해 준 문장을 그대로 쓰지 않음).

```text
my-work/policy-qa.json 의 Build answer 에 검사를 더해 줘. 검사마다 {name, passed} 를 checks 에, 실패 이름을 failed 에.
- found_in_policies: "찾지 못했", "찾을 수 없", "포함되어 있지 않", "명시되어 있지 않", "언급이 없", "나와 있지 않", "내용은 없", "내용이 없" 이 없어야
- cites_excerpt: 인용 번호가 하나 이상
- grounded: 답 글(번호 뺀)의 두 글자 묶음 중 30% 이상이 발췌에 있어야
- numbers_from_policies: 답에 나온 숫자가 모두 발췌에 있어야 (질문에 나온 숫자는 되짚어도 됨 — 틀린 전제 "30일")
failed 가 있으면 route "담당자 연결", answer "규정에서 확실한 답을 찾지 못해 IT 담당자에게 전달했습니다.", draft 에 원래 답.
기준값에 걸린 길(Not in policies)도 checks [relevant 실패], failed ["relevant"] 로 같은 모양.
cases/lab02-challenge.json, cases/lab02.json 둘 다 통과. push · test까지.
```

- 결과: `lab02-challenge` **24/24** (`runs/lab02-challenge-20261023-110656.json`) · `lab02` 그대로 **18/18** (`runs/lab02-20261023-110721.json`), 모두 `--repeat 3`
- grounded 겹침: 근거 있는 답 0.66~0.83, 답이 없는 답 0.11~0.24 → 30% 선이 둘 사이에 넉넉. 한 번은 "명시되어 있지 않습니다. VPN …" 답이 0.49로 grounded를 넘었지만 found_in_policies가 잡음 (검사를 여러 개 두는 이유).

## Lab 03 예제 1 · 2 · 기준 재기와 한 가지씩 바꾸기

- 워크플로우는 고치지 않음. 색인 설정만 바꾸고 `--no-before`로 같은 24문항을 잼.
- 섹션 25청크 24 · 22 · 24 / 200자 17청크 23 · 21 · 23 / 400자 9청크 21 · 20 · 24 (doc@1 · answer@1 · answer@3). 섹션으로 되돌린 뒤 `lab03-threshold` 10/10.

## Lab 03 과제 · 어려운 질문으로 고치기

- `cases/my-cases.json` 12문항 → 고치기 전 27/36 (`runs/my-cases-20261023-111525.json`)

```text
my-work/search.json 을 고쳐 줘. 검색 전에 AI Agent "Rewrite query"(gpt-4.1-mini, Tool 없음)를 둔다.
지시: 직원 질문을 규정 문서의 낱말로 바꾼 짧은 한국어 검색어 한 줄. 예: 비번 → 비밀번호, 컴 → 컴퓨터, 폰 → 휴대폰,
깔다 → 설치, 그만두다 → 퇴사, 챗GPT·제미나이 → 생성형 AI 서비스. 질문에 없는 주제 · 낱말은 더하지 않는다. 숫자와 이름은 그대로.
검색 prompt 는 Rewrite query 의 output. 결과에 query 를 더한다. 나머지 계약은 그대로.
cases/my-cases.json 과 retrieval-doc · retrieval-answer · retrieval-answer3 를 모두 다시 잰다. push · test까지.
```

- 1차(낱말표만): 30/36 — 예시 낱말을 질문과 상관없이 끼워 넣음 ("카톡" → "생성형 AI 서비스 및 메신저")
- 2차("질문에 있는 낱말만"): 33/36 (`runs/my-cases-20261023-111944.json`)
- 3차(12낱말 이내 + 질문 전체 예 4개, 위 요청문): 33/36 (`runs/my-cases-20261023-112201.json`), retrieval doc · answer · answer3 24 · 24 · 24, answer@1 ×3 72/72
- 같은 곳 3번 → 멈춤. 남은 실패: "집에서 애들이랑 같이 쓰는 컴" → "개인용 컴퓨터"로 뜻이 바뀜.

## Lab 03 마무리

- 11/12로 마무리 (가족 컴 1개 새로 틀림은 기록만). `TEST-REPORT.md` 작성, 최종 회귀 모두 `--repeat 3` 통과.

## Lab 03 더 해 보기 · 겹침 (교안 3단계와 비교)

```text
my-work/index.json 의 Make chunks 에 선택 입력 overlap(앞 조각과 겹칠 글자 수, 기본 0)을 더해 줘.
chunking 이 숫자일 때만, 다음 조각 시작 = 앞 시작 + (size - overlap). 섹션 청크와 기본 동작은 그대로.
결과에 overlap 을 줄 때만 overlap 칸. 측정하는 동안만 검색은 다시 쓰기 전 판으로, 끝나면 되돌린다.
```

- 200+40 · 400+80이 교안 숫자(20청크 24 · 20 · 24, 12청크 22 · 22 · 24)와 틀린 질문까지 같음. 기본(겹침 0)은 바뀌지 않아 다른 테스트 그대로.
