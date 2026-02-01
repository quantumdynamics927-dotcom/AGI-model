"""
Phi-Aware Data Sampler

Custom data samplers that prioritize samples based on their phi alignment,
enabling curriculum learning for golden ratio optimization.

Features:
- Priority sampling based on phi scores
- Curriculum learning with progressive difficulty
- Balanced sampling across consciousness archetypes
- Integration with PyTorch DataLoader
"""

import torch
from torch.utils.data import Sampler, Dataset
import numpy as np
from typing import Iterator, List, Optional, Dict, Callable

# Golden ratio constant
PHI = 1.618033988749895


class PhiAwareSampler(Sampler):
    """
    Data sampler that prioritizes samples based on phi alignment.

    Can be used for curriculum learning, starting with high-phi samples
    and progressively including harder examples.

    Parameters
    ----------
    dataset : Dataset
        PyTorch dataset to sample from
    phi_scores : array-like or None
        Phi alignment scores for each sample (0-1). Higher = more phi-aligned.
        If None, must call update_phi_scores() before use.
    curriculum_epochs : int, default=50
        Number of epochs over which to transition from easy to hard
    strategy : str, default='curriculum'
        Sampling strategy:
        - 'curriculum': Start with high-phi, gradually include all
        - 'priority': Always prioritize high-phi samples
        - 'balanced': Ensure balanced representation
        - 'random': Standard random sampling (baseline)
    batch_size : int, default=64
        Batch size for sampling calculations
    random_state : int, optional
        Random seed for reproducibility

    Example
    -------
    >>> sampler = PhiAwareSampler(dataset, phi_scores, curriculum_epochs=50)
    >>> loader = DataLoader(dataset, batch_size=64, sampler=sampler)
    >>> for epoch in range(100):
    ...     sampler.set_epoch(epoch)
    ...     for batch in loader:
    ...         # Train on batch
    """

    def __init__(
        self,
        dataset: Dataset,
        phi_scores: Optional[np.ndarray] = None,
        curriculum_epochs: int = 50,
        strategy: str = 'curriculum',
        batch_size: int = 64,
        random_state: Optional[int] = 42
    ):
        self.dataset = dataset
        self.n_samples = len(dataset)
        self.curriculum_epochs = curriculum_epochs
        self.strategy = strategy
        self.batch_size = batch_size
        self.random_state = random_state

        # Initialize RNG
        self.rng = np.random.RandomState(random_state)

        # Phi scores
        if phi_scores is not None:
            self.phi_scores = np.array(phi_scores)
            self._validate_scores()
        else:
            # Default: uniform scores (no priority)
            self.phi_scores = np.ones(self.n_samples)

        # Current epoch tracking
        self.current_epoch = 0

        # Precompute sorted indices by phi score
        self._update_sorted_indices()

    def _validate_scores(self):
        """Validate phi scores array."""
        if len(self.phi_scores) != self.n_samples:
            raise ValueError(
                f"phi_scores length ({len(self.phi_scores)}) must match "
                f"dataset length ({self.n_samples})"
            )

    def _update_sorted_indices(self):
        """Update sorted indices after phi score changes."""
        # Sort by phi score (descending - highest first)
        self.sorted_indices = np.argsort(-self.phi_scores)

        # Compute percentile ranks
        self.percentile_ranks = np.zeros(self.n_samples)
        for rank, idx in enumerate(self.sorted_indices):
            self.percentile_ranks[idx] = rank / self.n_samples

    def update_phi_scores(self, phi_scores: np.ndarray):
        """
        Update phi scores for all samples.

        Parameters
        ----------
        phi_scores : ndarray
            New phi scores for each sample
        """
        self.phi_scores = np.array(phi_scores)
        self._validate_scores()
        self._update_sorted_indices()

    def set_epoch(self, epoch: int):
        """
        Set current epoch for curriculum progression.

        Parameters
        ----------
        epoch : int
            Current training epoch
        """
        self.current_epoch = epoch

    def __iter__(self) -> Iterator[int]:
        """Generate sample indices based on strategy."""
        if self.strategy == 'random':
            yield from self._random_sampling()
        elif self.strategy == 'curriculum':
            yield from self._curriculum_sampling()
        elif self.strategy == 'priority':
            yield from self._priority_sampling()
        elif self.strategy == 'balanced':
            yield from self._balanced_sampling()
        else:
            yield from self._random_sampling()

    def __len__(self) -> int:
        """Return number of samples."""
        return self.n_samples

    def _random_sampling(self) -> Iterator[int]:
        """Standard random sampling."""
        indices = self.rng.permutation(self.n_samples)
        yield from indices

    def _curriculum_sampling(self) -> Iterator[int]:
        """
        Curriculum-based sampling.

        Starts with easiest (highest phi) samples and gradually
        includes harder samples as training progresses.
        """
        # Progress: 0 at start, 1 after curriculum_epochs
        progress = min(1.0, self.current_epoch / max(1, self.curriculum_epochs))

        # Determine how many samples to include
        # Start with top 20%, gradually include all
        min_fraction = 0.2
        include_fraction = min_fraction + (1.0 - min_fraction) * progress

        n_include = max(self.batch_size, int(self.n_samples * include_fraction))

        # Sample from the included portion
        included_indices = self.sorted_indices[:n_include]
        sampled_indices = self.rng.choice(
            included_indices,
            size=self.n_samples,
            replace=True
        )

        yield from sampled_indices

    def _priority_sampling(self) -> Iterator[int]:
        """
        Priority-based sampling.

        Samples with probability proportional to phi score.
        """
        # Convert scores to probabilities
        scores = self.phi_scores + 0.1  # Add small constant to avoid zero prob
        probs = scores / scores.sum()

        indices = self.rng.choice(
            self.n_samples,
            size=self.n_samples,
            replace=True,
            p=probs
        )

        yield from indices

    def _balanced_sampling(self) -> Iterator[int]:
        """
        Balanced sampling across phi score ranges.

        Ensures representation from low, medium, and high phi samples.
        """
        # Divide into terciles
        tercile_size = self.n_samples // 3

        high_phi = self.sorted_indices[:tercile_size]
        medium_phi = self.sorted_indices[tercile_size:2 * tercile_size]
        low_phi = self.sorted_indices[2 * tercile_size:]

        # Sample equal numbers from each tercile
        samples_per_tercile = self.n_samples // 3

        high_samples = self.rng.choice(high_phi, size=samples_per_tercile, replace=True)
        med_samples = self.rng.choice(medium_phi, size=samples_per_tercile, replace=True)
        low_samples = self.rng.choice(low_phi, size=samples_per_tercile, replace=True)

        # Combine and shuffle
        all_samples = np.concatenate([high_samples, med_samples, low_samples])
        self.rng.shuffle(all_samples)

        yield from all_samples


