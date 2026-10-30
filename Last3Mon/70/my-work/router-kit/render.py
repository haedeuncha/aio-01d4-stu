# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""router-kit 렌더: 템플릿 폴더 + 값 파일 → 새 파일들.

  uv run my-work/router-kit/render.py <템플릿 폴더> <값.yaml> [-o 폴더]          # 만들기
  uv run my-work/router-kit/render.py <템플릿 폴더> <값.yaml> [-o 폴더] --check  # 만들지 않고, 이미 있는 파일과 같은지 비교
  … --no-n8n   # n8n에 이미 등록된 웹훅 경로인지 묻지 않기 (n8n이 꺼져 있을 때)
  … --search 폴더   # 이미 쓰는 웹훅 경로를 찾을 폴더 (기본: 결과 폴더 위의 my-work)

- 변수 표시는 `[[ 이름 ]]`. n8n 표현식 `{{ … }}`은 건드리지 않는다.
- JSON 파일은 **읽은 뒤** 글자 값 안의 표시만 바꾼다 → 값에 따옴표 · 줄바꿈이 있어도 JSON이 깨지지 않는다.
- `kind: json` · `kind: lanes` 변수는 JSON 글자로 넣는다 (Code 노드 안의 표).
- 값 검사: 필수 · 없는 변수 · 웹훅 경로 모양 · 이미 쓰는 경로 · 갈래 설정 표. ✘ 오류는 만들지 않고, ⚠ 경고는 알리고 만든다.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

MARK = re.compile(r"\[\[ (\w+) \]\]")
PATH = re.compile(r"^[a-z0-9][a-z0-9-]*$")
LANE_KEY = re.compile(r"^[a-z][a-z0-9_]*$")
N8N = "http://localhost:5678/webhook/"
SKIP = {"template.yaml", "README.md"}


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        sys.exit(f"✘ {path}: 이름: 값 모양의 YAML이어야 합니다")
    return data


def check_lanes(lanes: object, prompt: str) -> tuple[list[str], list[str]]:
    """갈래 설정 표 검사 → (오류, 경고)."""
    errors, warnings = [], []
    if not isinstance(lanes, dict) or not lanes:
        return ["'lanes'는 갈래가 하나 이상 있는 표여야 합니다 (예: policy: {agent: …, body: {…}})"], []
    for key, lane in lanes.items():
        where = f"lanes.{key}"
        if not LANE_KEY.fullmatch(str(key)) or key == "other":
            errors.append(f"{where}: 갈래 이름은 소문자로 시작하는 영문 · 숫자 · _ 이고 'other'는 쓸 수 없습니다")
        if not isinstance(lane, dict):
            errors.append(f"{where}: agent · body가 있는 표여야 합니다")
            continue
        agent = lane.get("agent")
        if not isinstance(agent, str) or not PATH.fullmatch(agent):
            errors.append(f"{where}.agent: 부를 Agent의 웹훅 경로가 필요합니다 (소문자 · 숫자 · '-', 받은 값: {agent!r})")
        body = lane.get("body")
        if not isinstance(body, dict) or not body:
            errors.append(f"{where}.body: Agent에 보낼 본문 표가 필요합니다 (예: {{question: text, user: user}})")
            body = {}
        fields = set()
        for name, spec in body.items():
            if not isinstance(spec, str) or not spec.strip():
                errors.append(f"{where}.body.{name}: 꺼낼 곳이 비었습니다 (user · text · 칸 이름 · a|b · body.칸 · '{{칸}} 글자')")
                continue
            if "{" in spec:
                if not re.search(r"\{\w+\}", spec) or spec.count("{") != spec.count("}"):
                    errors.append(f"{where}.body.{name}: '{spec}' 끼워 넣기 모양이 틀렸습니다 (예: '{{city}} 출장')")
                fields |= set(re.findall(r"\{(\w+)\}", spec))
                continue
            for part in spec.split("|"):
                if part.startswith("body."):
                    if not re.fullmatch(r"body\.\w+", part):
                        errors.append(f"{where}.body.{name}: '{part}' 웹훅 본문 칸 이름이 틀렸습니다")
                elif part not in ("user", "text"):
                    if not re.fullmatch(r"\w+", part):
                        errors.append(f"{where}.body.{name}: '{part}'은(는) 꺼낼 곳 이름이 아닙니다")
                    fields.add(part)
        required = lane.get("required", [])
        if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
            errors.append(f"{where}.required: 칸 이름 목록이어야 합니다 (예: [start])")
            required = []
        for item in required:
            if item not in fields:
                warnings.append(f"{where}.required: '{item}'은(는) body에서 쓰지 않는 칸입니다 (꼭 필요한데 Agent에 보내지 않음)")
        if required and not lane.get("ask"):
            warnings.append(f"{where}.ask: 빠진 칸을 물을 말이 없어 기본 문장을 씁니다")
        if prompt and key not in prompt:
            warnings.append(f"{where}: split_prompt에 '{key}'가 안 나옵니다 (LLM이 이 유형을 모르면 갈래가 쓰이지 않음)")
    return errors, warnings


