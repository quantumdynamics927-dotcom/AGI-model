# Phase 3: Tesseract/Biomimetic Optimization Results

This directory contains results from Phase 3 optimization campaigns.

## Structure

```
phase3_results/
├── PHASE3_OPTIMIZATION_REPORT.md    # Human-readable summary
├── result_tess_001.json            # Detailed results for candidate 1
├── result_tess_002.json            # Detailed results for candidate 2
├── result_tess_003.json            # Detailed results for candidate 3
├── result_tess_004.json            # Detailed results for candidate 4
├── candidate_performance/          # Raw performance data
│   ├── tess_001_clean.jsonl
│   ├── tess_001_fault.jsonl
│   ├── tess_001_stress.jsonl
│   └── ... (similar for other candidates)
└── statistical_analyses/           # Detailed statistical tests
    ├── pairwise_comparisons.csv
    ├── effect_sizes.json
    └── confidence_intervals.json
```

## File Descriptions

### PHASE3_OPTIMIZATION_REPORT.md
Executive summary of the optimization campaign with:
- Candidate performance comparison
- Statistical test results
- Promotion decisions
- Recommendations for next steps

### result_*.json
Detailed results for each candidate:
```json
{
  "candidate_id": "tess_001",
  "metrics_comparison": {
    "clean": {
      "success_rate": {
        "baseline_mean": 0.899,
        "candidate_mean": 0.915,
        "difference": 0.016,
        "t_statistic": 2.34,
        "p_value": 0.021,
        "cohens_d": 0.24
      }
    }
  },
  "promotion_decision": "promote",
  "decision_reasoning": "Superior on 2 metrics, no non-inferiority violations"
}
```

### candidate_performance/*.jsonl
Raw performance data in JSONL format (one JSON object per line):
```json
{"timestamp": "2026-04-19T10:00:01", "seed": 42, "condition": "clean", "success_rate": 0.92, "latency": 0.45}
{"timestamp": "2026-04-19T10:00:02", "seed": 43, "condition": "clean", "success_rate": 0.89, "latency": 0.48}
```

### statistical_analyses/*
Detailed statistical analyses:
- Pairwise comparisons between baseline and candidates
- Effect sizes with confidence intervals
- Power analysis results

## Governance Integration

All results are recorded via the governance layer:
- `MetricsRegistry` tracks all metrics
- `BoundedExperiment` ensures controlled conditions
- `TypedMetric` maintains metric classification and bounds

## Access Patterns

To analyze results:
1. Start with `PHASE3_OPTIMIZATION_REPORT.md` for overview
2. Drill into `result_*.json` for detailed metrics
3. Examine `candidate_performance/` for raw data
4. Check `statistical_analyses/` for rigorous statistical tests

## Version Control

This directory is managed by git with:
- Results committed after each optimization run
- Filenames include timestamps for traceability
- Large data files tracked via Git LFS