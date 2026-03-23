from train_vae import (
    load_sacred_datasets,
    load_real_consciousness_data,
    create_unified_dataset,
)

print("Loading datasets...")
sacred = load_sacred_datasets()
real = load_real_consciousness_data()
out = create_unified_dataset(sacred, real)
data = out[0] if isinstance(out, tuple) else out
print("Dataset ready, shape:", getattr(data, "shape", None))
assert hasattr(data, "shape"), "Expected unified dataset to be array-like with .shape"
print("✅ All functions working correctly!")
