# 테스트 보고서 · 사내 IT 규정 Q&A

- 이름: 차해든
- 날짜: 2026-10-23 (71일차)
- 사용한 CLI 에이전트: claude (Claude Code)
- 워크플로우 파일: `my-work/index.json`(`71-1 · 📚 규정 색인`, `my-index`), `my-work/search.json`(`71-2 · 🔎 규정 검색`, `my-search`), `my-work/policy-qa.json`(`71-3 · 💬 규정 Q&A`, `my-policy-qa`)
- 색인: 섹션 청크 25개 · `text-embedding-3-large` · 메모리 저장소 `my_policy_docs` · 기준값 `min_score` 0.33
- 측정 숫자와 정답표는 `RAG-EVAL.md`, 요청문은 `PROMPTS.md`

## 1. 내가 쓴 테스트 (`cases/my-cases.json`)

직원 말투 질문 12개. 답이 있는 문서를 규정 원문(`data-api/data/docs/`)에서 먼저 확인했고, 답이 없는 질문은 넣지 않았다. 기대는 모두 `hits.0.source`(1등 청크의 문서).

| 케이스 | 요청 | 기대 결과 (업무 규칙) |
| --- | --- | --- |
| 챗GPT 견적서 | 챗GPT에 거래처 견적서 붙여 넣고 요약시켜도 돼? | `software-usage` (3. 생성형 AI 서비스: 대외비 문서 입력 금지) |
| 제미나이 고객 명단 | 제미나이한테 고객 명단 정리 시켜도 되나요? | `software-usage` (고객 정보 입력 금지) |
| 비번 | 비번 계속 틀려서 못 들어가요 | `password-policy` (3. 로그인 실패와 잠금) |
| 폰 OTP | 폰 바꿨는데 인증번호 앱은 어떻게 옮겨요? | `password-policy` (4. 다단계 인증: OTP 다시 등록) |
| 카톡 설치 | 회사 컴에 카톡 깔아도 돼요? | `software-usage` (1. 설치와 승인) |
| 맥북 분실 | 맥북 지하철에 두고 내렸어요 ㅠㅠ | `device-issue-return` (2. 분실과 도난: 24시간 이내 신고) |
| 스벅 접속 | 스벅에서 회사 서버 들어가도 돼요? | `remote-work-vpn` (1. 접속 원칙: 공용 와이파이) |
| 가족 컴 | 집에서 애들이랑 같이 쓰는 컴으로 일해도 되나요? | `remote-work-vpn` (3. 재택근무 중 보안) |
| 내 폰 메일 | 내 폰으로 회사 메일 보려면 뭐 깔아야 돼? | `device-issue-return` (4. 개인 장비 사용: MDM) |
| 퇴사 장비 | 퇴사 전에 장비 언제까지 내야 돼요? | `device-issue-return` (3. 반납: 5영업일) |
| 개인정보 엑셀 | 손님 개인정보 든 엑셀 파일 협력사에 보내야 하는데요 | `email-and-documents` (2. 첨부 파일: 암호) |
| 줌 카메라 | 줌 회의 카메라 쓰고 싶은데 언제 말해야 돼요? | `meeting-room` (2. 장비: 30분 전) |

## 2. 실패와 고친 내용

| 실패한 케이스 | 처음 결과 (3번 중 통과) | 내가 생각한 원인 | 에이전트가 고친 곳 | 고친 뒤 (3번 중 통과) |
| --- | --- | --- | --- | --- |
| `lab02` 점심 메뉴 → 담당자 연결 | 0/3 (`자동 답변`, LLM은 "찾지 못했습니다") | 관련 없는 질문에도 가까운 청크 3개는 언제나 나옴 (`top_score` 0.20) | `policy-qa.json`: `Build context`에 `min_score`(기본 0.33)와 `relevant`, If `Relevant?`, LLM 없이 `Not in policies` | 3/3 |
| `lab02-challenge` 규정에 답이 없는 4개 (VPN 속도 · 노트북 사양 · 비밀번호 잊음 · 보안 교육) | 0/3씩 (전체 2/8) | 같은 주제 규정이 있어 점수(0.35~0.55)가 기준을 넘음. LLM은 "명시되어 있지 않습니다" 등 **정해 준 문장과 다른 말로** 모른다고 했는데 그대로 자동 답변 | `policy-qa.json` `Build answer`에 규칙 검사 4개 (`found_in_policies` · `cites_excerpt` · `grounded` 두 글자 30% · `numbers_from_policies`), 실패하면 `담당자 연결` + `draft` | 3/3씩 (전체 24/24) |
| `lab02-challenge` 근거 있는 답 · 검사 기록 | 0/3 (`failed` · `checks` 칸 없음) | 검사를 만들어야 생기는 칸 | 위 검사가 `checks`, `failed`를 늘 남김 (기준값 길도 `failed: ["relevant"]`) | 3/3 |
| `my-cases` 챗GPT · 제미나이 · 카톡 | 0/3씩 (전체 27/36) | 질문 낱말이 규정에 없음 (챗GPT → 규정은 "생성형 AI 서비스", 카톡 깔기 → "소프트웨어 설치"). 1등이 "고객" · "컴"이 들어 있는 다른 규정 | `search.json`: 검색 앞에 AI Agent `Rewrite query` (규정 낱말로 바꾼 검색어, 결과에 `query`) | 3/3씩 |
| `my-cases` 가족 컴 (**새로 틀림**) | 3/3 → 0/3 | 다시 쓰기가 "애들이랑 같이 쓰는 컴"을 "개인용 컴퓨터"로 바꿔 뜻이 달라짐 → 장비 규정이 1등 | 고치지 않음 (같은 지시문을 3번 고쳐 멈춤, 4절) | 0/3 |

