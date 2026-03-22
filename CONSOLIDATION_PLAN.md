# Codebase Consolidation Plan - Quantum Consciousness AGI

## BACKUP STATUS ✅
- **Quantum files backed up**: quantum_results_backup_20260322_024147.tar.gz (253K)
- **Inventory created**: quantum_files_inventory.txt (27 files)
- **Backup verified**: ✓ Ready for safe consolidation

## NEW DIRECTORY STRUCTURE

```
quantum-consciousness-agi/
├── quantum/                          # QUANTUM RESULTS - PROTECTED
│   ├── results/                      # Quantum job results (JSON)
│   │   ├── ibm_hardware/            # IBM hardware aggregates
│   │   ├── dna_circuits/            # DNA 34bp results
│   │   ├── teleportation/           # Teleportation experiments
│   │   └── autonomous/              # Autonomous discoveries
│   ├── circuits/                    # Quantum circuits (QASM)
│   └── analysis/                    # Quantum analysis scripts
│
├── core/                            # Core VAE and models
│   ├── models/
│   │   ├── vae_model.py
│   │   ├── quantum_core.py
│   │   └── consciousness_link.py
│   ├── training/
│   │   ├── train_vae.py
│   │   └── train_utils.py
│   └── utils/
│       └── loss_functions.py
│
├── agents/                          # Three-agent pipeline
│   ├── dna/
│   │   ├── dna_agent.py
│   │   └── dna_analyzer.py
│   ├── phi/
│   │   ├── phi_agent.py
│   │   └── iit_calculator.py
│   └── qnn/
│       ├── qnn_agent.py
│       └── hybrid_network.py
│
├── nodes/                           # Metatron system (13 nodes)
│   ├── node1_tmt_os.py
│   ├── node2_cybershield.py
│   ├── node5_molecular_geometry.py
│   ├── node6_data_provenance.py
│   ├── node9_qvae_bridge.py
│   ├── node10_biodigital.py
│   ├── node11_frequency_master.py
│   ├── node12_neural_synapse.py
│   ├── node13_metatron.py
│   └── node_controller.py
│
├── consciousness/                   # IIT and complexity
│   ├── iit/
│   │   ├── integrated_information.py
│   │   └── complexity_measures.py
│   └── analysis/
│       ├── golden_ratio/
│       └── complexity/
│
├── data/                            # Datasets
│   ├── raw/
│   │   ├── real_data/
│   │   └── sacred_datasets/
│   └── processed/
│       └── unified/
│
├── api/                             # FastAPI services
│   ├── main.py
│   ├── websocket_bridge.py
│   └── routes/
│       ├── consciousness.py
│       └── quantum.py
│
├── dashboard/                       # Streamlit UI
│   └── app.py
│
├── tests/                           # Comprehensive tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/                            # Documentation
│   ├── architecture.md
│   ├── api/
│   └── tutorials/
│
└── configs/                         # Configuration files
    ├── default.yaml
    ├── production.yaml
    └── test.yaml
```

## FILE MAPPING - QUANTUM RESULTS (PROTECTED)

### Move to `quantum/results/ibm_hardware/`
- `ibm_hardware_aggregate_20260202_040836.json` → `quantum/results/ibm_hardware/aggregate_20260202_040836.json`
- `ibm_v21_optimized_aggregate_20260202_051029.json` → `quantum/results/ibm_hardware/v21_optimized_20260202_051029.json`

### Move to `quantum/results/dna_circuits/`
- `dna_34bp_results/dna_agent_report_20260310_210905.json` → `quantum/results/dna_circuits/agent_report_20260310_210905.json`
- `dna_quantum_analysis_results.json` → `quantum/results/dna_circuits/analysis_results.json`

### Move to `quantum/results/teleportation/`
- `quantum_teleportation_analysis.json` → `quantum/results/teleportation/analysis.json`
- `xy8_hardware_analysis.json` → `quantum/results/teleportation/xy8_hardware.json`

### Move to `quantum/results/autonomous/`
- `autonomous_data/discoveries_*.json` (16 files) → `quantum/results/autonomous/`
- `autonomous_data/toroidal_wormhole_results.json` → `quantum/results/autonomous/toroidal_wormhole_results.json`
- `autonomous_data/toroidal_wormhole_scan_summary.json` → `quantum/results/autonomous/toroidal_wormhole_scan_summary.json`

### Move to `quantum/results/misc/`
- `quantum_fingerprint_analysis.json` → `quantum/results/misc/fingerprint_analysis.json`
- `sacred_datasets/quantum_transport_spectra.json` → `quantum/results/misc/transport_spectra.json`

### Move to `quantum/circuits/`
- `wormhole_metatron_ibm_enhanced_v2.qasm` → `quantum/circuits/wormhole_metatron_enhanced_v2.qasm`
- `wormhole_metatron_ibm_hardware.qasm` → `quantum/circuits/wormhole_metatron_hardware.qasm`

