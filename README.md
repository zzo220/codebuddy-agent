# CodeBuddy 🤖 — AI GitHub PR 자동 리뷰 에이전트

Amazon Bedrock Agent 기반의 GitHub Pull Request 자동 코드 리뷰 시스템입니다.

## 주요 기능

- **PEP8 스타일 검사** — Knowledge Base 기반 Python 코딩 규칙 검토
- **OWASP 보안 취약점 탐지** — SQL Injection, 하드코딩 비밀번호, 안전하지 않은 역직렬화 등
- **코드 복잡도 분석** — Cyclomatic Complexity 측정 및 리팩토링 권장
- **PR 크기 평가** — 추가/삭제 줄 수 측정 및 분리 권고
- **중복 코드 감지** — 슬라이딩 윈도우 패턴으로 중복 로직 탐지
- **단위 테스트 자동 생성** — pytest 기반 테스트 코드 제안
- **리팩토링 제안** — 코드 구조 개선 방안 제시
- **PR 댓글 자동 등록** — 분석 결과를 마크다운 형식으로 PR에 자동 게시
- **Slack 알림** — 리뷰 완료 시 Slack 채널 알림 전송

## 아키텍처
GitHub PR → API Gateway → Orchestrator Lambda → Bedrock Agent

↓

Knowledge Base (S3 Vectors)

Action Group (8 Lambda Tools)

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
- Slack Incoming Webhook URL
- Google Colab

### 배포 순서

**1. Bedrock Agent 사전 준비** (AWS 콘솔)
- Bedrock → Model catalog → Anthropic Claude use case 제출
- IAM → CodeBuddyAgentRole 생성
  - Trust: `bedrock.amazonaws.com`, `bedrock-agentcore.amazonaws.com`
  - 정책: `AmazonBedrockFullAccess`, `BedrockAgentCoreFullAccess`

**2. CloudFormation 배포**
```bash
aws cloudformation deploy \
  --template-file cloudformation/template.yaml \
  --stack-name CodeBuddyStack \
  --parameter-overrides \
    AgentId=YOUR_AGENT_ID \
    AliasId=YOUR_ALIAS_ID \
    GitHubToken=YOUR_GITHUB_TOKEN \
    SlackWebhookUrl=YOUR_SLACK_WEBHOOK \
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

## Lambda Tool 목록 (8개)

| Tool | 파일 | 기능 |
|------|------|------|
| `get_github_pr` | github_pr.py | GitHub PR 코드 변경사항 조회 |
| `post_pr_comment` | post_comment.py | PR 리뷰 댓글 등록 |
| `send_slack` | slack.py | Slack 알림 전송 |
| `analyze_complexity` | complexity.py | 코드 복잡도 측정 (radon) |
| `generate_unit_test` | testgen.py | pytest 단위 테스트 자동 생성 |
| `suggest_refactor` | refactor.py | 리팩토링 방안 제안 |
| `check_pr_size` | check_pr_size.py | PR 크기 측정 및 분리 권고 |
| `check_duplicate_code` | check_duplicate_code.py | 중복 코드 패턴 감지 (미션) |

## 테스트 리포트

### 실습 6: 엣지 케이스 테스트

| 케이스 | 결과 | 응답 시간 |
|--------|------|-----------|
| 잘못된 PR URL | ✅ 통과 | 7.1초 |
| 존재하지 않는 PR | ✅ 통과 | 8.8초 |
| URL 없는 입력 | ✅ 통과 | 3.5초 |

### 실습 7: 성능 측정

| 측정 | 값 |
|------|----|
| 1회 | 90.9초 |
| 2회 | 98.7초 |
| 3회 | 93.6초 |
| **평균** | **94.4초** |
| 성공률 | 3/3 (100%) |

> Agent가 8개 Tool + Knowledge Base를 순차 실행하는 특성상 정상 범위

## 비용 분석 (ap-northeast-2, 월 100회 PR 기준)

| 서비스 | 단가 | 월 비용 |
|--------|------|---------|
| Bedrock Claude Sonnet | $3/1M 토큰 | ~$4.50 |
| Lambda (8개 × 60초) | $0.0000167/GB-초 | ~$0.50 |
| API Gateway | $1/백만 호출 | ~$0.10 |
| S3 Vectors | ~$0.05/GB | ~$0.01 |
| CloudWatch Logs | $0.50/GB | ~$0.10 |
| **합계** | | **~$5.21/월** |

## Repository 구조
codebuddy-agent/

├── README.md

├── cloudformation/

│   └── template.yaml

├── lambda/

│   ├── orchestrator.py

│   └── tools/

│       ├── github_pr.py

│       ├── post_comment.py

│       ├── slack.py

│       ├── complexity.py

│       ├── testgen.py

│       ├── refactor.py

│       ├── check_pr_size.py

│       └── check_duplicate_code.py

├── tests/

│   └── test_e2e.py

└── docs/

└── api-spec.yaml

## 라이선스

MIT
