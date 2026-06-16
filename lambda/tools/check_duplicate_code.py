
import re, json
from collections import defaultdict

def normalize(line):
    """공백/변수명 제거 후 코드 패턴 추출"""
    line = re.sub(r'["\'].*?["\']|\d+', 'X', line.strip())
    line = re.sub(r'\b[a-z_][a-z0-9_]*\b', 'V', line)
    return line

def handler(event, context):
    # Bedrock Agent 파라미터 파싱
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}
    code   = params.get("code", "")

    if not code.strip():
        result = "Error: No code provided"
    else:
        lines      = code.split("\n")
        patterns   = defaultdict(list)
        duplicates = []

        # 3줄 이상 슬라이딩 윈도우로 패턴 검사
        for i in range(len(lines) - 2):
            window = tuple(normalize(l) for l in lines[i:i+3] if l.strip())
            if len(window) == 3 and not all(p in ("", "V", "X") for p in window):
                patterns[window].append(i + 1)

        # 중복 발견
        for pattern, line_nums in patterns.items():
            if len(line_nums) > 1:
                duplicates.append(f"  라인 {line_nums}: 유사 패턴 {len(line_nums)}회 반복")

        if duplicates:
            result = (
                f"🔁 중복 코드 패턴 감지: {len(duplicates)}건\n\n"
                + "\n".join(duplicates[:10])
                + "\n\n리팩토링: 공통 함수 추출 또는 유틸리티 모듈 분리를 권장합니다."
            )
        else:
            result = "✅ 중복 코드 패턴 없음 — 코드 재사용이 잘 되어 있습니다."

    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup"),
            "function":    event.get("function"),
            "functionResponse": {"responseBody": {"TEXT": {"body": result}}}
        }
    }