class ConsciousnessArchetypeSampler(Sampler):
    """
    Sampler that balances across consciousness archetypes.

    Ensures each batch contains samples from different consciousness
    types (baseline, focused, creative, transcendent, chaotic).

    Parameters
    ----------
    dataset : Dataset
        PyTorch dataset
    archetype_labels : array-like
        Archetype label for each sample (0-4 or string labels)
    samples_per_archetype : int, default=None
        Samples per archetype per epoch. If None, uses full dataset.
    random_state : int, optional
        Random seed
    """

    ARCHETYPE_NAMES = ['baseline', 'focused', 'creative', 'transcendent', 'chaotic']

    def __init__(
        self,
        dataset: Dataset,
        archetype_labels: np.ndarray,
        samples_per_archetype: Optional[int] = None,
        random_state: Optional[int] = 42
    ):
        self.dataset = dataset
        self.n_samples = len(dataset)
        self.random_state = random_state
        self.rng = np.random.RandomState(random_state)

        # Convert string labels to integers if needed
        if isinstance(archetype_labels[0], str):
            self.archetype_labels = np.array([
                self.ARCHETYPE_NAMES.index(label) if label in self.ARCHETYPE_NAMES else 0
                for label in archetype_labels
            ])
        else:
            self.archetype_labels = np.array(archetype_labels)

        # Find indices for each archetype
        self.archetype_indices = {}
        for i, name in enumerate(self.ARCHETYPE_NAMES):
            self.archetype_indices[name] = np.where(self.archetype_labels == i)[0]

        # Samples per archetype
        if samples_per_archetype is None:
            # Use minimum class size
            min_size = min(len(idx) for idx in self.archetype_indices.values() if len(idx) > 0)
            self.samples_per_archetype = max(1, min_size)
        else:
            self.samples_per_archetype = samples_per_archetype

    def __iter__(self) -> Iterator[int]:
        """Generate balanced indices."""
        samples = []

        for name, indices in self.archetype_indices.items():
            if len(indices) == 0:
                continue

            # Sample with replacement if needed
            replace = len(indices) < self.samples_per_archetype
            selected = self.rng.choice(
                indices,
                size=self.samples_per_archetype,
                replace=replace
            )
            samples.extend(selected)

        # Shuffle combined samples
        samples = np.array(samples)
        self.rng.shuffle(samples)

        yield from samples

    def __len__(self) -> int:
        """Return total samples per epoch."""
        n_archetypes = sum(1 for idx in self.archetype_indices.values() if len(idx) > 0)
        return self.samples_per_archetype * n_archetypes


