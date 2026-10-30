# 68일차 n8n 실습 실행 보고서

워크플로: `split.json`, `assistant.json`, `supervisor.json`. 기존 두 Agent 파일은 수정하지 않았다.

## 실행 결과

| 실습 | 결과 | 요청·응답 보고서 |
| --- | --- | --- |
| Lab 01 업무 분리 | 21/21 | [JSON](../runs/lab01-20261020-114002.json) |
| Lab 01 담당·입력 과제 | 12/12 | [JSON](../runs/lab01-challenge-20261020-113955.json) |
| Lab 02 라우터 | 18/18 | [JSON](../runs/lab02-20261020-114505.json) |
| Lab 02 Supervisor 과제 | 15/15 | [JSON](../runs/lab02-challenge-20261020-114037.json) |
| Lab 03 입력 누락 | 15/15 | [JSON](../runs/lab03-20261020-114452.json) |
| Lab 03 장애 격리 | 3/3 | [JSON](../runs/lab03-down-20261020-114826.json) |
| Lab 03 경계 사례 과제 | 18/18 | [JSON](../runs/my-cases-20261020-114445.json) |

최종 버전의 위 테스트 합계: **102/102 통과**. 장애 격리는 1회, 나머지는 각 케이스를 3회 반복했다. `-v`로 각 요청·응답과 HTTP 코드를 출력했고 JSON 보고서에도 저장했다.

## 실패 재현과 수정

| 상황 | 수정 전 | 원인 | 수정 | 수정 후 |
| --- | --- | --- | --- | --- |
| 회의록 누락 | lab03 4/5, 해당 요청 500 | 회의록 Agent의 400 응답이 전체 중단으로 전파 | 호출 전 입력 검사, 입력 필요 결과로 취합 | lab03 15/15 |
| user 누락·공백 notes·혼합 요청 | my-cases 3/6 | 필수 입력 누락에도 호출 | Code에서 누락 입력 계산, Switch에서 분리 | my-cases 18/18 |
| Agent 게시 해제 | 복구 기능을 넣은 최종본으로 검증 | Agent 웹훅 404 | neverError·통신 오류 계속 진행·대체 답변 | lab03-down 3/3 |

수정 전 근거: [lab03](../runs/lab03-20261020-114016.json), [경계 사례](../runs/my-cases-20261020-114017.json). 기존 테스트 기대값은 변경하지 않았다.

## 추가 경계 사례

| 요청 | 업무 규칙 |
| --- | --- |
| 공백 message | 400, LLM 호출 전 거절 |
| message 누락 | 400, LLM 호출 전 거절 |
| IT인데 user 없음 | Agent 호출 없이 입력 필요 |
| notes가 공백 | Agent 호출 없이 회의록 요청 |
| 비밀번호 문의 + notes 없는 회의록 요청 | IT 답변 유지, 회의록만 입력 필요 |
| 이준호가 타인 소유 T-1002 조회 | 담당자 연결, 소유자 이름·상태 유출 금지 |

## 비교 실험과 한계

- 라우터용 테스트를 Supervisor에 적용한 결과는 [1/6](../runs/lab02-20261020-114334.json)이다. 라우터의 count/results 계약과 Supervisor의 reply/agents_used 계약이 달라 발생한 의도된 비교 결과다. Supervisor 전용 테스트는 15/15 통과했다.
- 직접 호출로 IT Agent 200, 회의록 Agent 200, notes 없는 회의록 Agent 400을 확인했다.
- 업무 분리 판단은 LLM이 하므로 표현이 달라질 수 있다. Agent 배정, 입력 누락, 결과 정렬, 실제 사용 Agent 기록은 코드와 노드로 처리한다.
- 지연 시간과 확장 검토는 [DESIGN.md](DESIGN.md)에 기록했다. 기능 테스트이며 21명 동시 부하 테스트는 실행하지 않았다.
- 별도 프로그램 제작 과제인 tflow는 이 n8n 실행 결과에 포함하지 않는다.

## 검증과 재실행

`check`: assistant·supervisor 오류 없음. split 오류 없음, 기존 설명 메모 5개에 연결 없음 경고.

```bash
uv run tools/flow.py push my-work/split.json my-work/assistant.json my-work/supervisor.json
uv run tools/flow.py test cases/lab02.json --repeat 3 -v
```

## 장애 테스트 후 복구 확인

회의록 Agent를 다시 게시했다. 복구 후 [lab02 6/6](../runs/lab02-20261020-114938.json), [lab03 15/15](../runs/lab03-20261020-114956.json)을 추가 확인했다. 위 102개 최종 버전 테스트와 복구 확인 21개를 합치면 123/123 통과다. 현재 회의록 Agent와 세 실습 워크플로 모두 게시되어 있다.

## Lab 02 라우터 최종 수정 확인

`assistant.json`을 최신 `split.json`의 분리 Agent·Code·모델 설정으로 갱신하고 `split.json` SHA-256이 유지됨을 확인했다. 업무 항목 생성, 한 줄 reply, 실제 HTTP 본문 매핑을 확인했다. 최종 게시 후 `lab02 --repeat 3`은 [18/18 통과](../runs/lab02-20261020-124247.json), `call my-assistant requests/composite.json`은 HTTP 200, 업무 3개로 5.2초였다.
