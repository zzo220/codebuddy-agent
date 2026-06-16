
import os, requests

def handler(event, context):
    # Bedrock Agent 파라미터 파싱
    params  = {p["name"]: p["value"] for p in event.get("parameters", [])}
    message = params.get("message", "")
    pr_url  = params.get("pr_url", "")

    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook:
        result = "Slack webhook not configured (skipped)"
    else:
        # Slack 메시지 전송
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "🤖 CodeBuddy 리뷰 완료"}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*PR:* {pr_url}"}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": message[:500]}
                }
            ]
        }
        resp   = requests.post(webhook, json=payload)
        result = "✅ Slack 알림 전송 완료" if resp.status_code == 200 else f"Error: {resp.status_code}"

    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup"),
            "function":    event.get("function"),
            "functionResponse": {"responseBody": {"TEXT": {"body": result}}}
        }
    }