def prepare(spec: dict, values: dict) -> tuple[dict[str, str], list[str], list[str]]:
    """변수마다 끼워 넣을 글자, 오류 목록, 경고 목록."""
    problems, warnings, texts = [], [], {}
    for var in spec.get("variables", []):
        name, kind = var["name"], var.get("kind", "text")
        value = values.get(name, var.get("default"))
        if value is None or value == "":
            if var.get("required"):
                problems.append(f"'{name}'이(가) 비었습니다 ({var.get('description', '').strip()[:40]})")
            value = "" if kind not in ("json", "lanes") else None
        elif kind == "path" and not PATH.fullmatch(str(value)):
            problems.append(f"'{name}' = {value!r}: 웹훅 경로는 소문자 · 숫자 · '-'만 씁니다 (빈칸 · 대문자 · 한글 안 됨)")
        elif kind == "lanes":
            errors, notes = check_lanes(value, str(values.get("split_prompt", "")))
            problems += errors
            warnings += notes
        if kind in ("json", "lanes"):
            texts[name] = json.dumps(value, ensure_ascii=False, indent=2)
        else:
            texts[name] = str(value)
    unknown = sorted(set(values) - {var["name"] for var in spec.get("variables", [])})
    if unknown:
        problems.append(f"template.yaml에 없는 변수: {', '.join(unknown)}")
    return texts, problems, warnings


def webhook_paths(path: Path) -> set[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    nodes = data.get("nodes", []) if isinstance(data, dict) else []
    return {str(node.get("parameters", {}).get("path", "")).strip("/") for node in nodes
            if isinstance(node, dict) and node.get("type") == "n8n-nodes-base.webhook"}


def search_root(out: Path) -> Path:
    """이미 쓰는 경로를 찾을 곳: 결과 폴더 위의 my-work (없으면 결과 폴더)."""
    for folder in [out.resolve(), *out.resolve().parents]:
        if folder.name == "my-work":
            return folder
    return out.resolve()


def in_n8n(path: str) -> bool | None:
    """n8n에 이 경로의 웹훅이 등록돼 있나 (n8n이 꺼져 있으면 None)."""
    try:
        with urllib.request.urlopen(N8N + path, timeout=3) as response:
            text = response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        text = error.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError):
        return None
    return "not registered for" in text  # POST로 등록된 웹훅은 GET에 이렇게 답한다


def path_conflicts(files: dict[Path, str], out: Path, ask_n8n: bool, search: Path | None = None) -> list[str]:
    problems = []
    for relative, text in files.items():
        if relative.suffix != ".json":
            continue
        try:
            mine = {str(node.get("parameters", {}).get("path", "")).strip("/") for node in json.loads(text).get("nodes", [])
                    if node.get("type") == "n8n-nodes-base.webhook"}
        except (ValueError, AttributeError):
            continue
        target = (out / relative).resolve()
        for other in (search or search_root(out)).rglob("*.json"):
            if other.resolve() == target or "templates" in other.parts:
                continue
            for path in mine & webhook_paths(other):
                problems.append(f"웹훅 경로 '{path}'은(는) 이미 {other} 가 씁니다")
        if ask_n8n and not target.exists():
            for path in mine:
                if in_n8n(path):
                    problems.append(f"웹훅 경로 '{path}'은(는) n8n에 이미 등록돼 있습니다 (다른 워크플로우가 막힐 수 있음)")
    return problems


