# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""auto3 과제에 질문하고 답을 읽기 좋게 보여 준다 (n8n을 몰라도 됨).

  uv run my-work/auto3/ask.py hr "연차 몇 개 남았어?" --user 박서연
  uv run my-work/auto3/ask.py trip "11월 12일부터 14일까지 부산 출장비 신청해 줘" --user 이준호
  uv run my-work/auto3/ask.py content "소개글 써 줘" --user 김민지 --product my-work/auto3/content/requests/product.json
  uv run my-work/auto3/ask.py hr                # 대화식: 질문을 계속 입력 (빈 줄이면 끝)
  uv run my-work/auto3/ask.py --examples        # 과제별 예시 문장
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

N8N = "http://localhost:5678/webhook/"
HERE = Path(__file__).resolve().parent
PROJECTS = {
    "hr": ("a3-hr", "인사(HR) 문의 창구", "박서연"),
    "trip": ("a3-trip", "출장 준비 비서", "이준호"),
    "content": ("a3-content", "마케팅 콘텐츠 제작", "김민지"),
}
EXAMPLES = {
    "hr": ["연차 몇 개 남았는지 알려 주고, 11월 6일 금요일에 연차 쓸게. 그리고 병가 쓰려면 진단서 필요해?",
           "11월 10일 오후 반차 쓸게요", "이준호 연차 몇 개 남았어?  (남의 연차 → 담당자 연결)", "휴가 쓸게요  (날짜 없음 → 입력 필요)"],
    "trip": ["11월 12일부터 14일까지 부산 출장 가. 숙소는 하루 얼마까지 돼? 출장비 신청하고 일정도 잡아 줘.",
             "11월 16일부터 17일까지 서울 출장비 신청해 줘", "11월 16일부터 26일까지 대구 출장비 신청해 줘  (10박 → 팀장 결재)"],
    "content": ["신제품 소개글 써 주고, 인스타랑 X용으로 줄여 줘. 11월 2일에 올리게 일정도 잡아 줘.  (--product 필요)",
                "이 글 인스타용으로 줄여 줘  (--text \"원문\" 필요)", "게시 일정 잡아 줘  (날짜 없음 → 입력 필요)"],
}
START_N8N = "cd ~/aio-01d4-stu/Last3Mon/65/n8n && docker compose start"


def post(hook: str, body: dict) -> tuple[int, object]:
    request = urllib.request.Request(N8N + hook, data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                     method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            status, raw = response.status, response.read()
    except urllib.error.HTTPError as error:
        status, raw = error.code, error.read()
    except (urllib.error.URLError, ConnectionError, TimeoutError):
        return 0, None
    text = raw.decode("utf-8", errors="replace")
    try:
        return status, json.loads(text) if text.strip() else {}
    except json.JSONDecodeError:
        return status, text


def explain_failure(project: str, status: int, payload: object) -> str:
    if status == 0:
        return f"n8n에 연결하지 못했어요. n8n이 켜져 있는지 확인해 주세요.\n   → {START_N8N}"
    text = json.dumps(payload, ensure_ascii=False)
    if status == 404 or "not registered" in text:
        return (f"이 과제의 워크플로우가 아직 n8n에 없어요. 먼저 올려 주세요.\n"
                f"   → uv run tools/flow.py push my-work/auto3/{project}/a3-*.json")
    if status == 400 and isinstance(payload, dict):
        return f"요청이 비었어요: {payload.get('error')}\n   예: {payload.get('hint', '')}"
    if status >= 500:
        return ("n8n 안에서 오류가 났어요. 브라우저 http://localhost:5678 → 워크플로우 → Executions 탭에서 빨간 노드를 확인해 주세요.\n"
                f"   (응답: {text[:200]})")
    return f"HTTP {status}: {text[:300]}"


def show(payload: dict) -> None:
    print(payload.get("reply") or "(reply 없음)")
    for result in payload.get("results") or []:
        detail = result.get("detail") or {}
        extra = {key: value for key, value in detail.items() if value not in (None, [], {}, "")}
        if extra.get("posts"):
            extra.pop("posts")  # 글은 reply에 이미 보임
        if extra:
            print(f"   └ {result.get('index')}번 자세히: {json.dumps(extra, ensure_ascii=False)[:300]}")


def ask(project: str, message: str, args: argparse.Namespace) -> int:
    hook, title, _ = PROJECTS[project]
    body: dict = {"message": message, "user": args.user}
    if args.product:
        path = Path(args.product)
        body["product"] = json.loads((path if path.exists() else HERE / project / "requests" / path).read_text(encoding="utf-8"))
    if args.text:
        body["text"] = args.text
    if args.channels:
        body["channels"] = args.channels.split(",")
    print(f"\n🙋 {args.user} → {title}: {message}")
    start = time.monotonic()
    status, payload = post(hook, body)
    seconds = time.monotonic() - start
    if status != 200 or not isinstance(payload, dict):
        print("⚠ " + explain_failure(project, status, payload))
        return 1
    print(f"🤖 ({seconds:.1f}초)")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        show(payload)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="auto3 과제(hr · trip · content)에 질문합니다.")
    parser.add_argument("project", nargs="?", choices=list(PROJECTS), help="hr · trip · content")
    parser.add_argument("message", nargs="?", help="직원 요청 문장 (없으면 대화식)")
    parser.add_argument("--user", help="요청한 사람 (기본: 과제마다 예시 직원)")
    parser.add_argument("--product", help="content: 제품 정보 JSON 파일 (예: product.json)")
    parser.add_argument("--text", help="content: SNS로 줄일 원문 글")
    parser.add_argument("--channels", help="content: instagram,x,linkedin")
    parser.add_argument("--json", action="store_true", help="응답 JSON 전체 보기")
    parser.add_argument("--examples", action="store_true", help="예시 문장 보기")
    args = parser.parse_args()

    if args.examples or not args.project:
        for key, (hook, title, user) in PROJECTS.items():
            print(f"\n[{key}] {title} (POST /webhook/{hook}, 예시 직원 {user})")
            for line in EXAMPLES[key]:
                print(f"  uv run my-work/auto3/ask.py {key} \"{line.split('  (')[0]}\"" + (f"   # {line.split('  (')[1][:-1]}" if "  (" in line else ""))
        print("\n직원: 박서연(연차 9일 남음) · 이준호(0.5일) · 김민지(17일)")
        return 0
    args.user = args.user or PROJECTS[args.project][2]
    if args.message:
        return ask(args.project, args.message, args)
    print(f"{PROJECTS[args.project][1]} · {args.user} 님으로 질문합니다. 빈 줄을 넣으면 끝나요.")
    while True:
        try:
            message = input("\n요청> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not message:
            break
        ask(args.project, message, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
