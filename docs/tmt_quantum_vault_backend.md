# TMT Quantum Vault Backend

This repo can use TMT_Quantum_Vault as an external validation backend for
AGI-model outputs.

## What This Integration Adds

- Post-training checkpoint validation from `train_vae.py`
- Conversion of AGI-model JSON artifacts into a Vault `eval` dataset
- A reusable local helper for `run`, `agent-task`, `eval`,
  `release-evidence`, and `release-gate`
- Central operation-to-model selection for Ollama Cloud-backed analysis

## Ollama Cloud Operation Map

The repo now resolves cloud model tags centrally in `ollama_cloud_models.py`.

Current default strategy:

- Use `qwen3-coder-next:cloud` for every AGI-model cloud operation by default.
- Reason: it is the only cloud tag already validated in this repo's CI and Vault smoke path.
- Override per operation with dedicated environment variables or per-command `--model`.

Operation map:

- `vae_checkpoint_validation`: best checkpoint health review after training
- `vae_loss_interpretation`: interpret `vae-smoke` loss terms and recommend one training adjustment
- `phi_artifact_analysis`: interpret phi / IIT artifact summaries and propose the next experiment
- `eval_case_generation`: generate additional Vault eval edge cases
- `ci_audit_oracle`: emit structured CI audit verdicts from smoke and artifact summaries
- `research_report_generation`: produce short artifact-grounded research summaries

Print the resolved model map locally:

```powershell
python tmt_vault_integration.py models
```

## Local Layout

The helper looks for the Vault checkout in one of these locations:

- `../TMT_Quantum_Vault-`
- `../TMT_Quantum_Vault`
- `./TMT_Quantum_Vault-`
- `./TMT_Quantum_Vault`

You can override discovery with the environment variable `TMT_QUANTUM_VAULT_REPO`.

## Training Validation

Run training as usual, then add the Vault hook when you want a structured pass/fail review of the best checkpoint.

```powershell
python train_vae.py --vault_validate --vault_mode cloud
```

Optional flags:

- `--vault_repo <path>`: explicit Vault checkout path
- `--vault_model <tag>`: explicit Ollama Cloud model override for checkpoint validation
- `--vault_extra_context "..."`: extra prompt context for the validator
- `--summary_path <path>`: where to write the AGI-model training summary JSON

Artifacts produced by training:

- `best_model.pt`
- `training_curves.png`
- `best_model.summary.json`

When Vault validation is enabled, the summary JSON is updated with a `vault_validation` block containing the executed command, stdout/stderr, and parsed JSON if the CLI returned JSON.

## Convert AGI Results To Eval Dataset

Use the converter to build a Vault-native `EvalDataset` from AGI-model
experiment artifacts.

```powershell
python convert_agi_results_to_tmt_eval.py \
  phi_agent_report_20260310_231439.json \
  dna_quantum_analysis_results.json \
  ibm_hardware_aggregate_20260202_040836.json \
  --output vault_eval_dataset.json
```

Then run Vault eval against the generated dataset.

```powershell
python tmt_vault_integration.py eval --dataset vault_eval_dataset.json
```

The converter currently recognizes:

- Phi agent reports with `dna_results` and `phi_harmonic`
- DNA quantum analysis files with `analysis_type` and `results`
- IBM hardware aggregate artifacts with `aggregate_metrics` and `individual_jobs`
- Generic JSON artifacts as a fallback

Vault also provides a single-command smoke path that converts and evaluates
the AGI regression dataset directly:

```powershell
$env:PYTHONPATH = "../TMT_Quantum_Vault-"
python -m tmt_quantum_vault agi-eval-smoke --root ../TMT_Quantum_Vault- --agi-root . --dataset-output tmp_vault_eval_dataset.json --json
```

## Run Raw AGI Artifact Through Vault

For a direct summary pass over an existing AGI artifact:

```powershell
python tmt_vault_integration.py run --payload phi_agent_report_20260310_231439.json --mode cloud
```

For a cloud interpretation pass over the phi artifact with the repo's selected
operation model:

```powershell
python tmt_vault_integration.py phi-analyst --artifact phi_agent_report_20260310_231439.json --mode cloud
```

Alias using the operation name directly:

```powershell
python tmt_vault_integration.py phi-artifact-analysis --artifact phi_agent_report_20260310_231439.json --mode cloud
```

By default this also persists the cloud-analysis result to
`phi_artifact_analysis.json`.

## CI Audit Oracle

Combine the saved VAE smoke contract, VAE interpretation, and phi analysis into
one releasability verdict:

```powershell
python tmt_vault_integration.py ci-audit-oracle --mode cloud
```

By default this writes `ci_audit_result.json`.

You can override the input artifact locations if needed:

```powershell
python tmt_vault_integration.py ci-audit-oracle --mode cloud --smoke-artifact artifacts/vae_smoke_result.json --vae-analysis-artifact artifacts/vae_loss_interpretation.json --phi-analysis-artifact artifacts/phi_artifact_analysis.json
```

