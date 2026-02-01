import os
import yaml

DEFAULTS = {
    'data': {
        'train_path': 'real_data/',
        'synthetic_path': 'sacred_datasets/',
        'input_dim': 128,
        'latent_dim': 32
    },
    'training': {
        'epochs': 200,
        'batch_size': 64,
        'learning_rate': 3e-4,
        'device': 'cpu',
        'random_seed': 42
    },
    'safety': {
        # Disallow remote uploads by default; can be enabled with TMTOS_ALLOW_UPLOAD='true'
        'allow_upload': False,
        # Default local delivery directory for artifacts and certificates
        'delivery_root': 'nft_metadata/',
        # Enforce that delivery roots are local filesystem paths (no http/s3/etc.)
        'enforce_local_paths': True
    }
} 


def load_config(path='config.yaml'):
    """Load configuration from YAML file and merge with defaults."""
    config = DEFAULTS.copy()
    if os.path.exists(path):
        with open(path, 'r') as f:
            loaded = yaml.safe_load(f)
        # shallow merge for simplicity
        for k, v in (loaded or {}).items():
            if isinstance(v, dict) and k in config:
                config[k].update(v)
            else:
                config[k] = v
    return config


if __name__ == '__main__':
    cfg = load_config()
    print('Loaded configuration:')
    print(cfg)
