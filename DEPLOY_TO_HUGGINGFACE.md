# Deploy AGI Model to Hugging Face Spaces

## 🎯 Overview

This guide walks you through deploying the AGI Model to Hugging Face Spaces as an interactive Docker-based demo.

## 📋 Prerequisites

- Hugging Face account: https://huggingface.co/join
- GitHub account (already set up)
- Hugging Face API token

## 🚀 Quick Start

### Option A: Automated Deployment (GitHub Actions) - RECOMMENDED

This is the easiest method - fully automated deployment on every push to `main`.

**Steps:**
1. Create Hugging Face Space (see Step 1 below)
2. Configure GitHub Secrets (see Step 3 below)
3. Push to GitHub → Automatic deployment!

### Option B: Manual Deployment (Hugging Face CLI)

For advanced users who want direct control via CLI.

**Prerequisites:**
```bash
# Install hf CLI
pip install -U "huggingface_hub[cli]"

# Login to Hugging Face
hf login

# Add CLI skill for AI agents (optional but recommended)
hf skills add --global
```

**Deploy Commands:**
```bash
# Create Space (one-time setup)
hf repos create Quantum927/agi-model --repo-type space --space-sdk docker --public --exist-ok

# Deploy Space files
cd hf-deploy
hf upload spaces/Quantum927/agi-model . .

# Check Space status
hf spaces info Quantum927/agi-model
```

### Step 1: Create Hugging Face Space

**Via Web Interface:**
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Configure:
   - **Space name**: `agi-model`
   - **License**: MIT
   - **SDK**: Docker
   - **Visibility**: Public
4. Click "Create Space"

**Via CLI (Alternative):**
```bash
hf repos create Quantum927/agi-model --repo-type space --space-sdk docker --public --exist-ok
```

