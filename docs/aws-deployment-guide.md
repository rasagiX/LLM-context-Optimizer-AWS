# AWS Deployment Guide for LLM Context Optimizer

This guide explains how to deploy both the **Frontend** and **Backend** of the **LLM Context Optimizer** using AWS services (**AWS Amplify** for Frontend and **AWS App Runner** for Backend).

> **LLM Provider:** This project uses **Google Gemini** (not Amazon Bedrock).
> You need a `GEMINI_API_KEY` from [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) — free, no billing required.

---

## Part 1: Backend Deployment (AWS App Runner)

AWS App Runner is a fully managed service for deploying containerized APIs directly from GitHub.

### Step 1: Log in to AWS Console

1. Open the [AWS Management Console](https://console.aws.amazon.com/).
2. Set region to `us-east-1` (North Virginia) in the top-right header.

### Step 2: Create App Runner Service

1. Search for **App Runner** and click **Create service**.
2. **Source Repository**:
   - Choose **Source code repository**.
   - Connect GitHub and select: `rasagiX/LLM-context-Optimizer-AWS`
   - Branch: `main`
   - Deployment trigger: **Automatic**
3. **Configure Build Settings**:
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r backend/requirements.txt -r ml/requirements.txt
     ```
   - **Start Command**:
     ```bash
     PYTHONPATH=backend:. python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
     ```
   - **Port**: `8000`

### Step 3: Configure Environment Variables

Under **Environment variables**, add:

| Variable | Value |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `LLM_MODEL` | `gemini-1.5-flash` (or `gemini-1.5-pro`) |
| `AWS_ENABLED` | `true` (enables DynamoDB, S3, CloudWatch) |
| `AWS_REGION` | `us-east-1` |
| `DYNAMODB_TABLE_NAME` | Your DynamoDB table name (or leave blank for in-memory) |
| `S3_BUCKET_NAME` | Your S3 bucket name (optional) |
| `EMBEDDER_BACKEND` | `local` (default) or `bedrock` for Titan Embeddings |

4. Click **Next**, review, and click **Create & Deploy**.
5. Once deployed (~3–5 mins), App Runner outputs a public URL like:
   `https://xxxxxx.us-east-1.awsapprunner.com`
6. Test the health endpoint:
   ```bash
   curl https://xxxxxx.us-east-1.awsapprunner.com/health
   ```

---

## Part 2: Frontend Deployment (AWS Amplify)

### Step 1: Open AWS Amplify Console

1. Search for **AWS Amplify** and click **Host an app**.

### Step 2: Connect GitHub Repository

1. Select **GitHub** and authorize Amplify.
2. Choose repo: `rasagiX/LLM-context-Optimizer-AWS`
3. Branch: `main`

### Step 3: Configure Build Settings

Since the frontend is in the `frontend/` subfolder, use this build config:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm install
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/.output/public
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
```

### Step 4: Add Environment Variable

Under **Advanced settings → Environment variables**, add:

| Variable | Value |
|---|---|
| `VITE_API_URL` | Your App Runner backend URL from Part 1 |

### Step 5: Save and Deploy

1. Click **Save and deploy**.
2. Amplify runs: **Provision → Build → Deploy → Verify**.
3. Once complete (~2 mins), your live URL will be:
   `https://main.xxxxxx.amplifyapp.com`

---

## Notes

- The embedder defaults to `local` (sentence-transformers, no AWS needed). Set `EMBEDDER_BACKEND=bedrock` to use Amazon Titan Embeddings V2 — requires `bedrock:InvokeModel` IAM permission on `amazon.titan-embed-text-v2:0`.
- DynamoDB, S3, and CloudWatch are all optional — the app falls back gracefully to in-memory/local logging when `AWS_ENABLED=false`.
- Never commit your `.env` file. Use App Runner / Amplify environment variable injection instead.
