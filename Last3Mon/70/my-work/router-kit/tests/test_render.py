"""render.py 값 검사 테스트 (7단계). 일부러 틀린 값 파일을 만들어 오류 · 경고를 확인한다.

  cd ~/aio-01d4-stu/Last3Mon/70
  uv run --with pytest --with pyyaml pytest my-work/router-kit/tests -q
"""
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parent.parent
TEMPLATE = KIT / "templates" / "n8n-router"
HR = yaml.safe_load((KIT / "values" / "hr.yaml").read_text(encoding="utf-8"))


def run(values: dict, out: Path, *extra: str, search: Path | None = None) -> subprocess.CompletedProcess:
    path = out / "values.yaml"
    path.write_text(yaml.safe_dump(values, allow_unicode=True, sort_keys=False), encoding="utf-8")
    args = [sys.executable, str(KIT / "render.py"), str(TEMPLATE), str(path), "-o", str(out / "result"),
            "--search", str(search or out / "result"), *extra]
    return subprocess.run(args, capture_output=True, text=True)


def new(**changes) -> dict:
    values = json.loads(json.dumps(HR))  # 깊은 복사
    values.update(path="rk-test", name="70-99 · 시험 라우터")
    values.update(changes)
    return values


def lanes(**changes) -> dict:
    table = json.loads(json.dumps(HR["lanes"]))
    for key, lane in changes.items():
        if lane is None:
            table.pop(key)
        else:
            table[key] = lane
    return table


# ---- 맞는 값
def test_hr_values_match_original():
    result = subprocess.run([sys.executable, str(KIT / "render.py"), str(TEMPLATE), str(KIT / "values" / "hr.yaml"),
                             "-o", str(KIT), "--check", "--no-n8n"], capture_output=True, text=True)
    assert result.returncode == 0 and "rk-hr.json: 원본과 같음" in result.stdout


def test_good_new_router_renders(tmp_path):
    result = run(new(), tmp_path, "--no-n8n")
    assert result.returncode == 0, result.stdout
    router = json.loads((tmp_path / "result" / "rk-test.json").read_text(encoding="utf-8"))
    assert router["name"] == "70-99 · 시험 라우터"
    assert (tmp_path / "result" / "cases" / "rk-test-basic.json").exists()


# ---- 웹훅 경로
@pytest.mark.parametrize("path", ["RK Trip", "rk_trip", "출장", "rk trip", "-rk"])
def test_bad_path_shape(tmp_path, path):
    result = run(new(path=path), tmp_path, "--no-n8n")
    assert result.returncode == 1 and "웹훅 경로는 소문자" in result.stdout
    assert not (tmp_path / "result").exists()  # 오류면 아무것도 만들지 않는다


def test_path_used_by_another_file(tmp_path):
    result = run(new(path="rk-hr"), tmp_path, "--no-n8n", search=KIT)
    assert result.returncode == 1 and "웹훅 경로 'rk-hr'은(는) 이미" in result.stdout and "rk-hr.json" in result.stdout


def n8n_up() -> bool:
    try:
        urllib.request.urlopen("http://localhost:5678/healthz", timeout=2)
        return True
    except OSError:
        return False


@pytest.mark.skipif(not n8n_up(), reason="n8n이 꺼져 있음")
def test_path_registered_in_n8n(tmp_path):
    result = run(new(path="rk-trip"), tmp_path)  # 파일 검색 폴더는 비어 있음 → n8n 등록만으로 걸려야 함
    assert result.returncode == 1 and "n8n에 이미 등록돼 있습니다" in result.stdout


# ---- 갈래 설정 표
def test_lane_without_agent(tmp_path):
    bad = new(lanes=lanes(policy={"body": {"question": "text"}, "required": []}))
    result = run(bad, tmp_path, "--no-n8n")
    assert result.returncode == 1 and "lanes.policy.agent" in result.stdout


def test_lane_bad_body_source(tmp_path):
    bad = new(lanes=lanes(policy={"agent": "a3-hr-policy", "body": {"question": "질문 칸", "title": "{city 출장"}, "required": []}))
    result = run(bad, tmp_path, "--no-n8n")
    assert result.returncode == 1
    assert "'질문 칸'은(는) 꺼낼 곳 이름이 아닙니다" in result.stdout and "끼워 넣기 모양이 틀렸습니다" in result.stdout


def test_lane_named_other_and_empty_table(tmp_path):
    result = run(new(lanes=lanes(other={"agent": "a3-hr-policy", "body": {"q": "text"}})), tmp_path, "--no-n8n")
    assert result.returncode == 1 and "'other'는 쓸 수 없습니다" in result.stdout
    result = run(new(lanes={}), tmp_path, "--no-n8n")
    assert result.returncode == 1 and "'lanes'" in result.stdout


def test_required_field_not_sent_is_warning_only(tmp_path):
    odd = new(lanes=lanes(leave={"agent": "a3-hr-leave", "body": {"user": "user"}, "required": ["start"]}))
    result = run(odd, tmp_path, "--no-n8n")
    assert result.returncode == 0  # 경고는 알리고 만든다
    assert "⚠ lanes.leave.required: 'start'은(는) body에서 쓰지 않는 칸" in result.stdout
    assert "⚠ lanes.leave.ask" in result.stdout


def test_lane_missing_from_prompt_is_warning(tmp_path):
    extra = new(lanes=lanes(equipment={"agent": "it-equipment", "body": {"user": "user", "item": "item"}, "required": []}))
    result = run(extra, tmp_path, "--no-n8n")
    assert result.returncode == 0 and "⚠ lanes.equipment: split_prompt에 'equipment'가 안 나옵니다" in result.stdout


# ---- 값 없음 · 이상한 글자
def test_missing_and_unknown(tmp_path):
    result = run({"name": "x", "path": "rk-x", "oops": 1}, tmp_path, "--no-n8n")
    assert result.returncode == 1
    assert "'split_prompt'이(가) 비었습니다" in result.stdout and "template.yaml에 없는 변수: oops" in result.stdout


def test_tricky_text_keeps_json_and_n8n_expressions(tmp_path):
    tricky = new(name='따옴표 "a" \\ 역슬래시', other_answer="줄1\n줄2 {{ 값일 뿐 }} [[ name ]]")
    assert run(tricky, tmp_path, "--no-n8n").returncode == 0
    router = json.loads((tmp_path / "result" / "rk-test.json").read_text(encoding="utf-8"))
    nodes = {node["name"]: node for node in router["nodes"]}
    assert router["name"] == '따옴표 "a" \\ 역슬래시'
    other = nodes["Other result"]["parameters"]["assignments"]["assignments"]
    assert any(row["value"] == "줄1\n줄2 {{ 값일 뿐 }} [[ name ]]" for row in other)  # 값 안의 [[ ]]는 다시 바뀌지 않음
    assert nodes["Call agent"]["parameters"]["url"] == "=http://localhost:5678/webhook/{{ $json.agent }}"
