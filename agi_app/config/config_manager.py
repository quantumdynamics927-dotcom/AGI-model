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
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
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
class NFTConfig:
    """NFT generation configuration."""
    default_style: str = "quantum_consciousness"
    max_generations_per_request: int = 10
    ipfs_gateway: str = "https://gateway.pinata.cloud"


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
    golden_ratio_analysis: GoldenRatioConfig = field(default_factory=GoldenRatioConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    api: APIConfig = field(default_factory=APIConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    nft: NFTConfig = field(default_factory=NFTConfig)
    
    # General settings
    environment: str = "development"
    log_level: str = "INFO"
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    
    @classmethod
    def from_yaml(cls, config_path: Union[str, Path]) -> 'QuantumConsciousnessConfig':
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            QuantumConsciousnessConfig instance
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"Config file {config_path} not found, using defaults")
            return cls()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
            
            logger.info(f"Loaded configuration from {config_path}")
            return cls.from_dict(config_dict)
            
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return cls()
    
    @classmethod
    def from_json(cls, config_path: Union[str, Path]) -> 'QuantumConsciousnessConfig':
        """
        Load configuration from JSON file.
        
        Args:
            config_path: Path to JSON configuration file
            
        Returns:
            QuantumConsciousnessConfig instance
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"Config file {config_path} not found, using defaults")
            return cls()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            logger.info(f"Loaded configuration from {config_path}")
            return cls.from_dict(config_dict)
            
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return cls()
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'QuantumConsciousnessConfig':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            QuantumConsciousnessConfig instance
        """
        # Extract top-level configs
        model_config = config_dict.get('model', {})
        training_config = config_dict.get('training', {})
        quantum_config = config_dict.get('quantum', {})
        golden_ratio_config = config_dict.get('golden_ratio_analysis', {})
        paths_config = config_dict.get('paths', {})
        api_config = config_dict.get('api', {})
        monitoring_config = config_dict.get('monitoring', {})
        nft_config = config_dict.get('nft', {})
        
        # Create configuration instances
        return cls(
            # Scientific constants
            golden_ratio=config_dict.get('golden_ratio', 1.618033988749895),
            planck_constant=config_dict.get('planck_constant', 6.62607015e-34),
            boltzmann_constant=config_dict.get('boltzmann_constant', 1.380649e-23),
            
            # Sub-configurations
            model=ModelConfig(**model_config),
            training=TrainingConfig(**training_config),
            quantum=QuantumConfig(**quantum_config),
            golden_ratio_analysis=GoldenRatioConfig(**golden_ratio_config),
            paths=PathsConfig(**paths_config),
            api=APIConfig(**api_config),
            monitoring=MonitoringConfig(**monitoring_config),
            nft=NFTConfig(**nft_config),
            
            # General settings
            environment=config_dict.get('environment', 'development'),
            log_level=config_dict.get('logging', {}).get('level', 'INFO'),
            log_format=config_dict.get('logging', {}).get('format', 
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
    
    def apply_env_overrides(self) -> None:
        """
        Apply environment variable overrides.
        
        Environment variables should be prefixed with QUANTUM_AGI_
        Example: QUANTUM_AGI_MODEL_INPUT_DIM=256
        """
        prefix = "QUANTUM_AGI_"
        
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue
                
            config_key = key[len(prefix):].lower()
            
            # Apply overrides based on nested keys
            if config_key.startswith('model_'):
                sub_key = config_key[6:]
                if hasattr(self.model, sub_key):
                    setattr(self.model, sub_key, self._convert_env_value(value))
                    logger.info(f"Override model.{sub_key} = {value}")
                    
            elif config_key.startswith('training_'):
                sub_key = config_key[9:]
                if hasattr(self.training, sub_key):
                    setattr(self.training, sub_key, self._convert_env_value(value))
                    logger.info(f"Override training.{sub_key} = {value}")
                    
            elif config_key.startswith('quantum_'):
                sub_key = config_key[8:]
                if hasattr(self.quantum, sub_key):
                    setattr(self.quantum, sub_key, self._convert_env_value(value))
                    logger.info(f"Override quantum.{sub_key} = {value}")
                    
            elif config_key.startswith('api_'):
                sub_key = config_key[4:]
                if hasattr(self.api, sub_key):
                    setattr(self.api, sub_key, self._convert_env_value(value))
                    logger.info(f"Override api.{sub_key} = {value}")
                    
            elif hasattr(self, config_key):
                setattr(self, config_key, self._convert_env_value(value))
                logger.info(f"Override {config_key} = {value}")
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable string to appropriate type."""
        # Boolean conversion
        if value.lower() in ('true', 'yes', '1'):
            return True
        elif value.lower() in ('false', 'no', '0'):
            return False
        
        # Numeric conversion
        try:
            if '.' in value:
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
        
        # Validate model parameters
        if self.model.input_dim <= 0:
            logger.error("model.input_dim must be positive")
            valid = False
            
        if self.model.latent_dim <= 0 or self.model.latent_dim >= self.model.input_dim:
            logger.error("model.latent_dim must be positive and less than input_dim")
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
        
        # Validate quantum parameters
        if self.quantum.n_qubits <= 0:
            logger.error("quantum.n_qubits must be positive")
            valid = False
            
        if self.quantum.shots <= 0:
            logger.error("quantum.shots must be positive")
            valid = False
        
        # Validate golden ratio
        if abs(self.golden_ratio - 1.618033988749895) > 0.01:
            logger.warning("golden_ratio seems incorrect, should be approximately 1.618033988749895")
        
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
            logger.debug(f"Ensured directory exists: {directory}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return {
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
            'nft': self.nft.__dict__,
            'environment': self.environment,
            'logging': {
                'level': self.log_level,
                'format': self.log_format
            }
        }
    
    def save_yaml(self, output_path: Union[str, Path]) -> None:
        """
        Save configuration to YAML file.
        
        Args:
            output_path: Path to save configuration
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
        
        logger.info(f"Configuration saved to {output_path}")
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"QuantumConsciousnessConfig(\n" + \
               f"  golden_ratio={self.golden_ratio:.12f},\n" + \
               f"  model={self.model},\n" + \
               f"  training={self.training},\n" + \
               f"  quantum={self.quantum},\n" + \
               f"  environment='{self.environment}'\n" + \
               f")"


# Global configuration instance
_config: Optional[QuantumConsciousnessConfig] = None


def get_config(config_path: Optional[str] = None) -> QuantumConsciousnessConfig:
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
    config.save_yaml("test_config.yaml")
    print("Test configuration saved to test_config.yaml")