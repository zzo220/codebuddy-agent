# CodeBuddy 🤖 — AI GitHub PR 자동 리뷰 에이전트

Amazon Bedrock Agent 기반의 GitHub Pull Request 자동 코드 리뷰 시스템입니다.

## 주요 기능

- **PEP8 스타일 검사** — Knowledge Base 기반 Python 코딩 규칙 검토
- **OWASP 보안 취약점 탐지** — SQL Injection, 하드코딩 비밀번호, 안전하지 않은 역직렬화 등
- **코드 복잡도 분석** — Cyclomatic Complexity 측정 및 리팩토링 권장
- **단위 테스트 자동 생성** — pytest 기반 테스트 코드 제안
- **리팩토링 제안** — 코드 구조 개선 방안 제시
- **PR 댓글 자동 등록** — 분석 결과를 마크다운 형식으로 PR에 자동 게시
- **Slack 알림** — 리뷰 완료 시 Slack 채널 알림 전송

## 아키텍처
GitHub PR → API Gateway → Orchestrator Lambda → Bedrock Agent

↓

Knowledge Base (S3 Vectors)

Action Group (6 Lambda Tools)

↓

PR 댓글 등록 + Slack 알림

## 기술 스택

| 구성 요소 | 서비스 |
|-----------|--------|
| AI 에이전트 | Amazon Bedrock Agent |
| LLM | Claude Sonnet (global.anthropic.claude-sonnet-4-6) |
| Vector Store | Amazon S3 Vectors |
| 서버리스 | AWS Lambda (Python 3.12) |
| API | Amazon API Gateway |
| IaC | AWS CloudFormation |
| 리전 | ap-northeast-2 (서울) |

## 설치 방법

### 사전 준비

- AWS 계정 (ap-northeast-2)
- GitHub Personal Access Token (`repo` 권한)
- Google Colab

### 배포 순서

**1. Bedrock Agent 사전 준비** (AWS 콘솔)
- Bedrock → Model access → Anthropic Claude use case 제출
- IAM → CodeBuddyAgentRole 생성 (trust: bedrock.amazonaws.com, bedrock-agentcore.amazonaws.com)
- IAM → AmazonBedrockFullAccess + BedrockAgentCoreFullAccess 정책 연결

**2. CloudFormation 배포**
```bash
aws cloudformation deploy \
  --template-file cloudformation/template.yaml \
  --stack-name CodeBuddyStack \
  --parameter-overrides \
    AgentId=YOUR_AGENT_ID \
    AliasId=YOUR_ALIAS_ID \
    GitHubToken=YOUR_GITHUB_TOKEN \
    LambdaRoleArn=YOUR_LAMBDA_ROLE_ARN \
  --capabilities CAPABILITY_IAM \
  --region ap-northeast-2
```

**3. GitHub Webhook 설정**
- Repository → Settings → Webhooks → Add webhook
- Payload URL: CloudFormation Output의 WebhookUrl
- Content type: `application/json`
- Events: Pull requests

## 사용 방법

PR을 열면 CodeBuddy가 자동으로 리뷰 댓글을 등록합니다.

```bash
git checkout -b feature/my-feature
git add .
git commit -m "Add new feature"
git push origin feature/my-feature
gh pr create --title "Add feature" --body "Please review"
# → CodeBuddy가 자동으로 리뷰 시작
```

## 비용 분석 (ap-northeast-2 기준)

| 서비스 | 단가 | 월 100회 PR 기준 |
|--------|------|-----------------|
| Bedrock Claude | $3/1M 토큰 | ~$4.50 |
| Lambda | $0.0000167/GB-초 | ~$0.50 |
| API Gateway | $1/백만 호출 | ~$0.10 |
| S3 Vectors | ~$0.05/GB | ~$0.01 |
| **합계** | | **~$5.11/월** |

## Repository 구조
codebuddy-agent/

├── README.md

├── cloudformation/

│   └── template.yaml          # 1클릭 배포 템플릿

├── lambda/

│   ├── orchestrator.py        # Webhook 수신 + Agent 호출

│   └── tools/

│       ├── github_pr.py       # GitHub PR 코드 조회

│       ├── post_comment.py    # PR 댓글 등록

│       ├── slack.py           # Slack 알림

│       ├── complexity.py      # 코드 복잡도 분석

│       ├── testgen.py         # 단위 테스트 생성

│       └── refactor.py        # 리팩토링 제안

├── tests/

│   └── test_e2e.py            # E2E 테스트

└── docs/

└── api-spec.yaml          # API 명세서

## 라이선스

MIT
