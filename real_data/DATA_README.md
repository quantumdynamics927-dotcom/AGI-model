# Real Data Directory

## Privacy Notice

This repository **does not contain any real biometric or personal data**.

All EEG, fMRI, and biological datasets are kept **local only** and are **not committed to version control**.

---

## Using Your Own Data

To use this project with your own consciousness/neuroscience datasets:

### 1. Prepare Your Data

Place your data files in the `real_data/` directory with the following structure:

```
real_data/
├── eeg/
│   └── subject_XXX_eeg.npy          # EEG timeseries data
├── fmri/
│   └── subject_XXX_features.npy     # fMRI feature vectors
├── dna/
│   └── sequence_data.npy            # DNA sequence encodings (if applicable)
├── behavioral/
│   └── behavioral_metrics.csv       # Behavioral/cognitive scores
├── doc_labels.csv                    # Subject IDs + consciousness states
└── processed_real_data.npz          # Combined preprocessed dataset
```

### 2. Expected Data Formats

**EEG Data:**
- Format: `.npy` (NumPy array)
- Shape: `(n_samples, n_channels, n_timepoints)`
- Channels: Standard 10-20 system recommended
- Sampling rate: 250-1000 Hz

**fMRI Data:**
- Format: `.npy` (NumPy array)
- Shape: `(n_samples, n_features)`
- Features: Pre-extracted ROI activations or voxel timeseries

**Labels CSV:**
- Columns: `subject_id`, `consciousness_state`
- States: `UWS` (unresponsive), `MCS` (minimally conscious), `Healthy`

### 3. Privacy & Ethics

**IMPORTANT:**
- **Never commit real biometric data to version control**
- Add `real_data/**/*.npy` and `real_data/**/*.npz` to your `.gitignore`
- Ensure you have proper ethical approval and informed consent for any human data
- Anonymize all subject identifiers (use numeric IDs only)

### 4. Running Training

Once your data is in place:

```bash
python train_vae.py --data_path real_data/
```

The VAE will automatically load from `real_data/` if available, otherwise it will use synthetic data from `sacred_datasets/`.

---

## Synthetic Data (Included)

For testing without real data, synthetic consciousness datasets are provided in:
- `sacred_datasets/` — Phi-harmonic synthetic quantum states
- Scripts automatically generate demo data if `real_data/` is empty

---

## Questions?

See `SECURITY_PRIVACY.md` in the root directory for full data handling guidelines.
