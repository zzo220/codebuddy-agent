
import os, re, requests

def handler(event, context):
    # Bedrock Agent 파라미터 파싱
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}
    pr_url = params.get("pr_url", "")

    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        result = "Error: Invalid PR URL"
    else:
        owner, repo, pr_number = match.groups()
        headers = {
            "Authorization": f"token {os.environ.get('GITHUB_TOKEN', '')}",
            "Accept": "application/vnd.github.v3+json"
        }
        # PR 파일 목록 조회
        files_resp = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files",
            headers=headers
        )
        if files_resp.status_code != 200:
            result = f"Error: {files_resp.status_code}"
        else:
            files      = files_resp.json()
            additions  = sum(f.get("additions", 0) for f in files)
            deletions  = sum(f.get("deletions", 0) for f in files)
            total      = additions + deletions
            file_count = len(files)

            # 크기 기준 평가
            if total > 500:
                grade   = "🔴 대형 PR"
                advice  = "500줄 초과 — 기능별로 분리하여 여러 PR로 나누기를 강력 권장합니다."
            elif total > 200:
                grade   = "🟡 중형 PR"
                advice  = "200~500줄 — 가능하면 더 작은 단위로 분리하는 것을 권장합니다."
            else:
                grade   = "🟢 소형 PR"
                advice  = "200줄 이하 — 리뷰하기 적절한 크기입니다."

            result = (
                f"PR 크기 분석 결과: {grade}\n"
                f"추가: +{additions}줄 / 삭제: -{deletions}줄 / 합계: {total}줄\n"
                f"변경 파일: {file_count}개\n"
                f"권고사항: {advice}"
            )

    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup"),
            "function":    event.get("function"),
            "functionResponse": {"responseBody": {"TEXT": {"body": result}}}
        }
    }
