#!/usr/bin/env python3
"""
Configuration Manager for Quantum Consciousness AGI
==================================================

Handles loading, validation, and management of configuration files.
Supports YAML, JSON, and environment variable overrides.
"""

import os
import yaml
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field, fields, is_dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Model architecture configuration."""
    input_dim: int = 128
    latent_dim: int = 32
    hidden_dim: int = 64
    sparsity_factor: float = 0.1


@dataclass
class TrainingConfig:
    """Training parameters configuration."""
    epochs: int = 200
    batch_size: int = 64
    learning_rate: float = 3e-4
    weight_decay: float = 1e-5
    early_stopping_patience: int = 30
    reduce_lr_patience: int = 15

    # Loss weights
    loss_weights: Dict[str, float] = field(default_factory=lambda: {
        'reconstruction': 1.0,
        'kl_divergence': 0.0008,
        'hamming': 0.3,
        'coherence': 0.1,
        'hardware': 0.01,
        'mixed_state': 0.1,
        'fidelity': 0.1,
        'entropy': 0.05
    })


@dataclass
class QuantumConfig:
    """Quantum computing configuration."""
    n_qubits: int = 6
    backend: str = "ibm_brisbane"
    shots: int = 8192
    coherence_time: float = 100e-6
    gate_fidelity_target: float = 0.999


@dataclass
class GoldenRatioConfig:
    """Golden ratio analysis configuration."""
    threshold: float = 0.05
    bootstrap_iterations: int = 10000
    permutation_iterations: int = 5000
    resonance_threshold: float = 0.7


@dataclass
class PathsConfig:
    """Directory paths configuration."""
    output_dir: str = "outputs"
    checkpoint_dir: str = "checkpoints"
    visualization_dir: str = "visualizations"
    data_dir: str = "data"
    log_dir: str = "logs"


@dataclass
class APIConfig:
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list = field(default_factory=lambda: ["*"])


@dataclass
class MonitoringConfig:
    """Performance monitoring configuration."""
    track_frequency: int = 5
    save_frequency: int = 10
    generate_plots: bool = True
    export_metrics: bool = True


@dataclass
class ArchiveConfig:
    """Quantum result archival configuration (replaces NFT)."""
    default_style: str = "quantum_consciousness"
    max_archives_per_request: int = 10
    storage_backend: str = "local"  # local, s3, zenodo
    archive_path: str = "archive"
    enable_verification: bool = True
    enable_provenance: bool = True


@dataclass
class QuantumConsciousnessConfig:
    """
    Main configuration class for Quantum Consciousness AGI.

    Combines all sub-configurations and provides methods for loading,
    validation, and environment variable overrides.
    """

    # Scientific constants
    golden_ratio: float = 1.618033988749895
    planck_constant: float = 6.62607015e-34
    boltzmann_constant: float = 1.380649e-23

    # Sub-configurations
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    quantum: QuantumConfig = field(default_factory=QuantumConfig)
    golden_ratio_analysis: GoldenRatioConfig = field(
        default_factory=GoldenRatioConfig
    )
    paths: PathsConfig = field(default_factory=PathsConfig)
    api: APIConfig = field(default_factory=APIConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    archive: ArchiveConfig = field(default_factory=ArchiveConfig)

    # General settings
    environment: str = "development"
    log_level: str = "INFO"
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    _provenance: Dict[str, str] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        """Initialize provenance for all default-backed fields."""
        self._initialize_default_provenance()

    @classmethod
    def from_yaml(
        cls,
        config_path: Union[str, Path],
    ) -> 'QuantumConsciousnessConfig':
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file

        Returns:
            QuantumConsciousnessConfig instance
        """
        config_path = Path(config_path)

        if not config_path.exists():
            logger.warning(
                "Config file %s not found, using defaults",
                config_path,
            )
            return cls()

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f) or {}

            logger.info("Loaded configuration from %s", config_path)
            return cls.from_dict(config_dict, source='yaml')

        except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
            logger.error("Failed to load config from %s: %s", config_path, exc)
            return cls()

    @classmethod
    def from_json(
        cls,
        config_path: Union[str, Path],
    ) -> 'QuantumConsciousnessConfig':
        """
        Load configuration from JSON file.

        Args:
            config_path: Path to JSON configuration file

        Returns:
            QuantumConsciousnessConfig instance
        """
        config_path = Path(config_path)

        if not config_path.exists():
            logger.warning(
                "Config file %s not found, using defaults",
                config_path,
            )
            return cls()

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)

            logger.info("Loaded configuration from %s", config_path)
            return cls.from_dict(config_dict, source='json')

        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            logger.error("Failed to load config from %s: %s", config_path, exc)
            return cls()

    @classmethod
    def from_dict(
        cls,
        config_dict: Dict[str, Any],
        source: str = 'dict',
    ) -> 'QuantumConsciousnessConfig':
        """
        Create configuration from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            QuantumConsciousnessConfig instance
        """
        instance = cls()

        for key in (
            'golden_ratio',
            'planck_constant',
            'boltzmann_constant',
            'environment',
        ):
            if key in config_dict:
                setattr(instance, key, config_dict[key])
                instance._set_provenance(key, source)

        nested_sections = {
            'model': instance.model,
            'training': instance.training,
            'quantum': instance.quantum,
            'golden_ratio_analysis': instance.golden_ratio_analysis,
            'paths': instance.paths,
            'api': instance.api,
            'monitoring': instance.monitoring,
            'archive': instance.archive,
            'nft': instance.archive,
        }

        for section_name, section_obj in nested_sections.items():
            section_values = config_dict.get(section_name)
            if not isinstance(section_values, dict):
                continue
            instance._apply_section_values(
                section_name,
                section_obj,
                section_values,
                source,
            )

        logging_config = config_dict.get('logging', {})
        if isinstance(logging_config, dict):
            if 'level' in logging_config:
                instance.log_level = logging_config['level']
                instance._set_provenance('log_level', source)
            if 'format' in logging_config:
                instance.log_format = logging_config['format']
                instance._set_provenance('log_format', source)

            return instance

    def _initialize_default_provenance(self) -> None:
        """Mark all leaf fields as default unless overridden later."""
        self._provenance.clear()
        self._mark_default_provenance(self)

    def _mark_default_provenance(self, obj: Any, prefix: str = "") -> None:
        """Recursively record default provenance for dataclass leaf fields."""
        for dataclass_field in fields(obj):
            if dataclass_field.name.startswith('_'):
                continue

            field_path = (
                f"{prefix}.{dataclass_field.name}"
                if prefix else dataclass_field.name
            )
            value = getattr(obj, dataclass_field.name)

            if is_dataclass(value):
                self._mark_default_provenance(value, field_path)
            else:
                self._provenance[field_path] = 'default'

    def _set_provenance(self, field_path: str, source: str) -> None:
        """Record where a field value came from."""
        self._provenance[field_path] = source

    def _apply_section_values(
        self,
        section_name: str,
        section_obj: Any,
        values: Dict[str, Any],
        source: str,
    ) -> None:
        """Apply nested config values and mark provenance."""
        provenance_section = (
            'archive' if section_name == 'nft' else section_name
        )
        for key, value in values.items():
            if hasattr(section_obj, key):
                setattr(section_obj, key, value)
                self._set_provenance(f"{provenance_section}.{key}", source)
            else:
                logger.warning(
                    "Unknown configuration key ignored: %s.%s",
                    section_name,
                    key,
                )

    def get_provenance(self) -> Dict[str, Any]:
        """Return provenance as a nested dictionary keyed by config path."""
        nested: Dict[str, Any] = {}
        for field_path, source in sorted(self._provenance.items()):
            current = nested
            path_parts = field_path.split('.')
            for part in path_parts[:-1]:
                current = current.setdefault(part, {})
            current[path_parts[-1]] = source
        return nested

    def apply_env_overrides(self) -> None:
        """
        Apply environment variable overrides.

        Environment variables should be prefixed with QUANTUM_AGI_
        Example: QUANTUM_AGI_MODEL_INPUT_DIM=256
        """
        prefix = "QUANTUM_AGI_"

        section_lookup = {
            'model': self.model,
            'training': self.training,
            'quantum': self.quantum,
            'golden_ratio_analysis': self.golden_ratio_analysis,
            'paths': self.paths,
            'api': self.api,
            'monitoring': self.monitoring,
            'archive': self.archive,
        }

        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue

            config_key = key[len(prefix):].lower()

            matched = False
            for section_name, section_obj in section_lookup.items():
                prefix_name = f"{section_name}_"
                if not config_key.startswith(prefix_name):
                    continue

                sub_key = config_key[len(prefix_name):]
                if hasattr(section_obj, sub_key):
                    converted = self._convert_env_value(value)
                    setattr(section_obj, sub_key, converted)
                    self._set_provenance(f"{section_name}.{sub_key}", 'env')
                    logger.info(
                        "Override %s.%s = %s",
                        section_name,
                        sub_key,
                        value,
                    )
                matched = True
                break

            if matched:
                continue

            if hasattr(self, config_key):
                setattr(self, config_key, self._convert_env_value(value))
                self._set_provenance(config_key, 'env')
                logger.info("Override %s = %s", config_key, value)

    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable string to appropriate type."""
        # Boolean conversion
        if value.lower() in ('true', 'yes', '1'):
            return True
        elif value.lower() in ('false', 'no', '0'):
            return False

        # Numeric conversion
        try:
            if any(marker in value.lower() for marker in ('.', 'e')):
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value

    def validate(self) -> bool:
        """
        Validate configuration parameters.

        Returns:
            True if configuration is valid, False otherwise
        """
        valid = True

        backend_pattern = re.compile(r'^[A-Za-z0-9._:-]+$')
        allowed_storage_backends = {'local', 's3', 'zenodo'}

        # Validate model parameters
        if self.model.input_dim <= 0:
            logger.error("model.input_dim must be positive")
            valid = False

        if (
            self.model.latent_dim <= 0
            or self.model.latent_dim >= self.model.input_dim
        ):
            logger.error(
                "model.latent_dim must be positive and less than input_dim"
            )
            valid = False

        if self.model.hidden_dim <= 0:
            logger.error("model.hidden_dim must be positive")
            valid = False

        if self.model.hidden_dim < self.model.latent_dim:
            logger.error(
                "model.hidden_dim must be greater than or equal to latent_dim"
            )
            valid = False

        if not 0 < self.model.sparsity_factor < 1:
            logger.error("model.sparsity_factor must be between 0 and 1")
            valid = False

        # Validate training parameters
        if self.training.epochs <= 0:
            logger.error("training.epochs must be positive")
            valid = False

        if self.training.batch_size <= 0:
            logger.error("training.batch_size must be positive")
            valid = False

        if not 0 < self.training.learning_rate < 1:
            logger.error("training.learning_rate must be between 0 and 1")
            valid = False

        if self.training.weight_decay < 0:
            logger.error("training.weight_decay must be non-negative")
            valid = False

        if self.training.early_stopping_patience <= 0:
            logger.error("training.early_stopping_patience must be positive")
            valid = False

        if self.training.reduce_lr_patience <= 0:
            logger.error("training.reduce_lr_patience must be positive")
            valid = False

        for loss_name, loss_weight in self.training.loss_weights.items():
            if loss_weight < 0:
                logger.error(
                    "training.loss_weights.%s must be non-negative",
                    loss_name,
                )
                valid = False

        # Validate quantum parameters
        if self.quantum.n_qubits <= 0:
            logger.error("quantum.n_qubits must be positive")
            valid = False

        if self.quantum.shots <= 0:
            logger.error("quantum.shots must be positive")
            valid = False

        if self.quantum.coherence_time <= 0:
            logger.error("quantum.coherence_time must be positive")
            valid = False

        if not 0 < self.quantum.gate_fidelity_target <= 1:
            logger.error(
                "quantum.gate_fidelity_target must be between 0 and 1"
            )
            valid = False

        if (
            not self.quantum.backend
            or not backend_pattern.match(self.quantum.backend)
        ):
            logger.error(
                "quantum.backend must be a non-empty backend identifier"
            )
            valid = False

        if not 0 < self.golden_ratio_analysis.threshold < 1:
            logger.error(
                "golden_ratio_analysis.threshold must be between 0 and 1"
            )
            valid = False

        if self.golden_ratio_analysis.bootstrap_iterations <= 0:
            logger.error(
                "golden_ratio_analysis.bootstrap_iterations must be positive"
            )
            valid = False

        if self.golden_ratio_analysis.permutation_iterations <= 0:
            logger.error(
                "golden_ratio_analysis.permutation_iterations must be positive"
            )
            valid = False

        if not 0 < self.golden_ratio_analysis.resonance_threshold <= 1:
            logger.error(
                "golden_ratio_analysis.resonance_threshold must be between "
                "0 and 1"
            )
            valid = False

        for path_name in (
            'output_dir',
            'checkpoint_dir',
            'visualization_dir',
            'data_dir',
            'log_dir',
        ):
            if not getattr(self.paths, path_name):
                logger.error("paths.%s must be non-empty", path_name)
                valid = False

        if not 1 <= self.api.port <= 65535:
            logger.error("api.port must be between 1 and 65535")
            valid = False

        if self.monitoring.track_frequency <= 0:
            logger.error("monitoring.track_frequency must be positive")
            valid = False

        if self.monitoring.save_frequency <= 0:
            logger.error("monitoring.save_frequency must be positive")
            valid = False

        if self.archive.max_archives_per_request <= 0:
            logger.error("archive.max_archives_per_request must be positive")
            valid = False

        if self.archive.storage_backend not in allowed_storage_backends:
            logger.error(
                "archive.storage_backend must be one of %s",
                sorted(allowed_storage_backends),
            )
            valid = False

        if not self.archive.archive_path:
            logger.error("archive.archive_path must be non-empty")
            valid = False

        if not self.environment:
            logger.error("environment must be non-empty")
            valid = False

        # Validate golden ratio
        if abs(self.golden_ratio - 1.618033988749895) > 0.01:
            logger.warning(
                "golden_ratio seems incorrect, should be approximately "
                "1.618033988749895"
            )

        return valid

    def create_directories(self) -> None:
        """Create all necessary directories specified in configuration."""
        directories = [
            self.paths.output_dir,
            self.paths.checkpoint_dir,
            self.paths.visualization_dir,
            self.paths.data_dir,
            self.paths.log_dir
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug("Ensured directory exists: %s", directory)

    def to_dict(self, include_provenance: bool = False) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Configuration dictionary
        """
        config_dict = {
            'golden_ratio': self.golden_ratio,
            'planck_constant': self.planck_constant,
            'boltzmann_constant': self.boltzmann_constant,
            'model': self.model.__dict__,
            'training': self.training.__dict__,
            'quantum': self.quantum.__dict__,
            'golden_ratio_analysis': self.golden_ratio_analysis.__dict__,
            'paths': self.paths.__dict__,
            'api': self.api.__dict__,
            'monitoring': self.monitoring.__dict__,
            'archive': self.archive.__dict__,
            'environment': self.environment,
            'logging': {
                'level': self.log_level,
                'format': self.log_format
            }
        }

        if include_provenance:
            config_dict['_provenance'] = self.get_provenance()

        return config_dict

    def save_yaml(
        self,
        output_path: Union[str, Path],
        include_provenance: bool = False,
    ) -> None:
        """
        Save configuration to YAML file.

        Args:
            output_path: Path to save configuration
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.to_dict(include_provenance=include_provenance),
                f,
                default_flow_style=False,
                indent=2,
                sort_keys=False,
            )

        logger.info("Configuration saved to %s", output_path)

    def __str__(self) -> str:
        """String representation of configuration."""
        return (
            "QuantumConsciousnessConfig(\n"
            f"  golden_ratio={self.golden_ratio:.12f},\n"
            f"  model={self.model},\n"
            f"  training={self.training},\n"
            f"  quantum={self.quantum},\n"
            f"  environment='{self.environment}'\n"
            ")"
        )


# Global configuration instance
_config: Optional[QuantumConsciousnessConfig] = None


def get_config(
    config_path: Optional[str] = None,
) -> QuantumConsciousnessConfig:
    """
    Get global configuration instance.

    Args:
        config_path: Optional path to configuration file

    Returns:
        QuantumConsciousnessConfig instance
    """
    global _config

    if _config is None:
        if config_path:
            _config = QuantumConsciousnessConfig.from_yaml(config_path)
        else:
            # Try default locations
            default_paths = [
                "agi_app/config/default.yaml",
                "config/default.yaml",
                "default.yaml"
            ]

            for path in default_paths:
                if Path(path).exists():
                    _config = QuantumConsciousnessConfig.from_yaml(path)
                    break
            else:
                logger.warning("No configuration file found, using defaults")
                _config = QuantumConsciousnessConfig()

        # Apply environment overrides and validate
        _config.apply_env_overrides()

        if not _config.validate():
            raise ValueError("Invalid configuration")

        _config.create_directories()

    return _config


def reset_config() -> None:
    """Reset global configuration instance."""
    global _config
    _config = None


if __name__ == "__main__":
    # Test configuration loading
    config = get_config()
    print(config)

    # Test saving
    config.save_yaml("test_config.yaml", include_provenance=True)
    print("Test configuration with provenance saved to test_config.yaml")