def compute_phi_scores_for_dataset(
    model,
    dataset: Dataset,
    batch_size: int = 64,
    threshold: float = 0.1
) -> np.ndarray:
    """
    Compute phi scores for all samples in a dataset.

    Parameters
    ----------
    model : nn.Module
        VAE model with encode() method
    dataset : Dataset
        PyTorch dataset
    batch_size : int, default=64
        Batch size for encoding
    threshold : float, default=0.1
        Threshold for phi proximity

    Returns
    -------
    ndarray
        Phi scores for each sample (0-1)
    """
    from torch.utils.data import DataLoader

    model.eval()
    phi_scores = []

    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    with torch.no_grad():
        for batch in loader:
            if isinstance(batch, (list, tuple)):
                batch = batch[0]

            # Encode to get latent codes
            mu, _ = model.encode(batch)

            # Compute phi score for each sample in batch
            for i in range(mu.shape[0]):
                sample = mu[i]
                score = _compute_sample_phi_score(sample, threshold)
                phi_scores.append(score)

    return np.array(phi_scores)


def _compute_sample_phi_score(latent: torch.Tensor, threshold: float) -> float:
    """Compute phi score for a single sample."""
    if latent.numel() < 2:
        return 0.0

    # Compute ratios between adjacent dimensions
    ratios = torch.abs(latent[1:]) / (torch.abs(latent[:-1]) + 1e-10)
    proximity = torch.abs(ratios - PHI)

    # Score = fraction within threshold
    score = (proximity < threshold).float().mean().item()

    return score


class DynamicPhiSampler(Sampler):
    """
    Sampler that updates phi scores during training.

    Recomputes phi scores periodically using the current model state,
    enabling truly adaptive sampling.

    Parameters
    ----------
    dataset : Dataset
        PyTorch dataset
    model : nn.Module
        VAE model for computing phi scores
    update_frequency : int, default=10
        Update phi scores every N epochs
    strategy : str, default='priority'
        Base sampling strategy
    random_state : int, optional
        Random seed
    """

    def __init__(
        self,
        dataset: Dataset,
        model,
        update_frequency: int = 10,
        strategy: str = 'priority',
        random_state: Optional[int] = 42
    ):
        self.dataset = dataset
        self.model = model
        self.update_frequency = update_frequency
        self.strategy = strategy
        self.random_state = random_state

        self.n_samples = len(dataset)
        self.rng = np.random.RandomState(random_state)

        # Initialize with uniform scores
        self.phi_scores = np.ones(self.n_samples)
        self.current_epoch = 0
        self.last_update_epoch = -update_frequency  # Force initial update

        # Create internal sampler
        self._sampler = PhiAwareSampler(
            dataset,
            self.phi_scores,
            strategy=strategy,
            random_state=random_state
        )

    def set_epoch(self, epoch: int):
        """
        Set current epoch and update scores if needed.

        Parameters
        ----------
        epoch : int
            Current training epoch
        """
        self.current_epoch = epoch
        self._sampler.set_epoch(epoch)

        # Update phi scores periodically
        if epoch - self.last_update_epoch >= self.update_frequency:
            self._update_scores()
            self.last_update_epoch = epoch

    def _update_scores(self):
        """Recompute phi scores using current model."""
        self.phi_scores = compute_phi_scores_for_dataset(
            self.model,
            self.dataset
        )
        self._sampler.update_phi_scores(self.phi_scores)

    def __iter__(self) -> Iterator[int]:
        """Generate indices using internal sampler."""
        return iter(self._sampler)

    def __len__(self) -> int:
        """Return number of samples."""
        return self.n_samples

    def get_phi_scores(self) -> np.ndarray:
        """Get current phi scores."""
        return self.phi_scores.copy()
