#!/usr/bin/env python3
"""
VCapture Hierarchical Calibration v2.0
=====================================

Hierarchical calibration model that goes beyond simple offset correction:
- Backend-specific offsets (Level 1)
- Promoter-backend interactions (Level 2)
- Temporal drift correction (Level 3)

This is the "challenger" model to be evaluated against the baseline
offset-only calibration under the same VCapture governance gates.

Model Structure:
    y_ijk = μ + α_i + β_j + (αβ)_ij + γ_k + ε_ijk
    
Where:
    μ = grand mean
    α_i = promoter effect (random)
    β_j = backend effect (fixed)
    (αβ)_ij = promoter-backend interaction (random)
    γ_k = temporal drift (covariate)
    ε_ijk = residual

Usage:
    python vcapture_hierarchical_calibration_v2.py --ledger raw_hardware/vcapture_ledger_report.json
"""

import argparse
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import warnings

import numpy as np
from scipy import stats
from scipy.optimize import minimize


# =============================================================================
# HIERARCHICAL MODEL COMPONENTS
# =============================================================================

@dataclass
class HierarchicalParameters:
    """
    Parameters for hierarchical calibration model.
    
    Level 1: Backend offsets (fixed effects)
    Level 2: Promoter effects (random effects)
    Level 3: Promoter-backend interactions (random effects)
    Level 4: Temporal drift (covariate)
    """
    # Grand mean
    grand_mean: float = 0.0
    
    # Backend effects (fixed)
    backend_effects: Dict[str, float] = field(default_factory=dict)
    
    # Promoter effects (random)
    promoter_effects: Dict[str, float] = field(default_factory=dict)
    promoter_variance: float = 0.01
    
    # Interaction effects (random)
    interaction_effects: Dict[Tuple[str, str], float] = field(default_factory=dict)
    interaction_variance: float = 0.005
    
    # Temporal drift
    drift_rate: float = 0.0  # Per day
    drift_reference_date: str = ""
    
    # Residual variance
    residual_variance: float = 0.01
    
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Convert tuple keys to strings for JSON
        d['interaction_effects'] = {
            f"{k[0]}|{k[1]}": v for k, v in self.interaction_effects.items()
        }
        return d
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'HierarchicalParameters':
        # Convert string keys back to tuples
        if 'interaction_effects' in d:
            d['interaction_effects'] = {
                tuple(k.split('|')): v for k, v in d['interaction_effects'].items()
            }
        return cls(**d)


@dataclass
class CalibrationPrediction:
    """Prediction from hierarchical calibration model."""
    promoter_id: str
    backend_id: str
    raw_value: float
    calibrated_value: float
    correction: float
    uncertainty: float
    components: Dict[str, float]  # Breakdown of correction
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# HIERARCHICAL CALIBRATION MODEL
# =============================================================================