`Rewrite query` 지시문을 고친 3번:

| 차례 | 바꾼 것 | `my-cases` |
| --- | --- | --- |
| 1 | 낱말표 예시만 | 30/36 (예시 낱말 "생성형 AI" · "첨부 파일"을 질문과 상관없이 끼워 넣음) |
| 2 | "질문에 있는 낱말만 바꿔라" | 33/36 (챗GPT가 남음) |
| 3 | 12낱말 이내 + 질문 전체 예 4개 | 33/36 (챗GPT는 맞고 가족 컴이 새로 틀림) |

## 3. 최종 결과 (2026-10-23 11:22~11:36, 섹션 색인)

| 테스트 파일 | 결과 | 보고서 |
| --- | --- | --- |
| `cases/lab01.json` (색인 · 검색) | Passed 18/18 (6 × 3) | `runs/lab01-20261023-113544.json` |
| `cases/lab01-challenge.json` (섹션 · `top_k`) | Passed 12/12 (4 × 3) | `runs/lab01-challenge-20261023-113604.json` |
| `cases/lab02.json` (답과 출처) | Passed 18/18 (6 × 3) | `runs/lab02-20261023-113353.json` |
| `cases/lab02-challenge.json` (답 검사) | Passed 24/24 (8 × 3) | `runs/lab02-challenge-20261023-113434.json` |
| `cases/retrieval-doc.json` (doc@1) | Passed 24/24 | `runs/retrieval-doc-20261023-112247.json` |
| `cases/retrieval-answer.json` (answer@1) | Passed 72/72 (24 × 3) | `runs/retrieval-answer-20261023-112628.json` |
| `cases/retrieval-answer3.json` (answer@3) | Passed 24/24 | `runs/retrieval-answer3-20261023-112400.json` |
| `cases/lab03-threshold.json` (기준값) | Passed 30/30 (10 × 3) | `runs/lab03-threshold-20261023-113514.json` |
| `cases/my-cases.json --repeat 3` | Passed 33/36 (12문항 중 11) | `runs/my-cases-20261023-112201.json` |

개선 전 · 후 (같은 섹션 색인):

| 측정 | 개선 전 | 개선 후 |
| --- | --- | --- |
| `my-cases` | 27/36 | 33/36 |
| doc@1 · answer@1 · answer@3 | 24 · 22 · 24 | 24 · 24 · 24 |
| 검색 한 번 평균 | 0.41초 | 1.58초 |

## 4. 남은 문제 · 배운 점

- **지시문(systemMessage)으로 고친 것과 규칙 노드(If·Code)로 고친 것 중 어느 쪽이 더 안정적이었나?** 규칙 쪽. 기준값(If)과 답 검사 4개(Code)는 처음 맞춘 뒤 3번 반복 · 다시 돌려도 결과가 같았다. LLM에게 "모르면 정확히 이 문장"이라고 지시한 것은 지켜지지 않았고(5가지 다른 말), 검색어 다시 쓰기 지시문은 3번 고쳐도 고칠 때마다 틀리는 질문이 바뀌었다.
- **기준값은 1등 점수만 본다**: 규정 질문 최저 0.464(노트북)와 "답이 없는" VPN 속도 0.463이 같아서 기준값을 올려도 못 거른다. 답이 없다는 판단은 답을 만든 뒤 검사로 해야 한다.
- **검사는 여러 개**: VPN 답 하나는 `grounded` 겹침이 0.49로 기준(0.3)을 넘었지만 `found_in_policies`가 잡았다.
- **청크는 문서 모양에 맞게**: 우리 규정은 섹션이 짧고 주제별로 나뉘어 있어 섹션 청크가 200자 · 400자보다 세 지표 모두 좋았다. 400자는 answer@3만 좋다 (청크가 커서 LLM에게 관련 없는 글이 많이 감).
- **다시 쓰기는 좋아진 것과 나빠진 것이 같이 온다**: 24문항 answer@1은 22 → 24로 올랐지만, 내 질문 하나("가족과 같이 쓰는 컴")는 뜻이 바뀌어 새로 틀렸다. 검색 시간도 약 4배.
- 남은 일 (하지 않음): 원래 질문과 다시 쓴 질문 **둘 다** 검색해 점수가 높은 쪽을 쓰면 다시 쓰기가 뜻을 바꿔도 원래 질문이 남는다. `policy-qa.json`은 자기 검색 노드를 따로 가지고 있어 이번 다시 쓰기가 들어가지 않았다 (Q&A에도 넣으려면 `my-search`를 HTTP로 부르게 바꾸는 것이 한 곳에서 고치는 길).
- 메모리 저장소는 push할 때마다 비워진다. 직접 `call`할 때는 먼저 `call my-index requests/index-section.json`.
