"""
AGI Database Interface
Quantum Consciousness AGI Project

This module provides database connectivity and operations for the AGI system,
integrating with the SQL Server database schema for storing and retrieving:
- Sacred geometry datasets
- Consciousness data (EEG/fMRI)
- Quantum VAE models
- NFT metadata
- Training sessions and analysis results
"""

import pyodbc
import json
import numpy as np
import torch
import io
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
from contextlib import asynccontextmanager
import time
from functools import wraps

# Configure logging for performance monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def performance_monitor(func):
    """Decorator to monitor database operation performance"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"Async operation completed in {duration:.4f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Async operation failed after {duration:.4f}s: {e}")
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"Sync operation completed in {duration:.4f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Sync operation failed after {duration:.4f}s: {e}")
            raise

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


class ConnectionPool:
    """Simple connection pool for database connections"""

    def __init__(self, connection_string: str, pool_size: int = 5):
        self.connection_string = connection_string
        self.pool_size = pool_size
        self._pool = []
        self._in_use = set()

    def get_connection(self):
        """Get a connection from the pool"""
        if self._pool:
            conn = self._pool.pop()
            self._in_use.add(conn)
            return conn

        if len(self._in_use) < self.pool_size:
            conn = pyodbc.connect(self.connection_string)
            self._in_use.add(conn)
            return conn

        raise RuntimeError("Connection pool exhausted")

    def return_connection(self, conn):
        """Return a connection to the pool"""
        if conn in self._in_use:
            self._in_use.remove(conn)
            if len(self._pool) < self.pool_size:
                self._pool.append(conn)
            else:
                conn.close()

    def close_all(self):
        """Close all connections in the pool"""
        for conn in self._pool + list(self._in_use):
            try:
                conn.close()
            except:
                pass
        self._pool.clear()
        self._in_use.clear()


class AGIDatabase:
    """Database interface for Quantum Consciousness AGI system"""

    def __init__(self, connection_string: str = None, use_pool: bool = True, pool_size: int = 5):
        """
        Initialize database connection

        Args:
            connection_string: SQLite database file path
            use_pool: Whether to use connection pooling
            pool_size: Size of connection pool
        """
        if connection_string is None:
            # Default to SQLite database file for development
            connection_string = "agi_database.db"

        self.connection_string = connection_string
        self.use_pool = use_pool
        self.pool_size = pool_size
        self._pool = ConnectionPool(connection_string, pool_size) if use_pool else None
        self._connection = None
        self._in_context = False

    def connect(self):
        """Establish database connection"""
        try:
            if self.use_pool and self._pool:
                self._connection = self._pool.get_connection()
            else:
                import sqlite3
                self._connection = sqlite3.connect(self.connection_string)
                self._create_tables()  # Create tables if they don't exist
            logger.info("Connected to AGI database successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def _create_tables(self):
        """Create database tables if they don't exist"""
        with self._connection.cursor() as cursor:
            # Sacred Geometry Datasets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS SacredGeometryDatasets (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    DatasetName TEXT NOT NULL,
                    DataType TEXT NOT NULL,
                    DataVector BLOB,
                    GoldenRatioScore REAL,
                    Metadata TEXT,
                    CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Consciousness Data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ConsciousnessData (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    SubjectId TEXT NOT NULL,
                    DataType TEXT NOT NULL,
                    TimeSeries BLOB,
                    SamplingRate INTEGER,
                    Duration REAL,
                    ConsciousnessMetrics TEXT,
                    CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # NFT Metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS NFTMetadata (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    TokenId TEXT NOT NULL UNIQUE,
                    ContractAddress TEXT NOT NULL,
                    ConsciousnessState BLOB,
                    GoldenRatioResonance REAL,
                    QuantumVerification TEXT,
                    Metadata TEXT,
                    CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Latent Analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS LatentAnalysis (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ModelId INTEGER,
                    InputDataId INTEGER,
                    LatentVector BLOB,
                    ReconstructionError REAL,
                    AnalysisMetrics TEXT,
                    CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self._connection.commit()

    async def connect_async(self):
        """Establish database connection asynchronously"""
        # pyodbc doesn't support true async, but we can use ThreadPoolExecutor
        import concurrent.futures
        import asyncio

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, self.connect)

    def disconnect(self):
        """Close database connection"""
        if self._connection:
            if self.use_pool and self._pool and not self._in_context:
                self._pool.return_connection(self._connection)
            else:
                self._connection.close()
            self._connection = None

    async def disconnect_async(self):
        """Close database connection asynchronously"""
        import concurrent.futures
        import asyncio

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, self.disconnect)

    def __enter__(self):
        self._in_context = True
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._in_context = False
        self.disconnect()

    @asynccontextmanager
    async def async_context(self):
        """Async context manager for database operations"""
        self._in_context = True
        await self.connect_async()
        try:
            yield self
        finally:
            self._in_context = False
            await self.disconnect_async()

    # Sacred Geometry Operations
    @performance_monitor
    def insert_sacred_geometry_data(self, dataset_name: str, data_type: str,
                                  data_vector: np.ndarray, golden_ratio_score: float = None,
                                  metadata: Dict = None) -> int:
        """Insert sacred geometry dataset"""
        with self._connection.cursor() as cursor:
            metadata_json = json.dumps(metadata) if metadata else None
            data_bytes = data_vector.astype(np.float32).tobytes()

            cursor.execute("""
                INSERT INTO SacredGeometryDatasets
                (DatasetName, DataType, DataVector, GoldenRatioScore, Metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (dataset_name, data_type, data_bytes, golden_ratio_score, metadata_json))

            self._connection.commit()
            return cursor.execute("SELECT last_insert_rowid()").fetchone()[0]

    @performance_monitor
    async def insert_sacred_geometry_data_async(self, dataset_name: str, data_type: str,
                                              data_vector: np.ndarray, golden_ratio_score: float = None,
                                              metadata: Dict = None) -> int:
        """Insert sacred geometry dataset asynchronously"""
        import concurrent.futures
        import asyncio

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, self.insert_sacred_geometry_data,
                dataset_name, data_type, data_vector, golden_ratio_score, metadata
            )

    def get_sacred_geometry_data(self, data_type: str = None, limit: int = 100) -> List[Dict]:
        """Retrieve sacred geometry datasets"""
        with self._connection.cursor() as cursor:
            if data_type:
                cursor.execute("""
                    SELECT Id, DatasetName, DataType, DataVector,
                           GoldenRatioScore, CreatedDate, Metadata
                    FROM SacredGeometryDatasets
                    WHERE DataType = ?
                    ORDER BY CreatedDate DESC
                    LIMIT ?
                """, (data_type, limit))
            else:
                cursor.execute("""
                    SELECT Id, DatasetName, DataType, DataVector,
                           GoldenRatioScore, CreatedDate, Metadata
                    FROM SacredGeometryDatasets
                    ORDER BY CreatedDate DESC
                    LIMIT ?
                """, (limit,))

            results = []
            for row in cursor.fetchall():
                data_vector = np.frombuffer(row[3], dtype=np.float32)  # DataVector is at index 3
                results.append({
                    'id': row[0],  # Id
                    'dataset_name': row[1],  # DatasetName
                    'data_type': row[2],  # DataType
                    'data_vector': data_vector,
                    'golden_ratio_score': row[4],  # GoldenRatioScore
                    'created_date': row[5],  # CreatedDate
                    'metadata': json.loads(row[6]) if row[6] else None  # Metadata
                })

            return results

    # Consciousness Data Operations
    def insert_consciousness_data(self, subject_id: str, data_type: str,
                                time_series: np.ndarray, sampling_rate: int,
                                consciousness_metrics: Dict = None) -> int:
        """Insert consciousness data (EEG/fMRI)"""
        with self._connection.cursor() as cursor:
            duration = len(time_series) / sampling_rate
            time_series_bytes = time_series.astype(np.float32).tobytes()
            metrics_json = json.dumps(consciousness_metrics) if consciousness_metrics else None

            cursor.execute("""
                INSERT INTO ConsciousnessData
                (SubjectId, DataType, TimeSeriesData, SamplingRate, DurationSeconds, ConsciousnessMetrics)
                VALUES (?, ?, ?, ?, ?, ?)
            """, subject_id, data_type, time_series_bytes, sampling_rate, duration, metrics_json)

            self._connection.commit()
            return cursor.execute("SELECT @@IDENTITY").fetchone()[0]

    # Model Operations
    @performance_monitor
    def save_quantum_vae_model(self, model_name: str, model_version: str,
                             model: torch.nn.Module, architecture: Dict,
                             training_config: Dict = None, performance_metrics: Dict = None) -> int:
        """Save trained Quantum VAE model"""
        with self._connection.cursor() as cursor:
            # Serialize model
            model_buffer = io.BytesIO()
            torch.save(model.state_dict(), model_buffer)
            model_bytes = model_buffer.getvalue()

            arch_json = json.dumps(architecture)
            config_json = json.dumps(training_config) if training_config else None
            metrics_json = json.dumps(performance_metrics) if performance_metrics else None

            cursor.execute("""
                INSERT INTO QuantumVAEModels
                (ModelName, ModelVersion, ModelData, Architecture, TrainingConfig, PerformanceMetrics)
                VALUES (?, ?, ?, ?, ?, ?)
            """, model_name, model_version, model_bytes, arch_json, config_json, metrics_json)

            self._connection.commit()
            return cursor.execute("SELECT @@IDENTITY").fetchone()[0]

    @performance_monitor
    async def save_quantum_vae_model_async(self, model_name: str, model_version: str,
                                         model: torch.nn.Module, architecture: Dict,
                                         training_config: Dict = None, performance_metrics: Dict = None) -> int:
        """Save trained Quantum VAE model asynchronously"""
        import concurrent.futures
        import asyncio

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, self.save_quantum_vae_model,
                model_name, model_version, model, architecture, training_config, performance_metrics
            )

    def load_quantum_vae_model(self, model_id: int) -> Tuple[torch.nn.Module, Dict]:
        """Load trained Quantum VAE model"""
        with self._connection.cursor() as cursor:
            cursor.execute("""
                SELECT ModelData, Architecture FROM QuantumVAEModels WHERE Id = ?
            """, model_id)

            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Model with ID {model_id} not found")

            # Deserialize model state
            model_buffer = io.BytesIO(row.ModelData)
            model_state = torch.load(model_buffer)

            architecture = json.loads(row.Architecture)
            return model_state, architecture

    # NFT Operations
    @performance_monitor
    def insert_nft_metadata(self, token_id: str, contract_address: str,
                          consciousness_state: np.ndarray, golden_ratio_resonance: float,
                          quantum_verification: Dict, metadata: Dict, image_hash: str = None) -> int:
        """Insert NFT metadata with quantum verification"""
        with self._connection.cursor() as cursor:
            state_bytes = consciousness_state.astype(np.float32).tobytes()
            verification_json = json.dumps(quantum_verification)
            metadata_json = json.dumps(metadata)

            cursor.execute("""
                INSERT INTO NFTMetadata
                (TokenId, ContractAddress, ConsciousnessState, GoldenRatioResonance,
                 QuantumVerification, Metadata, ImageHash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, token_id, contract_address, state_bytes, golden_ratio_resonance,
                verification_json, metadata_json, image_hash)

            self._connection.commit()
            return cursor.execute("SELECT @@IDENTITY").fetchone()[0]

    @performance_monitor
    async def insert_nft_metadata_async(self, token_id: str, contract_address: str,
                                      consciousness_state: np.ndarray, golden_ratio_resonance: float,
                                      quantum_verification: Dict, metadata: Dict, image_hash: str = None) -> int:
        """Insert NFT metadata asynchronously"""
        import concurrent.futures
        import asyncio

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, self.insert_nft_metadata,
                token_id, contract_address, consciousness_state, golden_ratio_resonance,
                quantum_verification, metadata, image_hash
            )

    # High-dimensional Vector Search Operations
    @performance_monitor
    def find_similar_sacred_geometry(self, query_vector: np.ndarray, top_k: int = 10,
                                   data_type: str = None) -> List[Tuple[int, float, Dict]]:
        """
        Find similar sacred geometry vectors using cosine similarity
        Returns: List of (id, similarity_score, metadata)
        """
        with self._connection.cursor() as cursor:
            # Get all vectors of the specified type
            if data_type:
                cursor.execute("""
                    SELECT Id, DataVector, Metadata, GoldenRatioScore
                    FROM SacredGeometryDatasets
                    WHERE DataType = ?
                """, data_type)
            else:
                cursor.execute("""
                    SELECT Id, DataVector, Metadata, GoldenRatioScore
                    FROM SacredGeometryDatasets
                """)

            results = []
            query_norm = np.linalg.norm(query_vector)

            for row in cursor.fetchall():
                vector_bytes = row.DataVector
                vector = np.frombuffer(vector_bytes, dtype=np.float32)
                vector_norm = np.linalg.norm(vector)

                # Cosine similarity
                if vector_norm > 0 and query_norm > 0:
                    similarity = np.dot(query_vector, vector) / (query_norm * vector_norm)
                else:
                    similarity = 0.0

                metadata = json.loads(row.Metadata) if row.Metadata else {}
                metadata['golden_ratio_score'] = row.GoldenRatioScore

                results.append((row.Id, float(similarity), metadata))

            # Sort by similarity and return top_k
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]

    # Training Session Operations
    def start_training_session(self, model_id: int, session_name: str,
                             training_config: Dict) -> int:
        """Start a new training session"""
        with self._connection.cursor() as cursor:
            config_json = json.dumps(training_config)
            start_time = datetime.utcnow()

            cursor.execute("""
                INSERT INTO TrainingSessions
                (ModelId, SessionName, StartTime, TrainingConfig, Status)
                VALUES (?, ?, ?, ?, 'running')
            """, model_id, session_name, start_time, config_json)

            self._connection.commit()
            return cursor.execute("SELECT @@IDENTITY").fetchone()[0]

    def update_training_session(self, session_id: int, epochs: int,
                              final_loss: float = None, best_loss: float = None,
                              metrics: Dict = None, status: str = None):
        """Update training session progress"""
        with self._connection.cursor() as cursor:
            end_time = datetime.utcnow() if status in ['completed', 'failed'] else None
            metrics_json = json.dumps(metrics) if metrics else None

            cursor.execute("""
                UPDATE TrainingSessions
                SET EndTime = ?, Epochs = ?, FinalLoss = ?, BestLoss = ?,
                    Metrics = ?, Status = ?
                WHERE Id = ?
            """, end_time, epochs, final_loss, best_loss, metrics_json, status, session_id)

            self._connection.commit()

    # Analysis Operations
    def insert_latent_analysis(self, model_id: int, input_data_id: int,
                             input_data_type: str, latent_vector: np.ndarray,
                             quantum_fingerprint: Dict = None, golden_ratio_patterns: Dict = None,
                             tsne_coordinates: Dict = None) -> int:
        """Insert latent space analysis results"""
        with self._connection.cursor() as cursor:
            latent_bytes = latent_vector.astype(np.float32).tobytes()
            fingerprint_json = json.dumps(quantum_fingerprint) if quantum_fingerprint else None
            patterns_json = json.dumps(golden_ratio_patterns) if golden_ratio_patterns else None
            tsne_json = json.dumps(tsne_coordinates) if tsne_coordinates else None

            cursor.execute("""
                INSERT INTO LatentSpaceAnalysis
                (ModelId, InputDataId, InputDataType, LatentVector, QuantumFingerprint,
                 GoldenRatioPatterns, TSNE_Coordinates)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, model_id, input_data_id, input_data_type, latent_bytes,
                fingerprint_json, patterns_json, tsne_json)

            self._connection.commit()
            return cursor.execute("SELECT @@IDENTITY").fetchone()[0]


# Example usage functions
def create_unified_dataset(db: AGIDatabase) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create unified dataset from sacred geometry and consciousness data
    Following project patterns: normalization, dimension matching
    """
    # Get sacred geometry data
    sacred_data = db.get_sacred_geometry_data(limit=1000)
    sacred_vectors = np.array([item['data_vector'] for item in sacred_data])

    # Get consciousness data (processed vectors)
    with db._connection.cursor() as cursor:
        cursor.execute("""
            SELECT ProcessedVector FROM ConsciousnessData
            WHERE ProcessedVector IS NOT NULL
        """)
        consciousness_vectors = []
        for row in cursor.fetchall():
            if row.ProcessedVector:
                vector = np.frombuffer(row.ProcessedVector, dtype=np.float32)
                consciousness_vectors.append(vector)

        if consciousness_vectors:
            consciousness_vectors = np.array(consciousness_vectors)
        else:
            consciousness_vectors = np.empty((0, 128))

    # Combine datasets
    if len(consciousness_vectors) > 0:
        all_data = np.concatenate([sacred_vectors, consciousness_vectors], axis=0)
    else:
        all_data = sacred_vectors

    # Apply normalization: (data - mean) / (std + 1e-10)
    mean = np.mean(all_data, axis=0)
    std = np.std(all_data, axis=0)
    normalized_data = (all_data - mean) / (std + 1e-10)

    # Create labels (0 for sacred geometry, 1 for consciousness)
    labels = np.concatenate([
        np.zeros(len(sacred_vectors)),
        np.ones(len(consciousness_vectors)) if len(consciousness_vectors) > 0 else np.array([])
    ]).astype(int)

    return normalized_data, labels


if __name__ == "__main__":
    # Example usage
    with AGIDatabase() as db:
        # Insert sample sacred geometry data
        sample_vector = np.random.randn(128).astype(np.float32)
        data_id = db.insert_sacred_geometry_data(
            "Fibonacci_Sequence_1", "molecular_kinetics", sample_vector,
            golden_ratio_score=0.95, metadata={"source": "mathematical"}
        )
        print(f"Inserted sacred geometry data with ID: {data_id}")

        # Insert sample consciousness data
        eeg_data = np.random.randn(1000).astype(np.float32)  # 1 second at 1000 Hz
        consciousness_id = db.insert_consciousness_data(
            "subject_001", "EEG", eeg_data, 1000,
            consciousness_metrics={"LZ_complexity": 0.85, "PCI": 0.72}
        )
        print(f"Inserted consciousness data with ID: {consciousness_id}")

        # Create unified dataset
        data, labels = create_unified_dataset(db)
        print(f"Unified dataset shape: {data.shape}, labels shape: {labels.shape}")