# Complete AWS Deployment Guide for TokenOpt

This guide explains how to deploy both the **Frontend** and **Backend** of the **LLM Context Optimizer** using 100% native AWS services (**AWS Amplify** for Frontend and **AWS App Runner** for Backend).

---

## Part 1: Backend Deployment (AWS App Runner)

AWS App Runner is a fully managed service that makes it easy to deploy containerized web applications and APIs directly from GitHub.

### Step 1: Log in to AWS Console
1. Open the [AWS Management Console](https://console.aws.amazon.com/).
2. Set region to `us-east-1` (North Virginia) in the top-right header.

### Step 2: Create App Runner Service
1. Search for **App Runner** in the AWS search bar and click **Create service**.
2. **Source Repository**:
   - Choose **Source code repository**.
   - Connect your GitHub account and select repository: `rasagiX/LLM-context-Optimizer-AWS`.
   - Branch: `main` (or `feature/ml-optimizer`).
   - Deployment trigger: Select **Automatic** (re-deploys on push).
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
Under **Environment variables**, add the following key-value pairs:

| Environment Variable | Value |
| :--- | :--- |
| `AWS_REGION` | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | `<YOUR_AWS_ACCESS_KEY_ID>` |
| `AWS_SECRET_ACCESS_KEY` | `<YOUR_AWS_SECRET_ACCESS_KEY>` |
| `AWS_ENABLED` | `True` |
| `BEDROCK_MODEL_ID` | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| `EMBEDDER_BACKEND` | `local` |

4. Click **Next**, review configuration, and click **Create & Deploy**.
5. Once deployed (approx 3-5 mins), AWS will output a public service URL (e.g. `https://xxxxxx.us-east-1.awsapprunner.com`).
6. Test your live backend URL in browser or terminal:
   ```bash
   curl https://xxxxxx.us-east-1.awsapprunner.com/health
   ```

---

## Part 2: Frontend Deployment (AWS Amplify)

AWS Amplify Hosting provides a git-based workflow for hosting modern web applications.

### Step 1: Open AWS Amplify Console
1. In the AWS Management Console search bar, type **AWS Amplify** and click on it.
2. Click **Host an app** (or **Create new app**).

### Step 2: Connect GitHub Repository
1. Select **GitHub** as the source code provider and click **Continue**.
2. Authorize AWS Amplify and choose your repository: `rasagiX/LLM-context-Optimizer-AWS`.
3. Select branch: `main` (or `feature/ml-optimizer`).

### Step 3: Configure Build Settings
Amplify auto-detects Vite/TanStack settings. Ensure build settings are as follows:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: dist
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

### Step 4: Save and Deploy
1. Click **Save and deploy**.
2. AWS Amplify will execute 4 stages: **Provision**, **Build**, **Deploy**, and **Verify**.
3. Once completed (approx 2 mins), Amplify will provide your live SSL domain URL (e.g., `https://main.xxxxxx.amplifyapp.com`).
