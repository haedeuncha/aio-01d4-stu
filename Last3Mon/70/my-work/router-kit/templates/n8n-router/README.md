# n8n-router 템플릿 (router-kit v1)

- `template.yaml`: 변수 목록 (이름 · 종류 · 필수 · 설명 · 예)
- `[[ path ]].json`: 라우터 워크플로우. 파일 이름의 `[[ path ]]`도 값으로 바뀐다
- `cases/[[ path ]]-basic.json`: 어느 라우터에나 맞는 기본 테스트 3개

변수 표시는 `[[ 이름 ]]`이고, n8n 표현식 `{{ $json … }}`은 그대로 둔다.
렌더는 JSON을 읽은 뒤 글자 값 안의 표시만 바꾼다. 그래서 따옴표 · 줄바꿈이 들어간 값도 JSON을 깨뜨리지 않는다.
`kind: json` 변수(`lanes`, `shared`)는 Code 노드 안에 JSON 글자로 들어간다.
