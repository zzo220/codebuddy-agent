"""
CodeBuddy E2E 테스트
실행: python tests/test_e2e.py
"""
import boto3
import json
from botocore.config import Config

AGENT_ID  = "8IPCZBOQJ5"
ALIAS_ID  = "TSTALIASID"
REGION    = "ap-northeast-2"
TEST_PR   = "https://github.com/zzo220/codebuddy-test/pull/2"

def test_agent_basic():
    """Agent 기본 동작 확인"""
    config     = Config(read_timeout=120)
    bedrock_rt = boto3.client("bedrock-agent-runtime", region_name=REGION, config=config)

    resp = bedrock_rt.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=ALIAS_ID,
        sessionId="e2e-basic",
        inputText="안녕하세요. 무엇을 할 수 있나요?"
    )
    result = ""
    for chunk in resp["completion"]:
        if "chunk" in chunk:
            result += chunk["chunk"]["bytes"].decode()

    assert len(result) > 0, "Agent 응답이 비어있음"
    print(f"✅ test_agent_basic 통과: {result[:100]}")


def test_pr_review():
    """PR 리뷰 E2E 테스트"""
    config     = Config(read_timeout=300)
    bedrock_rt = boto3.client("bedrock-agent-runtime", region_name=REGION, config=config)

    resp = bedrock_rt.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=ALIAS_ID,
        sessionId="e2e-review",
        inputText=f"{TEST_PR} 이 PR을 리뷰해주세요"
    )
    result = ""
    for chunk in resp["completion"]:
        if "chunk" in chunk:
            result += chunk["chunk"]["bytes"].decode()

    assert "리뷰" in result or "분석" in result or "✅" in result, "리뷰 결과 없음"
    print(f"✅ test_pr_review 통과: {result[:200]}")


def test_edge_empty_input():
    """엣지 케이스: 빈 입력"""
    config     = Config(read_timeout=60)
    bedrock_rt = boto3.client("bedrock-agent-runtime", region_name=REGION, config=config)

    resp = bedrock_rt.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=ALIAS_ID,
        sessionId="e2e-empty",
        inputText="https://github.com/invalid/repo/pull/99999 리뷰해주세요"
    )
    result = ""
    for chunk in resp["completion"]:
        if "chunk" in chunk:
            result += chunk["chunk"]["bytes"].decode()

    assert len(result) > 0, "오류 처리 응답 없음"
    print(f"✅ test_edge_empty_input 통과: {result[:100]}")


if __name__ == "__main__":
    print("=== CodeBuddy E2E 테스트 시작 ===\n")
    test_agent_basic()
    test_pr_review()
    test_edge_empty_input()
    print("\n=== 모든 테스트 통과 ✅ ===")
