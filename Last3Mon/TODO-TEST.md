# TODO 테스트 목록

과정 70에서 만든 공지 키트·규칙 검사 모듈·SMS·라우터를 실제 업무에 적용할 때 사용할 테스트 목록이다. 먼저 통과해야 할 정상·경계 테스트를 확인하고, 그 다음 실패를 재현하거나 보완할 테스트를 진행한다.

## 잘되는 테스트 10가지

- [ ] **점검 공지 정상 작성**: `maintenance`와 날짜·시간이 있으면 HTTP 200, `[점검 안내]`, `published: true`
- [ ] **보안 공지 필수 문장**: `IT팀은 절대 비밀번호를 묻지 않습니다.`가 공지에 포함됨
- [ ] **교육 공지 필수 문장**: `신청은 IT 포털에서 할 수 있습니다.`가 공지에 포함됨
- [ ] **설문 공지 추가 종류**: `survey`가 설정 표 한 줄로 처리되고 익명 문장이 포함됨
- [ ] **없는 공지 종류 차단**: `party` 입력이 HTTP 400과 `kinds` 목록을 반환함
- [ ] **규칙 모듈 정상 초안**: `modRuleCheck01`이 `{passed: true, codes: [], issues: []}`를 반환함
- [ ] **사내 링크 허용**: `intra.example.com` 링크가 `external_link` 없이 통과함
- [ ] **SMS 재사용 검사**: SMS가 같은 규칙 모듈을 사용하고 80자 이내 결과를 반환함
- [ ] **v2 경고 분리**: `too_long`은 v2의 `warnings`에만 들어가고 `passed`는 true임
- [ ] **복합 라우터 결과 보존**: IT·회의록·기타 업무 결과가 index 순서로 모두 모이고 reply가 생성됨

## 잘 안되는 테스트 10가지

- [ ] **사실 공백만 입력**: `facts: "   "`인데 HTTP 200으로 게시되는지 확인한다. 400이어야 한다.
- [ ] **필수 날짜·시간 누락**: 사실에 시간은 있는데 초안에 빠진 경우 `missing_fact`가 나와야 한다.
- [ ] **개인정보 포함**: 전화번호나 이메일이 공지·SMS에 남으면 `personal_info`로 차단되어야 한다.
- [ ] **외부 링크 포함**: `bit.ly` 같은 허용되지 않은 링크가 `external_link`로 차단되어야 한다.
- [ ] **허용 도메인 예외 누락**: `allowed_domains: ["bit.ly"]`를 줬는데도 링크가 차단되는지 확인한다.
- [ ] **필수 문장 누락**: Agent가 보안·교육·설문 필수 문장을 빼면 `missing_phrase`가 나와야 한다.
- [ ] **SMS 길이 초과**: 80자를 넘긴 문자가 `published: true`로 전송되지 않아야 한다.
- [ ] **모듈 ID 불일치**: 호출 노드가 존재하지 않는 workflow ID를 사용하면 게시 전에 발견되어야 한다.
- [ ] **Agent 장애 격리 실패**: 회의록 Agent가 404여도 IT 업무 결과까지 사라지면 안 된다.
- [ ] **계약 필드 삭제**: v2 전환 뒤 `codes`가 사라져 기존 키트 테스트가 깨지는지 확인하고, 기존 필드를 유지해야 한다.

## 실행 순서

```bash
cd ~/aio-01d4-stu/Last3Mon/70
uv run tools/flow.py check my-work/notice-kit.json
uv run tools/flow.py test cases/lab01.json --repeat 3
uv run tools/flow.py test cases/lab02-module.json --repeat 3
uv run tools/flow.py test cases/lab03-v2.json --repeat 3
```

실패하면 `runs/*.json`에서 요청과 응답을 확인하고, 기대 결과를 바꾸지 않은 채 설정 표·모듈·라우터 중 한 곳만 고친다.