## Deterministic Contract

For CI and subprocess-based validation, AGI-model now exposes a deterministic JSON contract:

```powershell
python -m agi_model.validate_run vae-smoke
python -m agi_model.validate_run artifact-summary --artifact phi_agent_report_20260310_231439.json
```

The Vault repo can call that contract directly:

```powershell
$env:PYTHONPATH = "../TMT_Quantum_Vault-"
python -m tmt_quantum_vault agi-validate --root ../TMT_Quantum_Vault- --agi-root . --operation vae-smoke --json
```

Use `vae-smoke` for deterministic gating and `artifact-summary` for normalized research-analysis summaries over AGI-model JSON outputs.

You can also route the `vae-smoke` output directly into Ollama Cloud for
automatic interpretation:

```powershell
python tmt_vault_integration.py vae-interpret --mode cloud
```

When this path generates `vae-smoke` locally, it also writes the contract JSON
to `vae_smoke_result.json` by default before calling Vault `agent-task`.

If you already saved the contract output to a JSON file, use the operation-name
alias and pass it explicitly:

```powershell
python tmt_vault_integration.py vae-loss-interpretation --artifact vae_smoke_result.json --mode cloud
```

To change where the auto-generated contract JSON is written:

```powershell
python tmt_vault_integration.py vae-interpret --mode cloud --contract-output artifacts/vae_smoke_result.json
```

This action runs the deterministic contract locally, sends the JSON to Vault
`agent-task`, persists the analysis result to `vae_loss_interpretation.json`
by default, and asks for structured JSON with loss analysis and one concrete
training recommendation.

To change where the analysis result is written:

```powershell
python tmt_vault_integration.py vae-interpret --mode cloud --analysis-output artifacts/vae_loss_interpretation.json
python tmt_vault_integration.py phi-artifact-analysis --artifact phi_agent_report_20260310_231439.json --mode cloud --analysis-output artifacts/phi_artifact_analysis.json
```

## Eval Case Generation

Generate new edge-case eval entries from a seed artifact and merge them into the
Vault dataset:

```powershell
python tmt_vault_integration.py eval-case-generation --seed-artifact phi_artifact_analysis.json --count 10 --mode cloud
```

Defaults:

- writes the generation artifact to `eval_case_generation.json`
- merges the new cases into `tmp_vault_eval_dataset.json`

Override the dataset target or artifact output:

```powershell
python tmt_vault_integration.py eval-case-generation --seed-artifact phi_artifact_analysis.json --count 10 --dataset artifacts/vault_eval_dataset.json --analysis-output artifacts/eval_case_generation.json --mode cloud
```

## One-Shot Research Loop

Run the repo-side chain in one command:

```powershell
python tmt_vault_integration.py research-loop --artifact phi_agent_report_20260310_231439.json --mode cloud
```

This runs:

- `vae-smoke` -> `vae_smoke_result.json`
- `vae-loss-interpretation` -> `vae_loss_interpretation.json`
- `phi-artifact-analysis` -> `phi_artifact_analysis.json`
- `ci-audit-oracle` -> `ci_audit_result.json`

and writes a manifest to `research_loop_result.json`.

## Release Evidence And Gate

Local helper commands:

```powershell
python tmt_vault_integration.py release-evidence --output-dir release-evidence-vae
python tmt_vault_integration.py release-gate --bundle release-evidence-vae
```

## GitHub Actions

The current CI workflow includes one manual Vault-backed smoke path:

- `agi_eval_smoke`: a `workflow_dispatch` job that checks out the sibling
  Vault repo, runs `validate` and `doctor`, executes a Vault `agent-task`
  smoke prompt, and uploads the smoke JSON, provenance JSON, and a dataset
  artifact.

Manual workflow inputs:

- `run_agi_eval_smoke`: enables the Vault smoke job
- `agi_eval_mode`: selects `cloud` or `local`
- `agi_eval_model`: overrides the model tag

Required secrets for private Vault checkout and cloud execution:

- `TMT_VAULT_TOKEN`: personal access token with access to
  `quantumdynamics927-dotcom/TMT_Quantum_Vault-`
- `OLLAMA_API_KEY`: required when `agi_eval_mode=cloud`

The live workflow currently invokes Vault directly from CI for this smoke
path. The deterministic contract and helper CLI in this repo are available for
local validation and future CI expansion, but they are not the mechanism used
by the current checked-in workflow.

## Helper CLI

The local helper script supports:

- `resolve`
- `models`
- `agent-task`
- `vae-interpret`
- `vae-loss-interpretation`
- `phi-analyst`
- `phi-artifact-analysis`
- `ci-audit-oracle`
- `eval-case-generation`
- `research-loop`
- `eval`
- `run`
- `release-evidence`
- `release-gate`

Example:

```powershell
python tmt_vault_integration.py resolve
```
