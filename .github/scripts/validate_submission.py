#!/usr/bin/env python3
"""
제출 파일(submissions/**/*.json) 형식을 검증합니다.
이 스크립트는 절대로 학생이 제출한 JSON의 값을 실행(eval/exec)하지 않습니다 —
오직 텍스트로 읽어서 형식만 확인합니다. (신뢰할 수 없는 입력을 다루는 원칙)
"""
import glob
import json
import re
import sys

REQUIRED_FIELDS = ["student_id", "repo_url", "commit_sha", "deploy_url"]
REPO_URL_RE = re.compile(r"^https://github\.com/[\w.-]+/[\w.-]+/?$")
SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")


def validate_file(path: str) -> list[str]:
    errors = []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"{path}: JSON 파싱 실패 ({e})"]

    if not isinstance(data, dict):
        return [f"{path}: 최상위 값은 객체({{...}})여야 합니다"]

    for field in REQUIRED_FIELDS:
        if not data.get(field):
            errors.append(f"{path}: 필수 필드 누락 또는 빈 값 - '{field}'")

    if data.get("repo_url") and not REPO_URL_RE.match(data["repo_url"]):
        errors.append(
            f"{path}: repo_url 형식이 올바르지 않습니다 "
            f"(예: https://github.com/user/repo) - 받은 값: {data.get('repo_url')}"
        )

    sha = data.get("commit_sha")
    if sha and not SHA_RE.match(sha):
        errors.append(
            f"{path}: commit_sha는 7~40자 사이의 16진수 커밋 해시여야 합니다 "
            f"(브랜치 이름 X) - 받은 값: {sha}"
        )
    if sha and len(sha) < 40:
        errors.append(
            f"{path}: commit_sha는 짧은 형태({sha})가 아니라 전체 40자 SHA를 권장합니다. "
            f"'git rev-parse HEAD'로 전체 값을 확인하세요."
        )

    deploy_url = data.get("deploy_url")
    if deploy_url and not deploy_url.startswith("https://"):
        errors.append(f"{path}: deploy_url은 https:// 로 시작해야 합니다")

    return errors


def main() -> int:
    files = [
        f
        for f in glob.glob("submissions/**/*.json", recursive=True)
        if not f.endswith("_example.json")
    ]
    if not files:
        print("검증할 제출 파일이 없습니다 (submissions/**/*.json).")
        return 0

    all_errors: list[str] = []
    for path in sorted(files):
        all_errors.extend(validate_file(path))

    if all_errors:
        print("::error::제출 파일 형식 오류가 있습니다:")
        for e in all_errors:
            print(f"::error::{e}")
        return 1

    print(f"검증 통과: {len(files)}개 제출 파일 모두 형식이 올바릅니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