### Move to `quantum/analysis/`
- `analyze_ibm_decoherence_jobs.py` → `quantum/analysis/ibm_decoherence.py`
- `analyze_ibm_enhanced_results.py` → `quantum/analysis/ibm_enhanced.py`
- `analyze_ibm_hardware_jobs.py` → `quantum/analysis/ibm_hardware.py`
- `analyze_ibm_wormhole_results.py` → `quantum/analysis/ibm_wormhole.py`
- `analyze_quantum_jobs.py` → `quantum/analysis/job_analyzer.py`
- `analyze_teleportation_job.py` → `quantum/analysis/teleportation.py`
- `analyze_v21_jobs.py` → `quantum/analysis/v21_jobs.py`

## FILE MAPPING - CORE MODULES

### Move to `core/models/`
- `vae_model.py`
- `quantum_consciousness_link.py`
- `quantum_consciousness_link_focused.py`
- `latent_analysis.py`
- `vae_model.py`

### Move to `core/training/`
- `train_vae.py`
- `train_vae_enhanced.py` (if exists)

### Move to `core/utils/`
- `dl_qmc.py`
- `check_resonance.py`

## FILE MAPPING - AGENTS

### Move to `agents/dna/`
- `agi_scripts/dna_agent.py`
- `TMT_DNA_Comprehensive_Analysis.py`
- `TMT_God_Gene_Test.py`

### Move to `agents/phi/`
- `agi_scripts/phi_agent.py`
- `consciousness_complexity_validation.py`
- `phi_artifact_analysis.json`

### Move to `agents/qnn/`
- `agi_scripts/qnn_agent.py`
- `airllm_neural_backbone.py`
- `enhanced_airllm_consciousness.py`

## FILE MAPPING - NODES (13 Metatron Nodes)

### Already exist as separate files:
- `node10_biodigital.py` → `nodes/node10_biodigital.py`
- `node11_frequency_master.py` → `nodes/node11_frequency_master.py`
- `node12_neural_synapse.py` → `nodes/node12_neural_synapse.py`
- `node_controller.py` → `nodes/node_controller.py`
- `metatron_nervous_system.py` → `nodes/metatron_coordinator.py`

### Need to create from integrations:
- `integrations/cybershield_adapter.py` → `nodes/node2_cybershield.py`
- `molecular_geometry/` → `nodes/node5_molecular_geometry/`
- `data_provenance/` → `nodes/node6_data_provenance/`
- `integrations/quantum_observer.py` → `nodes/node8_quantum_observer.py`
- `qvae_bridge.py` → `nodes/node9_qvae_bridge.py`

## SAFETY PROTOCOLS

### Before Each Move:
1. ✅ Verify file exists at source
2. ✅ Create target directory if needed
3. ✅ Copy file (don't move initially)
4. ✅ Verify copy integrity (size, json validation)
5. ✅ Update import paths in referencing files
6. ✅ Run quick import test
7. ✅ Only then remove source (after full verification)

### Quantum Results Protection:
- **NEVER delete** quantum JSON files from source until triple-verified
- **Keep original backup** until consolidation is complete
- **Validate JSON integrity** after each move: `python -m json.tool file.json > /dev/null`
- **Check file sizes** match before and after move
- **Verify no data loss** by comparing key metrics

### Rollback Plan:
If anything goes wrong:
1. Restore from backup: `tar -xzf quantum_results_backup_*.tar.gz`
2. Verify restoration: Compare file counts and sizes
3. Document the issue before retrying

## INTEGRITY VERIFICATION

### After Consolidation:
1. **Count files**: Verify 27 quantum files in new location
2. **Validate JSON**: All JSON files parse correctly
3. **Check references**: No broken imports in Python files
4. **Run smoke tests**: `python -c "import quantum.results.ibm_hardware"`
5. **Compare metrics**: Key quantum metrics unchanged

## NEXT STEPS

### Phase 1: Create Structure ✅ (DONE)
- [x] Backup quantum files
- [x] Create new directory structure
- [x] Write consolidation plan

### Phase 2: Move Quantum Files (PROTECTED)
- [ ] Move IBM hardware results
- [ ] Move DNA circuit results
- [ ] Move teleportation results
- [ ] Move autonomous discovery results
- [ ] Move quantum circuits (QASM)
- [ ] Verify all quantum files intact

### Phase 3: Move Core Modules
- [ ] Move VAE models
- [ ] Move training scripts
- [ ] Move utilities

### Phase 4: Move Agents
- [ ] Move DNA agent
- [ ] Move Phi agent
- [ ] Move QNN agent

### Phase 5: Move Nodes
- [ ] Move Metatron nodes
- [ ] Update node registration

### Phase 6: Testing & Verification
- [ ] Run import tests
- [ ] Run smoke tests
- [ ] Verify quantum data integrity
- [ ] Update documentation