### Step 2: Get Hugging Face Token

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: `AGI-Model-Deploy`
4. Role: `Write`
5. Click "Generate token"
6. **Save the token** (you won't see it again!)

### Step 3: Configure GitHub Secrets

1. Go to your GitHub repository: https://github.com/quantumdynamics927-dotcom/AGI-model
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add these secrets:

```
Name: HF_TOKEN
Value: [your Hugging Face token from Step 2]

Name: HF_USER
Value: [your Hugging Face username]
```

### Step 4: Enable GitHub Actions

1. Go to Actions tab in GitHub
2. Enable workflows if prompted
3. The workflow will automatically trigger on next push

### Step 5: Manual Deploy (Optional)

**Option 5A: Via Git (Traditional)**

If you want to deploy immediately (workflow does this automatically):

```bash
# Clone your Hugging Face Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/agi-model
cd agi-model

# Copy ONLY Space files from AGI-model repo
cp /path/to/AGI-model/space_app.py .
cp /path/to/AGI-model/Dockerfile.space ./Dockerfile
cp /path/to/AGI-model/README_HF_SPACE.md ./README.md
cp /path/to/AGI-model/requirements.txt .

# Create .gitignore
cat > .gitignore << 'EOF'
*.pyc
__pycache__/
*.py[cod]
.env
*.log
EOF

# Push to Space
git add .
git commit -m "Initial deployment: AGI Model v0.98.0-rc"
git push
```

**Option 5B: Via hf CLI (Recommended for Agents)**

For AI agents and automated workflows:

```bash
# Ensure you're logged in
hf login

# Deploy directly from hf-deploy directory
cd hf-deploy
hf upload spaces/YOUR_USERNAME/agi-model . . \
    --commit-message "Deploy AGI Model Space"

# Check Space status
hf spaces info YOUR_USERNAME/agi-model
```

**Note**: The GitHub Actions workflow automatically handles this deployment on every push to `main`!

## 📊 What Gets Deployed

### Files Included (Space-Only)
- ✅ `space_app.py` - Gradio interface (renamed from HF deployment)
- ✅ `Dockerfile.space` → `Dockerfile` - Space-specific container config
- ✅ `README_HF_SPACE.md` → `README.md` - Space front matter and docs
- ✅ `requirements.txt` - Python dependencies
- ✅ `.gitignore` - Space-specific ignores

### Files Excluded (Keep on GitHub)
- ❌ Full research codebase
- ❌ Test suites
- ❌ Documentation files (USER_MANUAL.md, etc.)
- ❌ Large artifacts
- ❌ Internal project files

### Features Available
- 🔬 **Discovery Validator**: Interactive certification demo
- 🚀 **Pipeline Demo**: 8-stage workflow visualization
- 📊 **Metrics Calculator**: Consciousness metrics tool
- ℹ️ **System Status**: Live platform information

## 🔧 Configuration

### Dockerfile Settings (Space-Optimized)

The `Dockerfile.space` is configured for:
- **Base Image**: python:3.10-slim
- **Port**: 7860 (Gradio standard)
- **Health Check**: Every 30 seconds
- **Server Binding**: 0.0.0.0 (required for Space proxy)
- **Startup**: `python space_app.py`

**Critical Settings**:
```dockerfile
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT=7860
CMD ["python", "space_app.py"]
```

### Space Metadata (README.md Front Matter)

The `README.md` on the Space must include:

```yaml
---
title: AGI Model - Scientific Discovery Validator
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---
```

**Important**: This YAML front matter MUST be in the root `README.md` of the Space repository, not in a separate file.

## 🎨 Customization

### Add Your Logo

1. Add `logo.png` to repository root
2. Update `space_app.py` to display it:

```python
gr.Image("logo.png", width=200)
```

### Customize Demo Workflows

Edit `space_app.py` to add your own demos:

```python
def custom_demo():
    # Your custom logic here
    return result
```

### Add More Tabs

```python
with gr.TabItem("🔬 Custom Demo"):
    # Your custom interface
    pass
```

## 📈 Monitoring

### Check Deployment Status

1. Go to your Space: https://huggingface.co/spaces/YOUR_USERNAME/agi-model
2. Click "Files" → See latest commit
3. Click "Logs" → View build logs
4. Optional CLI check: `hf spaces info YOUR_USERNAME/agi-model`

### Troubleshooting

**Build Fails**:
- Check logs for dependency errors
- Verify Dockerfile syntax
- Ensure all files are present

**App Won't Start**:
- Check `space_app.py` for syntax errors
- Verify port is 7860
- Check memory limits (Space has limits)

**GitHub Actions Fail**:
- Verify HF_TOKEN secret is set
- Check HF_USER matches your username
- Ensure Space exists on Hugging Face

## 🎯 Best Practices

### Security
- ✅ Never commit HF_TOKEN to repository
- ✅ Use GitHub Secrets for all credentials
- ✅ Keep Dockerfile minimal and secure
- ✅ Run as non-root user

### Performance
- ✅ Use Docker layer caching
- ✅ Install only required dependencies
- ✅ Keep demo lightweight
- ✅ Mock heavy computations if needed

### User Experience
- ✅ Provide clear instructions
- ✅ Show progress indicators
- ✅ Handle errors gracefully
- ✅ Link to full documentation

## 📊 Usage Analytics

Hugging Face provides:
- **Space visits**: View count
- **App interactions**: Usage metrics
- **Build history**: Deployment logs

Access via: Space → Settings → Analytics

## 🔄 Sync Strategy

### Automatic Sync (Recommended)
- GitHub Actions triggers on every push to `main`
- Space stays in sync with repository
- Zero manual intervention

### Manual Sync
- Deploy when ready for public demo
- Control what gets published
- Test locally first

## 🎊 Success Indicators

✅ Space builds successfully  
✅ App loads without errors  
✅ Demo workflows execute  
✅ System status displays correctly  
✅ Links to GitHub work  

## 🤖 AI Agent Integration

### Hugging Face CLI Skill for Agents

The `hf` CLI provides powerful tools for AI agents to interact with Hugging Face:

**Install CLI Skill:**
```bash
# Global installation (all projects)
hf skills add --global

# Claude Code specific
hf skills add --claude --global

# Project-specific only
hf skills add
```

**Agent Capabilities:**
- 🔍 **Search Models**: Find and evaluate models
- 📊 **Manage Datasets**: Upload/download training data
- 🚀 **Launch Spaces**: Deploy and manage Spaces programmatically
- 💼 **Run Jobs**: Execute compute jobs on Hugging Face infrastructure
- 🪣 **Storage Management**: Manage buckets and files

**Example Agent Commands:**
```bash
# Search for quantum models
hf search models "quantum variational autoencoder"

# Upload dataset
hf upload dataset YOUR_USERNAME/agi-datasets ./real_data

# Deploy Space
hf upload spaces/YOUR_USERNAME/agi-model hf-deploy .

# Check Space status
hf spaces info YOUR_USERNAME/agi-model
```

**Resources:**
- [CLI Reference](https://huggingface.co/docs/huggingface_hub/guides/cli) - Complete command documentation
- [Agent Skills](https://agentskills.io) - CLI skill documentation
- [Jobs Documentation](https://huggingface.co/docs/huggingface_hub/guides/cli#hf-jobs) - Compute jobs guide

---

## 📞 Support

- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces
- **GitHub Community**: https://github.com/community
- **AGI Model Issues**: https://github.com/quantumdynamics927-dotcom/AGI-model/issues

---

**AGI Model v0.98.0-rc**  
*Production-Ready Research Platform*
