"""
Experiment Lineage Tracking
===========================

Comprehensive experiment tracking and lineage management
for quantum VAE research. Provides reproducibility,
provenance tracking, and experiment comparison.

Features:
- Experiment registration and metadata storage
- Hyperparameter tracking
- Model checkpoint management
- Result lineage (parent/child experiments)
- Artifact tracking (datasets, models, metrics)
- Reproducibility verification
"""

import torch
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field, asdict
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
import logging
import uuid
import os

logger = logging.getLogger(__name__)


@dataclass
class Hyperparameters:
    """Container for experiment hyperparameters."""
    latent_dim: int
    input_dim: int
    hidden_dims: List[int]
    learning_rate: float
    batch_size: int
    epochs: int
    optimizer: str
    loss_weights: Dict[str, float] = field(default_factory=dict)
    seed: int = 42
    device: str = 'cpu'
    
    # Quantum-specific
    sparsity: float = 0.1
    coherence_weight: float = 0.1
    fidelity_weight: float = 0.1
    
    # Additional params
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hyperparameters':
        return cls(**data)


@dataclass
class ExperimentMetadata:
    """Metadata for an experiment."""
    experiment_id: str
    name: str
    description: str
    created_at: str
    updated_at: str
    status: str  # 'running', 'completed', 'failed', 'paused'
    tags: List[str]
    parent_ids: List[str]  # Parent experiment IDs for lineage
    author: str
    version: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ArtifactInfo:
    """Information about an experiment artifact."""
    artifact_id: str
    name: str
    artifact_type: str  # 'model', 'dataset', 'metrics', 'config', 'log'
    path: str
    checksum: str
    size_bytes: int
    created_at: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExperimentResult:
    """Results from an experiment."""
    experiment_id: str
    metrics: Dict[str, float]
    training_history: Dict[str, List[float]]
    best_epoch: int
    final_loss: float
    completed_at: str
    duration_seconds: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExperimentLineage:
    """
    Manages experiment lineage and tracking.
    
    Provides:
    - Experiment registration and metadata management
    - Hyperparameter tracking
    - Artifact management (models, datasets, metrics)
    - Lineage tracking (parent/child relationships)
    - Reproducibility verification
    """
    
    def __init__(
        self,
        storage_dir: str = "experiment_lineage",
        project_name: str = "quantum_vae"
    ):
        """
        Initialize experiment lineage tracker.
        
        Args:
            storage_dir: Directory to store experiment data
            project_name: Name of the project
        """
        self.storage_dir = Path(storage_dir)
        self.project_name = project_name
        
        # Create directory structure
        self.experiments_dir = self.storage_dir / "experiments"
        self.artifacts_dir = self.storage_dir / "artifacts"
        self.checkpoints_dir = self.storage_dir / "checkpoints"
        
        for directory in [self.storage_dir, self.experiments_dir, 
                          self.artifacts_dir, self.checkpoints_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Index file for quick lookups
        self.index_file = self.storage_dir / "experiment_index.json"
        self.index = self._load_index()
        
        # Current experiment context
        self.current_experiment_id: Optional[str] = None
    
    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """Load experiment index."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        """Save experiment index."""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def _generate_id(self) -> str:
        """Generate unique experiment ID."""
        return f"exp_{uuid.uuid4().hex[:12]}"
    
    def _compute_checksum(self, filepath: str) -> str:
        """Compute SHA256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def register_experiment(
        self,
        name: str,
        description: str,
        hyperparameters: Hyperparameters,
        parent_ids: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        author: str = "unknown",
        version: str = "1.0.0"
    ) -> str:
        """
        Register a new experiment.
        
        Args:
            name: Experiment name
            description: Experiment description
            hyperparameters: Hyperparameters for the experiment
            parent_ids: IDs of parent experiments (for lineage)
            tags: Tags for categorization
            author: Author name
            version: Version string
            
        Returns:
            Experiment ID
        """
        experiment_id = self._generate_id()
        now = datetime.now().isoformat()
        
        metadata = ExperimentMetadata(
            experiment_id=experiment_id,
            name=name,
            description=description,
            created_at=now,
            updated_at=now,
            status='registered',
            tags=tags or [],
            parent_ids=parent_ids or [],
            author=author,
            version=version
        )
        
        # Create experiment directory
        exp_dir = self.experiments_dir / experiment_id
        exp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save metadata
        self._save_experiment_file(exp_dir, "metadata.json", metadata.to_dict())
        
        # Save hyperparameters
        self._save_experiment_file(exp_dir, "hyperparameters.json", hyperparameters.to_dict())
        
        # Update index
        self.index[experiment_id] = {
            'name': name,
            'status': 'registered',
            'created_at': now,
            'parent_ids': parent_ids or [],
            'tags': tags or []
        }
        self._save_index()
        
        logger.info(f"Registered experiment {experiment_id}: {name}")
        
        return experiment_id
    
    def _save_experiment_file(
        self,
        exp_dir: Path,
        filename: str,
        data: Dict[str, Any]
    ):
        """Save data to experiment file."""
        filepath = exp_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_experiment_file(
        self,
        exp_dir: Path,
        filename: str
    ) -> Dict[str, Any]:
        """Load data from experiment file."""
        filepath = exp_dir / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    
    def start_experiment(self, experiment_id: str) -> bool:
        """
        Start an experiment.
        
        Args:
            experiment_id: ID of experiment to start
            
        Returns:
            True if successful
        """
        exp_dir = self.experiments_dir / experiment_id
        if not exp_dir.exists():
            logger.error(f"Experiment {experiment_id} not found")
            return False
        
        # Update metadata
        metadata = self._load_experiment_file(exp_dir, "metadata.json")
        metadata['status'] = 'running'
        metadata['updated_at'] = datetime.now().isoformat()
        self._save_experiment_file(exp_dir, "metadata.json", metadata)
        
        # Update index
        self.index[experiment_id]['status'] = 'running'
        self._save_index()
        
        self.current_experiment_id = experiment_id
        
        logger.info(f"Started experiment {experiment_id}")
        return True
    
    def log_metrics(
        self,
        experiment_id: str,
        metrics: Dict[str, float],
        step: Optional[int] = None
    ):
        """
        Log metrics for an experiment.
        
        Args:
            experiment_id: Experiment ID
            metrics: Dictionary of metric names to values
            step: Optional step number
        """
        exp_dir = self.experiments_dir / experiment_id
        metrics_file = exp_dir / "metrics_history.json"
        
        # Load existing history
        history = []
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                history = json.load(f)
        
        # Add new entry
        entry = {
            'timestamp': datetime.now().isoformat(),
            'step': step,
            'metrics': metrics
        }
        history.append(entry)
        
        # Save
        with open(metrics_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def log_artifact(
        self,
        experiment_id: str,
        filepath: str,
        artifact_type: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log an artifact for an experiment.
        
        Args:
            experiment_id: Experiment ID
            filepath: Path to the artifact file
            artifact_type: Type of artifact ('model', 'dataset', 'config', etc.)
            name: Optional name (uses filename if None)
            metadata: Additional metadata
            
        Returns:
            Artifact ID
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Artifact not found: {filepath}")
        
        artifact_id = f"art_{uuid.uuid4().hex[:8]}"
        name = name or filepath.name
        
        # Copy artifact to storage
        artifact_dir = self.artifacts_dir / experiment_id
        artifact_dir.mkdir(parents=True, exist_ok=True)
        
        dest_path = artifact_dir / f"{artifact_id}_{filepath.name}"
        
        # Copy file
        import shutil
        shutil.copy2(filepath, dest_path)
        
        # Compute checksum
        checksum = self._compute_checksum(str(dest_path))
        size = dest_path.stat().st_size
        
        # Create artifact info
        artifact_info = ArtifactInfo(
            artifact_id=artifact_id,
            name=name,
            artifact_type=artifact_type,
            path=str(dest_path),
            checksum=checksum,
            size_bytes=size,
            created_at=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        # Save artifact metadata
        self._save_experiment_file(
            self.experiments_dir / experiment_id,
            f"artifact_{artifact_id}.json",
            artifact_info.to_dict()
        )
        
        logger.info(f"Logged artifact {artifact_id}: {name}")
        return artifact_id
    
    def save_checkpoint(
        self,
        experiment_id: str,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        epoch: int,
        metrics: Dict[str, float],
        is_best: bool = False
    ) -> str:
        """
        Save a model checkpoint.
        
        Args:
            experiment_id: Experiment ID
            model: PyTorch model
            optimizer: Optimizer
            epoch: Current epoch
            metrics: Current metrics
            is_best: Whether this is the best model so far
            
        Returns:
            Checkpoint path
        """
        checkpoint_dir = self.checkpoints_dir / experiment_id
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'metrics': metrics,
            'experiment_id': experiment_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save regular checkpoint
        checkpoint_path = checkpoint_dir / f"checkpoint_epoch_{epoch}.pt"
        torch.save(checkpoint, checkpoint_path)
        
        # Save as best if specified
        if is_best:
            best_path = checkpoint_dir / "best_model.pt"
            torch.save(checkpoint, best_path)
            logger.info(f"Saved best model at epoch {epoch}")
        
        logger.info(f"Saved checkpoint at epoch {epoch}")
        return str(checkpoint_path)
    
    def load_checkpoint(
        self,
        experiment_id: str,
        model: torch.nn.Module,
        optimizer: Optional[torch.optim.Optimizer] = None,
        checkpoint_path: Optional[str] = None,
        load_best: bool = False
    ) -> Dict[str, Any]:
        """
        Load a model checkpoint.
        
        Args:
            experiment_id: Experiment ID
            model: PyTorch model to load into
            optimizer: Optional optimizer to load into
            checkpoint_path: Specific checkpoint path
            load_best: Whether to load the best model
            
        Returns:
            Checkpoint dictionary
        """
        checkpoint_dir = self.checkpoints_dir / experiment_id
        
        if checkpoint_path:
            path = Path(checkpoint_path)
        elif load_best:
            path = checkpoint_dir / "best_model.pt"
        else:
            # Find latest checkpoint
            checkpoints = list(checkpoint_dir.glob("checkpoint_epoch_*.pt"))
            if not checkpoints:
                raise FileNotFoundError(f"No checkpoints found for {experiment_id}")
            path = max(checkpoints, key=lambda p: int(p.stem.split('_')[-1]))
        
        checkpoint = torch.load(path)
        model.load_state_dict(checkpoint['model_state_dict'])
        
        if optimizer and 'optimizer_state_dict' in checkpoint:
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        logger.info(f"Loaded checkpoint from {path}")
        return checkpoint
    
    def complete_experiment(
        self,
        experiment_id: str,
        final_metrics: Dict[str, float],
        training_history: Optional[Dict[str, List[float]]] = None,
        notes: Optional[str] = None
    ) -> ExperimentResult:
        """
        Mark experiment as completed.
        
        Args:
            experiment_id: Experiment ID
            final_metrics: Final metrics
            training_history: Training history
            notes: Optional notes
            
        Returns:
            ExperimentResult
        """
        exp_dir = self.experiments_dir / experiment_id
        
        # Load metadata
        metadata = self._load_experiment_file(exp_dir, "metadata.json")
        created_at = datetime.fromisoformat(metadata['created_at'])
        duration = (datetime.now() - created_at).total_seconds()
        
        # Find best epoch
        metrics_history = self._load_experiment_file(exp_dir, "metrics_history.json")
        best_epoch = 0
        best_loss = float('inf')
        
        for entry in metrics_history:
            if 'loss' in entry['metrics']:
                if entry['metrics']['loss'] < best_loss:
                    best_loss = entry['metrics']['loss']
                    best_epoch = entry['step'] or 0
        
        result = ExperimentResult(
            experiment_id=experiment_id,
            metrics=final_metrics,
            training_history=training_history or {},
            best_epoch=best_epoch,
            final_loss=final_metrics.get('loss', best_loss),
            completed_at=datetime.now().isoformat(),
            duration_seconds=duration
        )
        
        # Save result
        self._save_experiment_file(exp_dir, "result.json", result.to_dict())
        
        # Update metadata
        metadata['status'] = 'completed'
        metadata['updated_at'] = datetime.now().isoformat()
        if notes:
            metadata['notes'] = notes
        self._save_experiment_file(exp_dir, "metadata.json", metadata)
        
        # Update index
        self.index[experiment_id]['status'] = 'completed'
        self._save_index()
        
        logger.info(f"Completed experiment {experiment_id}")
        return result
    
    def get_lineage(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get the lineage of an experiment.
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            Lineage information
        """
        exp_dir = self.experiments_dir / experiment_id
        metadata = self._load_experiment_file(exp_dir, "metadata.json")
        
        lineage = {
            'experiment_id': experiment_id,
            'name': metadata.get('name', 'Unknown'),
            'parents': [],
            'children': [],
            'siblings': []
        }
        
        # Get parents
        for parent_id in metadata.get('parent_ids', []):
            parent_dir = self.experiments_dir / parent_id
            if parent_dir.exists():
                parent_meta = self._load_experiment_file(parent_dir, "metadata.json")
                lineage['parents'].append({
                    'id': parent_id,
                    'name': parent_meta.get('name', 'Unknown')
                })
        
        # Get children
        for exp_id, exp_info in self.index.items():
            if experiment_id in exp_info.get('parent_ids', []):
                lineage['children'].append({
                    'id': exp_id,
                    'name': exp_info.get('name', 'Unknown')
                })
        
        # Get siblings (experiments with same parents)
        parent_ids = set(metadata.get('parent_ids', []))
        for exp_id, exp_info in self.index.items():
            if exp_id != experiment_id:
                other_parents = set(exp_info.get('parent_ids', []))
                if parent_ids and other_parents and parent_ids == other_parents:
                    lineage['siblings'].append({
                        'id': exp_id,
                        'name': exp_info.get('name', 'Unknown')
                    })
        
        return lineage
    
    def compare_experiments(
        self,
        experiment_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple experiments.
        
        Args:
            experiment_ids: List of experiment IDs to compare
            
        Returns:
            Comparison results
        """
        comparison = {
            'experiments': [],
            'hyperparameters_diff': {},
            'metrics_comparison': {},
            'best_experiment': None
        }
        
        all_hyperparams = {}
        all_metrics = {}
        
        for exp_id in experiment_ids:
            exp_dir = self.experiments_dir / exp_id
            
            metadata = self._load_experiment_file(exp_dir, "metadata.json")
            hyperparams = self._load_experiment_file(exp_dir, "hyperparameters.json")
            result = self._load_experiment_file(exp_dir, "result.json")
            
            comparison['experiments'].append({
                'id': exp_id,
                'name': metadata.get('name', 'Unknown'),
                'status': metadata.get('status', 'Unknown')
            })
            
            all_hyperparams[exp_id] = hyperparams
            all_metrics[exp_id] = result.get('metrics', {})
        
        # Find differing hyperparameters
        if len(all_hyperparams) > 1:
            keys = set()
            for hp in all_hyperparams.values():
                keys.update(hp.keys())
            
            for key in keys:
                values = set()
                for hp in all_hyperparams.values():
                    val = hp.get(key)
                    if isinstance(val, list):
                        val = tuple(val)
                    values.add(str(val))
                
                if len(values) > 1:
                    comparison['hyperparameters_diff'][key] = {
                        exp_id: hp.get(key)
                        for exp_id, hp in all_hyperparams.items()
                    }
        
        # Compare metrics
        metric_names = set()
        for metrics in all_metrics.values():
            metric_names.update(metrics.keys())
        
        for metric in metric_names:
            comparison['metrics_comparison'][metric] = {
                exp_id: metrics.get(metric)
                for exp_id, metrics in all_metrics.items()
            }
        
        # Find best experiment (lowest loss)
        best_exp = None
        best_loss = float('inf')
        for exp_id, metrics in all_metrics.items():
            if 'loss' in metrics and metrics['loss'] < best_loss:
                best_loss = metrics['loss']
                best_exp = exp_id
        
        comparison['best_experiment'] = best_exp
        
        return comparison
    
    def reproduce_experiment(
        self,
        experiment_id: str,
        new_name: Optional[str] = None
    ) -> str:
        """
        Create a reproduction of an experiment.
        
        Args:
            experiment_id: ID of experiment to reproduce
            new_name: Name for new experiment
            
        Returns:
            New experiment ID
        """
        exp_dir = self.experiments_dir / experiment_id
        
        # Load original data
        metadata = self._load_experiment_file(exp_dir, "metadata.json")
        hyperparams = self._load_experiment_file(exp_dir, "hyperparameters.json")
        
        # Create new experiment
        new_id = self.register_experiment(
            name=new_name or f"Reproduction of {metadata['name']}",
            description=f"Reproduction of experiment {experiment_id}",
            hyperparameters=Hyperparameters.from_dict(hyperparams),
            parent_ids=[experiment_id],
            tags=metadata.get('tags', []) + ['reproduction'],
            author=metadata.get('author', 'unknown')
        )
        
        logger.info(f"Created reproduction {new_id} of {experiment_id}")
        return new_id
    
    def export_experiment(
        self,
        experiment_id: str,
        export_dir: str
    ) -> str:
        """
        Export an experiment to a directory.
        
        Args:
            experiment_id: Experiment ID
            export_dir: Directory to export to
            
        Returns:
            Export directory path
        """
        import shutil
        
        exp_dir = self.experiments_dir / experiment_id
        export_path = Path(export_dir) / experiment_id
        export_path.mkdir(parents=True, exist_ok=True)
        
        # Copy all files
        for file in exp_dir.glob("*"):
            if file.is_file():
                shutil.copy2(file, export_path / file.name)
        
        # Copy checkpoints
        checkpoint_dir = self.checkpoints_dir / experiment_id
        if checkpoint_dir.exists():
            shutil.copytree(checkpoint_dir, export_path / "checkpoints")
        
        # Copy artifacts
        artifact_dir = self.artifacts_dir / experiment_id
        if artifact_dir.exists():
            shutil.copytree(artifact_dir, export_path / "artifacts")
        
        logger.info(f"Exported experiment {experiment_id} to {export_path}")
        return str(export_path)
    
    def list_experiments(
        self,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        List experiments with optional filtering.
        
        Args:
            status: Filter by status
            tags: Filter by tags (any match)
            
        Returns:
            List of experiment info
        """
        results = []
        
        for exp_id, exp_info in self.index.items():
            # Filter by status
            if status and exp_info.get('status') != status:
                continue
            
            # Filter by tags
            if tags:
                exp_tags = set(exp_info.get('tags', []))
                if not exp_tags.intersection(tags):
                    continue
            
            results.append({
                'id': exp_id,
                'name': exp_info.get('name', 'Unknown'),
                'status': exp_info.get('status', 'Unknown'),
                'created_at': exp_info.get('created_at', 'Unknown'),
                'tags': exp_info.get('tags', [])
            })
        
        return results
    
    def get_experiment_info(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get full information about an experiment.
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            Full experiment information
        """
        exp_dir = self.experiments_dir / experiment_id
        
        info = {
            'metadata': self._load_experiment_file(exp_dir, "metadata.json"),
            'hyperparameters': self._load_experiment_file(exp_dir, "hyperparameters.json"),
            'result': self._load_experiment_file(exp_dir, "result.json"),
            'lineage': self.get_lineage(experiment_id)
        }
        
        # List artifacts
        artifact_files = list(exp_dir.glob("artifact_*.json"))
        info['artifacts'] = [
            self._load_experiment_file(exp_dir, f.name)
            for f in artifact_files
        ]
        
        # List checkpoints
        checkpoint_dir = self.checkpoints_dir / experiment_id
        if checkpoint_dir.exists():
            info['checkpoints'] = [
                str(f) for f in checkpoint_dir.glob("*.pt")
            ]
        else:
            info['checkpoints'] = []
        
        return info


if __name__ == "__main__":
    print("Experiment Lineage Tracking")
    print("=" * 50)
    
    # Create lineage tracker
    lineage = ExperimentLineage(
        storage_dir="experiment_lineage",
        project_name="quantum_vae"
    )
    
    # Create sample hyperparameters
    hp = Hyperparameters(
        latent_dim=32,
        input_dim=128,
        hidden_dims=[64, 32],
        learning_rate=1e-3,
        batch_size=32,
        epochs=100,
        optimizer="Adam",
        seed=42,
        device="cpu"
    )
    
    # Register experiment
    exp_id = lineage.register_experiment(
        name="test_experiment",
        description="Test experiment for lineage tracking",
        hyperparameters=hp,
        tags=["test", "demo"]
    )
    
    print(f"\nRegistered experiment: {exp_id}")
    
    # List experiments
    experiments = lineage.list_experiments()
    print(f"\nExperiments: {len(experiments)}")
    for exp in experiments:
        print(f"  - {exp['id']}: {exp['name']} ({exp['status']})")
    
    # Get lineage
    exp_lineage = lineage.get_lineage(exp_id)
    print(f"\nLineage: {json.dumps(exp_lineage, indent=2)}")
    
    print("\nLineage tracking ready.")