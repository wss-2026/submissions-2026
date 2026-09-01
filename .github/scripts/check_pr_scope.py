#!/usr/bin/env python3
"""
자동 merge 전에 "이 PR이 제출 파일 정확히 1개만 추가/수정하는가"를 확인합니다.

여러 파일을 한꺼번에 건드리거나, 이미 있는 다른 사람의 제출 파일을 지우거나
덮어쓰는 PR은 형식 검증(validate_submission.py)만으로는 걸러지지 않으므로,
그런 PR은 자동 merge 대상에서 제외하고 사람이 직접 보게 합니다.

이 스크립트는 파일 "내용"을 실행하지 않고, GitHub PR files API가 돌려준
메타데이터(경로, 변경 종류)만 읽습니다 — 학생이 제출한 JSON 값 자체는
validate_submission.py가 이미 안전하게(읽기 전용으로) 검증합니다.

입력: GitHub `.../pulls/{number}/files` API 응답(JSON 배열, stdin)
종료 코드: 문제 없으면 0, 있으면 1 (+ ::error:: 메시지)
"""
import json
import re
import sys

SUBMISSION_PATH_RE = re.compile(r"^submissions/(week\d+|team)/[^/]+\.json$")


def main() -> int:
    try:
        files = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"::error::PR 파일 목록을 읽을 수 없습니다 ({e})")
        return 1

    if not isinstance(files, list) or len(files) != 1:
        n = len(files) if isinstance(files, list) else "?"
        print(f"::error::제출 PR은 파일을 1개만 바꿔야 합니다 (현재 {n}개) — 자동 merge하지 않고 사람이 확인해야 합니다.")
        return 1

    f = files[0]
    path = f.get("filename", "")
    status = f.get("status", "")

    if path.endswith("_example.json"):
        print(f"::error::_example.json은 제출 파일이 아닙니다: {path}")
        return 1

    if not SUBMISSION_PATH_RE.match(path):
        print(
            f"::error::제출 파일 경로 형식이 아닙니다: {path} "
            "(submissions/weekNN/학번.json 또는 submissions/team/팀이름.json 이어야 합니다)"
        )
        return 1

    if status not in ("added", "modified"):
        print(f"::error::파일을 삭제하거나 이름을 바꾸는 PR은 자동 merge하지 않습니다 (status={status}): {path}")
        return 1

    print(f"OK: {path} ({status})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
