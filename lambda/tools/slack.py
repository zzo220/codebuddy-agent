import os, requests

def handler(event, context):
    params  = {p["name"]: p["value"] for p in event.get("parameters", [])}
    message = params.get("message", "")
    pr_url  = params.get("pr_url", "")

    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook:
        result = "Slack webhook not configured (skipped)"
    else:
        resp   = requests.post(webhook, json={"text": f"🤖 *CodeBuddy 리뷰 완료*\nPR: {pr_url}\n\n{message[:500]}"})
        result = "✅ Slack 알림 전송 완료" if resp.status_code == 200 else f"Error: {resp.status_code}"

    return {"messageVersion": "1.0", "response": {
        "actionGroup": event.get("actionGroup"), "function": event.get("function"),
        "functionResponse": {"responseBody": {"TEXT": {"body": result}}}
    }}
