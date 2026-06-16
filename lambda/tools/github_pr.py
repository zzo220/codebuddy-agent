import os, re, requests

def handler(event, context):
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}
    pr_url = params.get("pr_url", "")

    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        result = f"Error: Invalid PR URL: {pr_url}"
    else:
        owner, repo, pr_number = match.groups()
        headers = {
            "Authorization": f"token {os.environ.get('GITHUB_TOKEN', '')}",
            "Accept": "application/vnd.github.v3+json"
        }
        pr_resp = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
            headers=headers
        )
        if pr_resp.status_code != 200:
            result = f"GitHub API Error: {pr_resp.status_code}"
        else:
            pr_data  = pr_resp.json()
            files    = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files",
                headers=headers
            ).json()
            py_files = [f for f in files if f["filename"].endswith(".py")]
            patches  = [f"File: {f['filename']}\n{f.get('patch', '')[:2000]}" for f in py_files[:5]]
            result   = (
                f"PR: {pr_data['title']}\nAuthor: {pr_data['user']['login']}\n"
                f"Files: {len(files)} ({len(py_files)} Python)\n\n"
                + "\n\n".join(patches)
            )

    return {"messageVersion": "1.0", "response": {
        "actionGroup": event.get("actionGroup"), "function": event.get("function"),
        "functionResponse": {"responseBody": {"TEXT": {"body": result}}}
    }}
