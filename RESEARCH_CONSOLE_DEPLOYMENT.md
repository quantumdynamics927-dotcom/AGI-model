# AGI Research Console Deployment Checklist

## Status: ⏳ NOT READY FOR DEPLOYMENT

**Blocker**: PR #35 critical bugs must be fixed first.

---

## Files Created

| File | Purpose | Status |
|------|---------|--------|
| `research_console.py` | Main Gradio app | ✅ Created |
| `requirements_console.txt` | Dependencies | ✅ Created |
| `README_console.md` | HF Space header | ✅ Created |
| `Dockerfile.console` | Docker build with Ollama | ✅ Created |
| `start_console.sh` | Startup script | ✅ Created |
| `.github/workflows/sync-research-console.yml` | CI/CD workflow | ✅ Created |

---

## Pre-Deployment Requirements

### 1. Fix PR #35 Critical Bugs

Before deploying, these bugs must be fixed on `minimal-repo` branch and merged to `main`:

| Bug | File | Status |
|-----|------|--------|
| Layer weights not applied in ablation forward pass | `qagi_matched_controls_ablation.py` | ❌ Not fixed |
| Zero-variance baseline in matched-controls ablation | `qagi_matched_controls_ablation.py` | ❌ Not fixed |
| Hardcoded `ranking_correlation = 0.7` | `qagi_matched_controls_ablation.py` | ❌ Not fixed |
| Inflated `estimated_accuracy + 0.5` | `qagi_matched_controls_ablation.py` | ❌ Not fixed |

**Why this matters**: The Research Console surfaces governance outputs directly in the UI. If these bugs are live in the backend, the console will display scientifically invalid results publicly.

### 2. Create Hugging Face Space

1. Go to https://huggingface.co/new-space
2. Configure:
   - **Owner**: Quantum927
   - **Space name**: `agi-research-console`
   - **SDK**: Gradio (or Docker for Ollama support)
   - **Visibility**: Private (until bugs fixed)
   - **License**: MIT
3. Click "Create Space"

### 3. Configure GitHub Secrets

In your GitHub repository settings:

1. Go to Settings → Secrets and variables → Actions
2. Ensure `HF_TOKEN` is set (same as existing `agi-ollama-demo`)

---

## Deployment Order

```
1. Fix PR #35 bugs on minimal-repo branch
   ↓
2. Run tests to verify fixes
   ↓
3. Merge PR #35 to main
   ↓
4. Create HF Space: Quantum927/agi-research-console
   ↓
5. Push triggers GitHub Actions workflow
   ↓
6. Workflow checks bug fixes automatically
   ↓
7. If checks pass → deployment proceeds
   ↓
8. Verify Space at: https://huggingface.co/spaces/Quantum927/agi-research-console
```

---

## Technical Constraints

### Ollama in HF Spaces

HF Spaces do not have Ollama installed by default. Two options:

**Option A: Docker Space (Recommended)**
- Use `Dockerfile.console` which installs Ollama
- Pulls `llama3.2:1b` and `qwen3:1.7b` on startup
- Larger image size but full local inference

**Option B: Gradio SDK with Cloud Fallback**
- Use `research_console.py` directly
- Ollama unavailable → falls back to cloud models
- Requires API keys for cloud models

### Model Availability

| Model | Local (Docker) | Cloud (Gradio SDK) |
|-------|----------------|-------------------|
| llama3.2:1b | ✅ Available | ❌ Unavailable |
| qwen3:1.7b | ✅ Available | ❌ Unavailable |
| glm-5 | ❌ Requires API | ⚠️ Requires API |
| claude-3-5-sonnet | ❌ Requires API | ⚠️ Requires API |
| gpt-4o | ❌ Requires API | ⚠️ Requires API |

---

## Post-Deployment Verification

After deployment, verify:

1. **Space loads** at https://huggingface.co/spaces/Quantum927/agi-research-console
2. **Ollama models available** (if Docker Space)
3. **Governance tab** shows correct lifecycle state
4. **Golden tests** pass
5. **Paired fixtures** load correctly
6. **Chat** responds with model routing

---

## Rollback Plan

If issues occur:

1. Delete the HF Space: `hf spaces delete Quantum927/agi-research-console`
2. Disable the workflow: `.github/workflows/sync-research-console.yml`
3. Fix issues on `minimal-repo` branch
4. Re-deploy following the deployment order above

---

## Related Files

- `research_console.py` - Main application
- `vcapture_lifecycle_governance.py` - Governance backend
- `vcapture_canonical_schema.py` - Output schema
- `vcapture_golden_tests.py` - Test suite
- `vcapture_paired_fixtures.py` - Comparison fixtures
- `phase3_optimization.py` - Phase 3 evaluation
- `consciousness_validation_framework.py` - Consciousness metrics
- `qagi_sacred_geometry_native.py` - Topology explorer

---

## Next Steps

1. **Fix PR #35 bugs** - Priority #1
2. **Test locally** - Run `python research_console.py` and verify all tabs work
3. **Create HF Space** - After bugs fixed
4. **Enable workflow** - Uncomment `workflow_dispatch` for manual trigger
5. **Deploy** - Push to main or trigger manually