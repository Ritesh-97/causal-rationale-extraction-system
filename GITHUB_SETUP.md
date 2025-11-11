# GitHub Repository Setup Guide

## Repository Name
**Suggested:** `causal-rationale-extraction-system`

## Important: GitHub Authentication

⚠️ **GitHub no longer accepts passwords for authentication!** You must use a **Personal Access Token (PAT)**.

## Step 1: Create a Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `causal-rationale-repo`
4. Select expiration: Choose your preference (90 days recommended)
5. Select scopes: Check **`repo`** (this gives full repository access)
6. Click **"Generate token"**
7. **COPY THE TOKEN IMMEDIATELY** - you won't see it again!

## Step 2: Create Repository on GitHub

### Option A: Using GitHub Website
1. Go to: https://github.com/new
2. Repository name: `causal-rationale-extraction-system`
3. Description: `Causal Rationale Extraction and Synthesis System - Complete implementation for ObserveAI M5 Tech Meet 14`
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **"Create repository"**

### Option B: Using GitHub API (Automated)
Run this command (replace `YOUR_TOKEN` with your PAT):

```bash
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"causal-rationale-extraction-system","description":"Causal Rationale Extraction and Synthesis System - Complete implementation for ObserveAI M5 Tech Meet 14","private":false}'
```

## Step 3: Push Code to GitHub

After creating the repository, run these commands:

```bash
cd "/mnt/ritesh/7 th Semester/INTER_IIT_PREP"

# Add remote (replace YOUR_TOKEN with your Personal Access Token)
git remote add origin https://YOUR_TOKEN@github.com/Ritesh-97/causal-rationale-extraction-system.git

# Push to GitHub
git push -u origin main
```

**OR** use the automated script:

```bash
./scripts/push_to_github.sh
```

## Alternative: Using SSH (Recommended for Future)

For easier future pushes, set up SSH keys:

1. Generate SSH key:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. Add to GitHub:
   - Copy public key: `cat ~/.ssh/id_ed25519.pub`
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Paste and save

3. Update remote:
```bash
git remote set-url origin git@github.com:Ritesh-97/causal-rationale-extraction-system.git
```

## Quick Push Command

If you have your token ready, run:

```bash
cd "/mnt/ritesh/7 th Semester/INTER_IIT_PREP"
git remote add origin https://YOUR_TOKEN@github.com/Ritesh-97/causal-rationale-extraction-system.git
git push -u origin main
```

Replace `YOUR_TOKEN` with your Personal Access Token.

## Repository URL

Once pushed, your repository will be available at:
**https://github.com/Ritesh-97/causal-rationale-extraction-system**

