# AWS Infrastructure & Setup Guide

This document outlines the AWS setup, IAM permissions, environment configuration, and local testing modes for the **AI Context Compiler**.

---

## ⚙️ Environment Configuration

Create a `.env` file in the `backend/` directory or project root with the following keys:

```bash
# Set AWS_ENABLED=true when AWS credentials are configured
AWS_ENABLED=true

AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Amazon Bedrock LLM Model ID
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# ML Embedding Backend (local or bedrock)
EMBEDDER_BACKEND=local

# AWS Resource Names
S3_BUCKET_NAME=ai-context-compiler-artifacts
CLOUDWATCH_LOG_GROUP=/aws/fastapi/ai-context-compiler
```

---

## 🔒 Required IAM Permissions

The AWS credentials or IAM Role used by the backend require the following permissions:

### 1. Amazon Bedrock Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:Converse"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
        "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
      ]
    }
  ]
}
```

### 2. Amazon S3 Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::ai-context-compiler-artifacts",
        "arn:aws:s3:::ai-context-compiler-artifacts/*"
      ]
    }
  ]
}
```

### 3. Amazon CloudWatch Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 🛠️ Local Mock Mode (`AWS_ENABLED=false`)

When `AWS_ENABLED=false` is set in `.env`:
- Bedrock API calls return realistic simulated responses and quality scores.
- S3 calls use in-memory store.
- CloudWatch metric calls log metrics locally.
- **Zero AWS account or internet credentials are required to test or develop!**