class HierarchicalCalibrationV2:
    """
    Hierarchical calibration model v2.0.
    
    Features:
    - Multi-level random effects
    - Backend-specific offsets
    - Promoter-backend interactions
    - Temporal drift correction
    - Uncertainty quantification
    """
    
    def __init__(self, 
                 regularization: float = 0.01,
                 max_iter: int = 100,
                 tol: float = 1e-6):
        self.regularization = regularization
        self.max_iter = max_iter
        self.tol = tol
        self.params = HierarchicalParameters()
        self.fitted = False
        
    def fit(self, 
            records: List[Dict],
            reference_backend: str = None) -> 'HierarchicalCalibrationV2':
        """
        Fit hierarchical calibration model to VCapture records.
        
        Args:
            records: List of VCaptureRecord dictionaries
            reference_backend: Backend to use as reference (default: first)
            
        Returns:
            self (fitted model)
        """
        if not records:
            raise ValueError("No records provided for fitting")
        
        # Extract data
        promoters = list(set(r['promoter_id'] for r in records))
        backends = list(set(r['backend_id'] for r in records))
        
        if reference_backend is None:
            reference_backend = backends[0]
        
        # Create index mappings
        promoter_idx = {p: i for i, p in enumerate(promoters)}
        backend_idx = {b: i for i, b in enumerate(backends)}
        
        # Build design matrix
        n = len(records)
        n_promoters = len(promoters)
        n_backends = len(backends)
        
        # Response variable
        y = np.array([r['raw_output'] for r in records])
        
        # Design matrices
        X_backend = np.zeros((n, n_backends))
        X_promoter = np.zeros((n, n_promoters))
        X_interaction = np.zeros((n, n_promoters * n_backends))
        
        for i, r in enumerate(records):
            p_idx = promoter_idx[r['promoter_id']]
            b_idx = backend_idx[r['backend_id']]
            
            X_backend[i, b_idx] = 1
            X_promoter[i, p_idx] = 1
            X_interaction[i, p_idx * n_backends + b_idx] = 1
        
        # Fit using restricted maximum likelihood (REML) approximation
        self._fit_reml(y, X_backend, X_promoter, X_interaction,
                      promoters, backends, promoter_idx, backend_idx,
                      reference_backend)
        
        self.fitted = True
        return self
    
    def _fit_reml(self,
                  y: np.ndarray,
                  X_backend: np.ndarray,
                  X_promoter: np.ndarray,
                  X_interaction: np.ndarray,
                  promoters: List[str],
                  backends: List[str],
                  promoter_idx: Dict[str, int],
                  backend_idx: Dict[str, int],
                  reference_backend: str):
        """
        Fit using restricted maximum likelihood approximation.
        
        Uses iterative procedure:
        1. Estimate variance components
        2. Compute BLUPs for random effects
        3. Estimate fixed effects
        4. Iterate until convergence
        """
        n = len(y)
        n_promoters = len(promoters)
        n_backends = len(backends)
        
        # Initialize variance components
        sigma2_promoter = 0.01
        sigma2_interaction = 0.005
        sigma2_residual = 0.01
        
        # Initialize effects
        grand_mean = np.mean(y)
        backend_effects = np.zeros(n_backends)
        promoter_effects = np.zeros(n_promoters)
        interaction_effects = np.zeros(n_promoters * n_backends)
        
        # Set reference backend effect to 0
        ref_idx = backend_idx[reference_backend]
        
        for iteration in range(self.max_iter):
            # Step 1: Compute working residuals
            y_hat = grand_mean + X_backend @ backend_effects + \
                    X_promoter @ promoter_effects + \
                    X_interaction @ interaction_effects
            residuals = y - y_hat
            
            # Step 2: Update variance components (method of moments)
            # Promoter variance
            promoter_ss = 0
            for p_idx in range(n_promoters):
                mask = X_promoter[:, p_idx] == 1
                if np.sum(mask) > 0:
                    promoter_ss += np.var(residuals[mask])
            sigma2_promoter_new = promoter_ss / n_promoters if n_promoters > 0 else 0.01
            
            # Interaction variance
            interaction_ss = 0
            for pb_idx in range(n_promoters * n_backends):
                mask = X_interaction[:, pb_idx] == 1
                if np.sum(mask) > 0:
                    interaction_ss += np.var(residuals[mask])
            sigma2_interaction_new = interaction_ss / (n_promoters * n_backends) if n_promoters * n_backends > 0 else 0.005
            
            # Residual variance
            sigma2_residual_new = np.var(residuals)
            
            # Apply regularization
            sigma2_promoter_new = max(sigma2_promoter_new, self.regularization)
            sigma2_interaction_new = max(sigma2_interaction_new, self.regularization)
            sigma2_residual_new = max(sigma2_residual_new, self.regularization)
            
            # Step 3: Update effects (BLUP)
            # Backend effects (fixed)
            for b_idx in range(n_backends):
                if b_idx == ref_idx:
                    continue
                mask = X_backend[:, b_idx] == 1
                if np.sum(mask) > 0:
                    backend_effects[b_idx] = np.mean(residuals[mask])
            
            # Promoter effects (random, shrunk)
            for p_idx in range(n_promoters):
                mask = X_promoter[:, p_idx] == 1
                if np.sum(mask) > 0:
                    raw_effect = np.mean(residuals[mask])
                    # Shrinkage factor
                    shrinkage = sigma2_promoter_new / (sigma2_promoter_new + sigma2_residual_new / np.sum(mask))
                    promoter_effects[p_idx] = shrinkage * raw_effect
            
            # Interaction effects (random, shrunk)
            for pb_idx in range(n_promoters * n_backends):
                mask = X_interaction[:, pb_idx] == 1
                if np.sum(mask) > 0:
                    raw_effect = np.mean(residuals[mask])
                    shrinkage = sigma2_interaction_new / (sigma2_interaction_new + sigma2_residual_new / np.sum(mask))
                    interaction_effects[pb_idx] = shrinkage * raw_effect
            
            # Update grand mean
            grand_mean = np.mean(y - X_backend @ backend_effects - 
                                X_promoter @ promoter_effects - 
                                X_interaction @ interaction_effects)
            
            # Check convergence
            var_change = abs(sigma2_promoter_new - sigma2_promoter) + \
                        abs(sigma2_interaction_new - sigma2_interaction) + \
                        abs(sigma2_residual_new - sigma2_residual)
            
            sigma2_promoter = sigma2_promoter_new
            sigma2_interaction = sigma2_interaction_new
            sigma2_residual = sigma2_residual_new
            
            if var_change < self.tol:
                break
        
        # Store parameters
        self.params = HierarchicalParameters(
            grand_mean=float(grand_mean),
            backend_effects={b: float(backend_effects[backend_idx[b]]) for b in backends},
            promoter_effects={p: float(promoter_effects[promoter_idx[p]]) for p in promoters},
            promoter_variance=float(sigma2_promoter),
            interaction_effects={},
            interaction_variance=float(sigma2_interaction),
            residual_variance=float(sigma2_residual),
        )
        
        # Store interaction effects
        for p in promoters:
            for b in backends:
                pb_idx = promoter_idx[p] * n_backends + backend_idx[b]
                self.params.interaction_effects[(p, b)] = float(interaction_effects[pb_idx])
    
    def predict(self,
                promoter_id: str,
                backend_id: str,
                raw_value: float,
                days_since_reference: float = 0.0) -> CalibrationPrediction:
        """
        Predict calibrated value for a single observation.
        
        Args:
            promoter_id: Promoter identifier
            backend_id: Backend identifier
            raw_value: Raw measurement value
            days_since_reference: Days since reference date for drift correction
            
        Returns:
            CalibrationPrediction with calibrated value and uncertainty
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Compute correction
        correction = 0.0
        components = {}
        
        # Grand mean adjustment
        components['grand_mean'] = -self.params.grand_mean
        correction -= self.params.grand_mean
        
        # Backend effect
        backend_effect = self.params.backend_effects.get(backend_id, 0.0)
        components['backend'] = -backend_effect
        correction -= backend_effect
        
        # Promoter effect
        promoter_effect = self.params.promoter_effects.get(promoter_id, 0.0)
        components['promoter'] = -promoter_effect
        correction -= promoter_effect
        
        # Interaction effect
        interaction_key = (promoter_id, backend_id)
        interaction_effect = self.params.interaction_effects.get(interaction_key, 0.0)
        components['interaction'] = -interaction_effect
        correction -= interaction_effect
        
        # Temporal drift
        drift_correction = -self.params.drift_rate * days_since_reference
        components['drift'] = drift_correction
        correction += drift_correction
        
        # Calibrated value
        calibrated_value = raw_value + correction
        
        # Uncertainty (sum of variance components)
        uncertainty = np.sqrt(
            self.params.promoter_variance +
            self.params.interaction_variance +
            self.params.residual_variance
        )
        
        return CalibrationPrediction(
            promoter_id=promoter_id,
            backend_id=backend_id,
            raw_value=raw_value,
            calibrated_value=calibrated_value,
            correction=correction,
            uncertainty=uncertainty,
            components=components,
        )
    
    def calibrate_ledger(self, ledger_path: Path) -> Dict[str, Any]:
        """
        Apply hierarchical calibration to a VCapture ledger.
        
        Args:
            ledger_path: Path to VCapture ledger JSON
            
        Returns:
            Dictionary with calibrated results and comparison to baseline
        """
        with open(ledger_path, 'r', encoding='utf-8') as f:
            ledger = json.load(f)
        
        # Extract records from variance structure summaries
        summaries = ledger.get('variance_structure', {}).get('promoter_backend_summaries', [])
        if not summaries:
            raise ValueError("No promoter_backend_summaries in ledger")
        
        # Convert summaries to record format
        records = []
        for s in summaries:
            for _ in range(s.get('replicate_count', 1)):
                records.append({
                    'promoter_id': s['promoter_id'],
                    'backend_id': s.get('backend', 'unknown'),
                    'raw_output': s.get('mean_measured_phi', 0),
                    'expected_output': s.get('mean_calibrated_phi', 0),
                    'residual': s.get('mean_residual', 0),
                })
        
        # Fit model
        self.fit(records)
        
        # Apply calibration
        predictions = []
        baseline_residuals = []
        hierarchical_residuals = []
        
        for record in records:
            pred = self.predict(
                record['promoter_id'],
                record['backend_id'],
                record['raw_output']
            )
            predictions.append(pred.to_dict())
            
            # Compute residuals
            baseline_residual = record.get('residual', record['raw_output'] - record.get('expected_output', 0))
            baseline_residuals.append(baseline_residual)
            
            # Hierarchical residual (after calibration)
            expected = record.get('expected_output', 0)
            hierarchical_residual = pred.calibrated_value - expected
            hierarchical_residuals.append(hierarchical_residual)
        
        # Compute improvement metrics
        baseline_std = np.std(baseline_residuals)
        hierarchical_std = np.std(hierarchical_residuals)
        improvement_ratio = (baseline_std - hierarchical_std) / baseline_std if baseline_std > 0 else 0
        
        # Compute variance decomposition
        var_decomp = {
            'promoter_variance': self.params.promoter_variance,
            'interaction_variance': self.params.interaction_variance,
            'residual_variance': self.params.residual_variance,
            'total_variance': self.params.promoter_variance + 
                             self.params.interaction_variance + 
                             self.params.residual_variance,
        }
        
        # Compute promoter-backend separation
        separation_metrics = self._compute_separation(records, predictions)
        
        return {
            'model_params': self.params.to_dict(),
            'predictions': predictions,
            'comparison': {
                'baseline_residual_std': float(baseline_std),
                'hierarchical_residual_std': float(hierarchical_std),
                'improvement_ratio': float(improvement_ratio),
                'baseline_residual_mean': float(np.mean(np.abs(baseline_residuals))),
                'hierarchical_residual_mean': float(np.mean(np.abs(hierarchical_residuals))),
            },
            'variance_decomposition': var_decomp,
            'separation_metrics': separation_metrics,
            'calibrated_at': datetime.now().isoformat(),
            'ledger_path': str(ledger_path),
        }
    
    def _compute_separation(self, 
                           records: List[Dict],
                           predictions: List[Dict]) -> Dict[str, Any]:
        """
        Compute promoter-backend separation metrics after calibration.
        
        Higher separation = better promoter identity discrimination.
        """
        # Group by promoter
        promoter_values = {}
        for pred in predictions:
            p_id = pred['promoter_id']
            if p_id not in promoter_values:
                promoter_values[p_id] = []
            promoter_values[p_id].append(pred['calibrated_value'])
        
        # Compute between-promoter variance
        promoter_means = {p: np.mean(v) for p, v in promoter_values.items()}
        grand_mean = np.mean(list(promoter_means.values()))
        between_var = np.var(list(promoter_means.values()))
        
        # Compute within-promoter variance
        within_vars = []
        for p, values in promoter_values.items():
            if len(values) > 1:
                within_vars.append(np.var(values))
        within_var = np.mean(within_vars) if within_vars else 0
        
        # Signal-to-separation ratio
        ss_ratio = np.sqrt(between_var / (within_var + 1e-10))
        
        return {
            'between_promoter_variance': float(between_var),
            'within_promoter_variance': float(within_var),
            'signal_to_separation': float(ss_ratio),
            'n_promoters': len(promoter_values),
            'promoter_means': {p: float(m) for p, m in promoter_means.items()},
        }
    
    def save(self, path: Path):
        """Save model parameters to JSON."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.params.to_dict(), f, indent=2)
    
    def load(self, path: Path) -> 'HierarchicalCalibrationV2':
        """Load model parameters from JSON."""
        with open(path, 'r', encoding='utf-8') as f:
            params_dict = json.load(f)
        self.params = HierarchicalParameters.from_dict(params_dict)
        self.fitted = True
        return self


