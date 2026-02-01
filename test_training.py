from train_vae import load_sacred_datasets, load_real_consciousness_data, create_unified_dataset, train_vae
from vae_model import QuantumVAE
import torch
from torch.utils.data import DataLoader, TensorDataset

def _run_training_smoke_test():
    # Load sacred datasets (this may be large; keep it inside a callable so pytest won't execute it on import)
    print('Loading sacred datasets...')
    sacred_data = load_sacred_datasets()

    # Load real data
    print('Loading real consciousness data...')
    real_data = load_real_consciousness_data()

    # Create unified dataset
    print('Creating unified dataset...')
    unified_data = create_unified_dataset(sacred_data, real_data)
    print(f'Dataset shape: {unified_data.shape}')

    # Create model
    model = QuantumVAE(input_dim=unified_data.shape[1], latent_dim=64)
    print('Model created')

    # Create data loaders (small batch for testing)
    dataset = TensorDataset(torch.tensor(unified_data, dtype=torch.float32))
    train_loader = DataLoader(dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(dataset, batch_size=32, shuffle=False)

    print('Starting training smoke test...')
    # Train for just 1 epoch to keep the run-time short during manual invocation
    train_vae(model, train_loader, val_loader, num_epochs=1, device='cpu', save_path='test_model.pt')
    print('Training smoke test completed successfully!')


# Lightweight pytest-compatible check that doesn't trigger long-running operations
def test_training_smoke_imports():
    """Verify training functions are importable and callable without executing heavy work."""
    assert callable(load_sacred_datasets)
    assert callable(load_real_consciousness_data)
    assert callable(create_unified_dataset)
    assert callable(train_vae)


if __name__ == "__main__":
    # Run the smoke test only when executed explicitly
    _run_training_smoke_test()