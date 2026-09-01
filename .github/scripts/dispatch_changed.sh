#!/usr/bin/env bash
# main 브랜치에 새로 merge된 제출 파일을 찾아서, autograder 레포에
# repository_dispatch 이벤트를 보냅니다.
#
# 이 스크립트는 push 이벤트(= PR이 main에 merge된 뒤)에서만 실행되므로,
# 학생이 PR 안에서 이 파일 내용을 바꿔도 실행되는 버전은 항상 main의 것입니다.
set -euo pipefail

# TODO: 실제 autograder 레포 이름으로 바꾸세요 (예: wss-2026/autograder-2026)
AUTOGRADER_REPO="${AUTOGRADER_REPO:-wss-2026/autograder-2026}"

CHANGED=$(git diff --name-only HEAD~1 HEAD -- 'submissions/*/*.json' 2>/dev/null || true)

if [ -z "$CHANGED" ]; then
  echo "채점 대상으로 바뀐 제출 파일이 없습니다."
  exit 0
fi

for f in $CHANGED; do
  case "$f" in
    *_example.json) continue ;;
  esac
  [ -f "$f" ] || { echo "삭제된 파일 건너뜀: $f"; continue; }

  WEEK=$(basename "$(dirname "$f")")
  STUDENT_ID=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['student_id'])" "$f")
  REPO_URL=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['repo_url'])" "$f")
  COMMIT_SHA=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['commit_sha'])" "$f")
  DEPLOY_URL=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['deploy_url'])" "$f")

  echo "=> 채점 요청 전송: week=$WEEK student=$STUDENT_ID repo=$REPO_URL"

  gh api "repos/${AUTOGRADER_REPO}/dispatches" \
    -f event_type=new-submission \
    -f "client_payload[week]=${WEEK}" \
    -f "client_payload[student_id]=${STUDENT_ID}" \
    -f "client_payload[repo_url]=${REPO_URL}" \
    -f "client_payload[commit_sha]=${COMMIT_SHA}" \
    -f "client_payload[deploy_url]=${DEPLOY_URL}"
done
