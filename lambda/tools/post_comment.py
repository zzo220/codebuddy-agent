import os, re, requests

def handler(event, context):
    params  = {p["name"]: p["value"] for p in event.get("parameters", [])}
    pr_url  = params.get("pr_url", "")
    comment = params.get("comment", "")

    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        result = f"Error: Invalid PR URL"
    else:
        owner, repo, pr_number = match.groups()
        resp = requests.post(
            f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments",
            headers={"Authorization": f"token {os.environ.get('GITHUB_TOKEN', '')}",
                     "Accept": "application/vnd.github.v3+json"},
            json={"body": comment}
        )
        result = f"✅ 댓글 등록: {resp.json().get('html_url', '')}" if resp.status_code == 201 else f"Error: {resp.status_code}"

    return {"messageVersion": "1.0", "response": {
        "actionGroup": event.get("actionGroup"), "function": event.get("function"),
        "functionResponse": {"responseBody": {"TEXT": {"body": result}}}
    }}
