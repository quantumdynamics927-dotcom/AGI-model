import os
import sys
import tempfile
import unittest
import importlib
from pathlib import Path

import yaml


sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
)

QuantumConsciousnessConfig = importlib.import_module(
    'agi_app.config.config_manager'
).QuantumConsciousnessConfig


class TestQuantumConsciousnessConfig(unittest.TestCase):
    def setUp(self):
        self.original_env = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_default_provenance_is_recorded_for_leaf_fields(self):
        config = QuantumConsciousnessConfig()
        provenance = config.get_provenance()

        self.assertEqual(provenance['model']['input_dim'], 'default')
        self.assertEqual(provenance['training']['learning_rate'], 'default')
        self.assertEqual(provenance['quantum']['backend'], 'default')
        self.assertEqual(provenance['archive']['enable_provenance'], 'default')

    def test_yaml_and_env_sources_are_tracked(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'config.yaml'
            config_path.write_text(
                yaml.safe_dump(
                    {
                        'model': {'input_dim': 256},
                        'quantum': {'backend': 'ibm_brisbane'},
                        'logging': {'level': 'DEBUG'},
                    },
                    sort_keys=False,
                ),
                encoding='utf-8',
            )

            os.environ['QUANTUM_AGI_MODEL_LATENT_DIM'] = '16'
            os.environ['QUANTUM_AGI_TRAINING_WEIGHT_DECAY'] = '1e-4'
            os.environ['QUANTUM_AGI_QUANTUM_SHOTS'] = '4096'

            config = QuantumConsciousnessConfig.from_yaml(config_path)
            config.apply_env_overrides()
            provenance = config.get_provenance()

            self.assertEqual(config.model.input_dim, 256)
            self.assertEqual(config.model.latent_dim, 16)
            self.assertEqual(config.training.weight_decay, 1e-4)
            self.assertEqual(config.quantum.shots, 4096)
            self.assertEqual(provenance['model']['input_dim'], 'yaml')
            self.assertEqual(provenance['model']['latent_dim'], 'env')
            self.assertEqual(provenance['training']['weight_decay'], 'env')
            self.assertEqual(provenance['quantum']['backend'], 'yaml')
            self.assertEqual(provenance['log_level'], 'yaml')

    def test_validation_rejects_invalid_ranges_and_backend_names(self):
        config = QuantumConsciousnessConfig()
        config.model.sparsity_factor = 1.2
        config.training.epochs = 0
        config.quantum.backend = 'invalid backend name'
        config.quantum.shots = 0
        config.api.port = 70000

        self.assertFalse(config.validate())

    def test_save_yaml_can_include_provenance(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / 'saved_config.yaml'
            config = QuantumConsciousnessConfig()
            config.save_yaml(output_path, include_provenance=True)

            saved = yaml.safe_load(output_path.read_text(encoding='utf-8'))
            self.assertIn('_provenance', saved)
            self.assertEqual(
                saved['_provenance']['model']['input_dim'],
                'default',
            )


if __name__ == '__main__':
    unittest.main()
