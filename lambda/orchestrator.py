import json, boto3, os, hashlib, hmac
from botocore.config import Config

AGENT_ID = os.environ.get("AGENT_ID", "8IPCZBOQJ5")
ALIAS_ID = os.environ.get("ALIAS_ID", "TSTALIASID")
REGION   = "ap-northeast-2"

def handler(event, context):
    body_str = event.get("body", "") or ""
    try:
        body = json.loads(body_str)
    except Exception:
        return {"statusCode": 400, "body": "Invalid JSON"}

    # GitHub Webhook 서명 검증
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
    if secret:
        sig = (event.get("headers") or {}).get("x-hub-signature-256", "")
        expected = "sha256=" + hmac.new(secret.encode(), body_str.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return {"statusCode": 401, "body": "Signature mismatch"}

    # PR 이벤트만 처리
    action = body.get("action", "")
    pr_url = (body.get("pull_request") or {}).get("html_url", "")

    if not pr_url or action not in ("opened", "synchronize"):
        return {"statusCode": 200, "body": f"Skipped: {action}"}

    # Bedrock Agent 호출
    bedrock_rt = boto3.client("bedrock-agent-runtime", region_name=REGION,
                               config=Config(read_timeout=300))
    try:
        resp = bedrock_rt.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=ALIAS_ID,
            sessionId=f"webhook-{pr_url.split('/')[-1]}",
            inputText=f"{pr_url} 이 PR을 리뷰해주세요"
        )
        result = ""
        for chunk in resp["completion"]:
            if "chunk" in chunk:
                result += chunk["chunk"]["bytes"].decode()
        return {"statusCode": 200, "body": json.dumps({"status": "success", "message": result[:500]})}
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
