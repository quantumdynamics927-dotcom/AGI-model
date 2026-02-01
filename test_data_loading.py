from train_vae import load_sacred_datasets, load_real_consciousness_data, create_unified_dataset
print('Loading datasets...')
sacred = load_sacred_datasets()
real = load_real_consciousness_data()
data = create_unified_dataset(sacred, real)
print('Dataset ready, shape:', data.shape)
print('✅ All functions working correctly!')