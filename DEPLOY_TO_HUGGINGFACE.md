# Deploy AGI Model to Hugging Face Spaces

## 🎯 Overview

This guide walks you through deploying the AGI Model to Hugging Face Spaces as an interactive Docker-based demo.

## 📋 Prerequisites

- Hugging Face account: https://huggingface.co/join
- GitHub account (already set up)
- Hugging Face API token

## 🚀 Quick Start

### Step 1: Create Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Configure:
   - **Space name**: `agi-model`
   - **License**: MIT
   - **SDK**: Docker
   - **Visibility**: Public
4. Click "Create Space"

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

If you want to deploy immediately:

```bash
# Clone your Hugging Face Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/agi-model
cd agi-model

# Copy files from AGI-model repo
cp /path/to/AGI-model/space_app.py .
cp /path/to/AGI-model/Dockerfile .
cp /path/to/AGI-model/README_HF_SPACE.md README.md
cp -r /path/to/AGI-model/.github .

# Push to Space
git add .
git commit -m "Initial deployment: AGI Model v0.98.0-rc"
git push
```

## 📊 What Gets Deployed

### Files Included
- ✅ `space_app.py` - Gradio interface
- ✅ `Dockerfile` - Container configuration
- ✅ `README_HF_SPACE.md` - Space documentation
- ✅ `.github/workflows/` - Auto-sync workflow
- ✅ `requirements.txt` - Python dependencies

### Features Available
- 🔬 **Discovery Validator**: Interactive certification demo
- 🚀 **Pipeline Demo**: 8-stage workflow visualization
- 📊 **Metrics Calculator**: Consciousness metrics tool
- ℹ️ **System Status**: Live platform information

## 🔧 Configuration

### Dockerfile Settings

The Dockerfile is configured for:
- **Python**: 3.10-slim
- **Port**: 7860 (Gradio default)
- **Health Check**: Every 30 seconds
- **Security**: Non-root user

### Space Metadata

Edit `README_HF_SPACE.md` front matter:

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

## 📞 Support

- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces
- **GitHub Community**: https://github.com/community
- **AGI Model Issues**: https://github.com/quantumdynamics927-dotcom/AGI-model/issues

---

**AGI Model v0.98.0-rc**  
*Production-Ready Research Platform*