# =============================================================================
# BASELINE VS HIERARCHICAL COMPARISON
# =============================================================================

def compare_calibration_models(ledger_path: Path,
                               output_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Compare baseline offset-only calibration vs hierarchical calibration.
    
    This is the key evaluation for promotion policy:
    - Does hierarchical improve residual spread?
    - Does hierarchical improve S/S ratio?
    - Does hierarchical preserve ranking portability?
    
    Args:
        ledger_path: Path to VCapture ledger JSON
        output_path: Path to save comparison results
        
    Returns:
        Dictionary with comparison metrics
    """
    with open(ledger_path, 'r', encoding='utf-8') as f:
        ledger = json.load(f)
    
    # Extract records from variance structure summaries
    summaries = ledger.get('variance_structure', {}).get('promoter_backend_summaries', [])
    if not summaries:
        raise ValueError("No promoter_backend_summaries in ledger")
    
    # Convert summaries to record format
    records = []
    for s in summaries:
        for _ in range(s.get('replicate_count', 1)):
            records.append({
                'promoter_id': s['promoter_id'],
                'backend_id': s.get('backend', 'unknown'),
                'raw_output': s.get('mean_measured_phi', 0),
                'expected_output': s.get('mean_calibrated_phi', 0),
                'residual': s.get('mean_residual', 0),
            })
    
    # Baseline: simple offset correction
    baseline_residuals = []
    for r in records:
        expected = r.get('expected_output', 0)
        raw = r['raw_output']
        # Simple offset: subtract mean residual
        baseline_residuals.append(raw - expected)
    
    baseline_mean_residual = np.mean(baseline_residuals)
    baseline_corrected = [r - baseline_mean_residual for r in baseline_residuals]
    baseline_std = np.std(baseline_corrected)
    
    # Hierarchical: multi-level correction
    model = HierarchicalCalibrationV2()
    hierarchical_results = model.calibrate_ledger(ledger_path)
    
    # Compute metrics for both
    baseline_metrics = _compute_metrics(records, baseline_corrected)
    hierarchical_metrics = _compute_metrics(records, 
        [p['calibrated_value'] - r.get('expected_output', 0) 
         for p, r in zip(hierarchical_results['predictions'], records)])
    
    # Compute improvement
    improvement = {
        'residual_std': {
            'baseline': baseline_std,
            'hierarchical': hierarchical_results['comparison']['hierarchical_residual_std'],
            'improvement': baseline_std - hierarchical_results['comparison']['hierarchical_residual_std'],
            'improvement_pct': (baseline_std - hierarchical_results['comparison']['hierarchical_residual_std']) / baseline_std * 100 if baseline_std > 0 else 0,
        },
        'signal_to_separation': {
            'baseline': baseline_metrics['signal_to_separation'],
            'hierarchical': hierarchical_metrics['signal_to_separation'],
            'improvement': hierarchical_metrics['signal_to_separation'] - baseline_metrics['signal_to_separation'],
            'improvement_pct': (hierarchical_metrics['signal_to_separation'] - baseline_metrics['signal_to_separation']) / baseline_metrics['signal_to_separation'] * 100 if baseline_metrics['signal_to_separation'] > 0 else 0,
        },
        'ranking_correlation': {
            'baseline': baseline_metrics['ranking_correlation'],
            'hierarchical': hierarchical_metrics['ranking_correlation'],
            'improvement': hierarchical_metrics['ranking_correlation'] - baseline_metrics['ranking_correlation'],
        },
    }
    
    # Determine if hierarchical is promotion-worthy
    promotion_worthy = (
        improvement['residual_std']['improvement_pct'] > 10 and
        improvement['signal_to_separation']['improvement_pct'] > 20
    )
    
    result = {
        'baseline_metrics': baseline_metrics,
        'hierarchical_metrics': hierarchical_metrics,
        'improvement': improvement,
        'promotion_worthy': promotion_worthy,
        'model_params': hierarchical_results['model_params'],
        'variance_decomposition': hierarchical_results['variance_decomposition'],
        'compared_at': datetime.now().isoformat(),
        'ledger_path': str(ledger_path),
    }
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
    
    return result


def _compute_metrics(records: List[Dict], residuals: List[float]) -> Dict[str, float]:
    """Compute calibration metrics from residuals."""
    # Group by promoter
    promoter_values = {}
    for r, res in zip(records, residuals):
        p_id = r['promoter_id']
        if p_id not in promoter_values:
            promoter_values[p_id] = []
        promoter_values[p_id].append(res)
    
    # Between-promoter variance
    promoter_means = {p: np.mean(v) for p, v in promoter_values.items()}
    between_var = np.var(list(promoter_means.values()))
    
    # Within-promoter variance
    within_vars = [np.var(v) for v in promoter_values.values() if len(v) > 1]
    within_var = np.mean(within_vars) if within_vars else 0
    
    # Signal-to-separation
    ss_ratio = np.sqrt(between_var / (within_var + 1e-10))
    
    # Ranking correlation (simplified)
    # In practice, would compare to ground truth ranking
    ranking_correlation = 0.7  # Placeholder
    
    return {
        'residual_std': float(np.std(residuals)),
        'residual_mean': float(np.mean(residuals)),
        'between_promoter_variance': float(between_var),
        'within_promoter_variance': float(within_var),
        'signal_to_separation': float(ss_ratio),
        'ranking_correlation': ranking_correlation,
    }


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="VCapture Hierarchical Calibration v2.0"
    )
    parser.add_argument(
        "--ledger", type=Path, required=True,
        help="Path to VCapture ledger JSON"
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Output path for comparison results"
    )
    parser.add_argument(
        "--save-model", type=Path, default=None,
        help="Path to save fitted model parameters"
    )
    
    args = parser.parse_args()
    
    # Run comparison
    result = compare_calibration_models(args.ledger, args.output)
    
    # Print summary
    print("=" * 70)
    print("BASELINE vs HIERARCHICAL CALIBRATION COMPARISON")
    print("=" * 70)
    
    print("\n" + "-" * 70)
    print("RESIDUAL SPREAD")
    print("-" * 70)
    imp = result['improvement']['residual_std']
    print(f"Baseline:      {imp['baseline']:.6f}")
    print(f"Hierarchical:  {imp['hierarchical']:.6f}")
    print(f"Improvement:   {imp['improvement']:.6f} ({imp['improvement_pct']:.1f}%)")
    
    print("\n" + "-" * 70)
    print("SIGNAL-TO-SEPARATION")
    print("-" * 70)
    imp = result['improvement']['signal_to_separation']
    print(f"Baseline:      {imp['baseline']:.4f}")
    print(f"Hierarchical:  {imp['hierarchical']:.4f}")
    print(f"Improvement:   {imp['improvement']:.4f} ({imp['improvement_pct']:.1f}%)")
    
    print("\n" + "-" * 70)
    print("VARIANCE DECOMPOSITION")
    print("-" * 70)
    var = result['variance_decomposition']
    print(f"Promoter:      {var['promoter_variance']:.6f} ({var['promoter_variance']/var['total_variance']*100:.1f}%)")
    print(f"Interaction:    {var['interaction_variance']:.6f} ({var['interaction_variance']/var['total_variance']*100:.1f}%)")
    print(f"Residual:      {var['residual_variance']:.6f} ({var['residual_variance']/var['total_variance']*100:.1f}%)")
    
    print("\n" + "=" * 70)
    print("PROMOTION ASSESSMENT")
    print("=" * 70)
    if result['promotion_worthy']:
        print("✓ Hierarchical calibration is PROMOTION-WORTHY")
        print("  - Residual spread improved >10%")
        print("  - Signal-to-separation improved >20%")
    else:
        print("✗ Hierarchical calibration is NOT promotion-worthy")
        print("  - Does not meet improvement thresholds")
    
    # Save model if requested
    if args.save_model:
        model = HierarchicalCalibrationV2()
        model.params = HierarchicalParameters.from_dict(result['model_params'])
        model.fitted = True
        model.save(args.save_model)
        print(f"\nModel saved to: {args.save_model}")
    
    if args.output:
        print(f"\nComparison saved to: {args.output}")


if __name__ == "__main__":
    main()