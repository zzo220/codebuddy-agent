from radon.complexity import cc_visit
from radon.metrics import mi_visit

def handler(event, context):
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}
    code   = params.get("code", "")

    try:
        cc      = cc_visit(code)
        mi      = mi_visit(code, multi=True)
        lines   = [f"Maintainability Index: {mi:.1f}/100"]
        for b in cc:
            warn = " ⚠️ 리팩토링 권장" if b.complexity > 10 else ""
            lines.append(f"  {b.name}: 복잡도 {b.complexity} ({b.letter}){warn}")
        result  = "\n".join(lines)
    except SyntaxError as e:
        result  = f"구문 오류: {e}"

    return {"messageVersion": "1.0", "response": {
        "actionGroup": event.get("actionGroup"), "function": event.get("function"),
        "functionResponse": {"responseBody": {"TEXT": {"body": result}}}
    }}