def fill(text: str, texts: dict[str, str], missing: set[str]) -> str:
    def swap(match: re.Match) -> str:
        if match.group(1) not in texts:
            missing.add(match.group(1))
            return match.group(0)
        return texts[match.group(1)]
    return MARK.sub(swap, text)


def fill_json(value: object, texts: dict[str, str], missing: set[str]) -> object:
    if isinstance(value, str):
        return fill(value, texts, missing)
    if isinstance(value, list):
        return [fill_json(item, texts, missing) for item in value]
    if isinstance(value, dict):
        return {fill(key, texts, missing): fill_json(item, texts, missing) for key, item in value.items()}
    return value


def render(template: Path, texts: dict[str, str]) -> tuple[dict[Path, str], set[str]]:
    """템플릿 폴더 안 파일마다 (결과 상대 경로 → 내용)."""
    out, missing = {}, set()
    for source in sorted(template.rglob("*")):
        if not source.is_file() or source.name in SKIP:
            continue
        relative = Path(fill(str(source.relative_to(template)), texts, missing))
        text = source.read_text(encoding="utf-8")
        if source.suffix == ".json":
            text = json.dumps(fill_json(json.loads(text), texts, missing), ensure_ascii=False, indent=2) + "\n"
        else:
            text = fill(text, texts, missing)
        out[relative] = text
    return out, missing


def differences(a: object, b: object, where: str = "") -> list[str]:
    if type(a) is not type(b):
        return [f"{where or '(전체)'}: 모양이 다름"]
    if isinstance(a, dict):
        found = []
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                found.append(f"{where}.{key}: 한쪽에만 있음")
            else:
                found += differences(a[key], b[key], f"{where}.{key}")
        return found
    if isinstance(a, list):
        if len(a) != len(b):
            return [f"{where}: 개수 {len(a)} ↔ {len(b)}"]
        found = []
        for index, (x, y) in enumerate(zip(a, b)):
            label = x.get("name") if isinstance(x, dict) and "name" in x else index
            found += differences(x, y, f"{where}[{label}]")
        return found
    return [] if a == b else [f"{where}: 값이 다름"]


def main() -> int:
    parser = argparse.ArgumentParser(description="router-kit 템플릿 렌더")
    parser.add_argument("template", type=Path)
    parser.add_argument("values", type=Path)
    parser.add_argument("-o", "--out", type=Path, default=Path("."), help="만들 폴더 (기본: 지금 폴더)")
    parser.add_argument("--check", action="store_true", help="만들지 않고 이미 있는 파일과 비교")
    parser.add_argument("--no-n8n", action="store_true", help="n8n에 등록된 웹훅 경로를 묻지 않기")
    parser.add_argument("--search", type=Path, help="이미 쓰는 웹훅 경로를 찾을 폴더 (기본: 결과 폴더 위의 my-work)")
    args = parser.parse_args()

    spec = load_yaml(args.template / "template.yaml")
    texts, problems, warnings = prepare(spec, load_yaml(args.values))
    files, missing = render(args.template, texts)
    if missing:
        problems.append(f"값이 없는 표시: {', '.join('[[ ' + name + ' ]]' for name in sorted(missing))}")
    if not problems:
        problems += path_conflicts(files, args.out, not args.no_n8n, args.search)
    for warning in warnings:
        print(f"⚠ {warning}")
    if problems:
        for problem in problems:
            print(f"✘ {problem}")
        return 1

    if args.check:
        same = True
        for relative, text in files.items():
            target = args.out / relative
            if not target.exists():
                print(f"· {target}: 새로 생길 파일 (아직 없음)")
                continue
            old = target.read_text(encoding="utf-8")
            found = differences(json.loads(text), json.loads(old)) if target.suffix == ".json" else ([] if text == old else ["글자가 다름"])
            if found:
                same = False
                print(f"✘ {target}: 원본과 다른 곳 {len(found)}개")
                for line in found[:10]:
                    print(f"   {line}")
            else:
                print(f"✔ {target}: 원본과 같음")
        return 0 if same else 1

    for relative, text in files.items():
        target = args.out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        print(f"✔ {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
