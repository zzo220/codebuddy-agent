import json, boto3

MODEL = "apac.anthropic.claude-3-5-sonnet-20241022-v2:0"

def handler(event, context):
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}
    code   = params.get("code", "")

    bedrock = boto3.client("bedrock-runtime", region_name="ap-northeast-2")
    resp    = bedrock.invoke_model(
        modelId=MODEL,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content":
                f"다음 Python 코드에 대한 pytest 단위 테스트 3-5개를 작성하세요:\n```python\n{code[:2000]}\n```\n테스트 코드만 출력하세요."
            }]
        })
    )
    result = json.loads(resp["body"].read())["content"][0]["text"]

    return {"messageVersion": "1.0", "response": {
        "actionGroup": event.get("actionGroup"), "function": event.get("function"),
        "functionResponse": {"responseBody": {"TEXT": {"body": result}}}
    }}
