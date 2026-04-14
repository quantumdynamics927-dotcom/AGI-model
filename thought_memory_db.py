"""
Thought Memory Database Layer
==============================

Persistent storage for AGI model reflections, thoughts, and benchmark runs.
Supports local-first workflow with cloud comparison mode.

Design:
- Every generation auto-saves to database
- Stores prompt, output, model, backend, scores, and review labels
- Enables retrieval of similar past thoughts for context
- Supports curated promotion to training/benchmark sets

Schema:
- thought_memory: Main table for all generated thoughts
- thought_tags: Tags for categorization
- thought_scores: QAGI metrics for each thought
- thought_comparisons: Cloud vs local comparison records
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import hashlib


@dataclass
class ThoughtRecord:
    """A single thought/reflection record."""
    id: Optional[int] = None
    prompt: str = ""
    generated_thought: str = ""
    model: str = ""
    backend: str = ""
    provider: str = ""
    
    # Timestamps
    created_at: str = ""
    reviewed_at: str = ""
    
    # Model-conditioned signals (secondary diagnostics)
    raw_phi_coherence: float = 0.0
    raw_biomimetic_resonance: float = 0.0
    z_phi_coherence: float = 0.0
    z_biomimetic_resonance: float = 0.0
    phi_resonance: float = 1.6180
    information_density: float = 0.0
    
    # QAGI scores
    structural_score: float = 0.0
    cognition_quality: float = 0.0
    total_qagi_score: float = 0.0
    
    # Field scores
    mechanism_score: float = 0.0
    measurable_outcome_score: float = 0.0
    boundary_condition_score: float = 0.0
    failure_condition_score: float = 0.0
    
    # Extracted text spans
    mechanism_text: str = ""
    measurable_outcome_text: str = ""
    boundary_condition_text: str = ""
    failure_condition_text: str = ""
    
    # Review labels
    review_status: str = "pending"  # pending, keep, reject, improve
    review_labels: str = ""  # JSON list: ["creative", "technical", "benchmark-grade"]
    review_notes: str = ""
    
    # Run context
    run_mode: str = "standard"  # standard, comparison, teacher
    provider_purity: float = 1.0
    fallback_used: bool = False
    baseline_version: str = ""
    
    # Hash for deduplication
    content_hash: str = ""
    
    def compute_hash(self) -> str:
        """Compute hash of prompt + generated_thought for deduplication."""
        content = f"{self.prompt}|{self.generated_thought}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'prompt': self.prompt,
            'generated_thought': self.generated_thought,
            'model': self.model,
            'backend': self.backend,
            'provider': self.provider,
            'created_at': self.created_at,
            'reviewed_at': self.reviewed_at,
            'raw_phi_coherence': self.raw_phi_coherence,
            'raw_biomimetic_resonance': self.raw_biomimetic_resonance,
            'z_phi_coherence': self.z_phi_coherence,
            'z_biomimetic_resonance': self.z_biomimetic_resonance,
            'phi_resonance': self.phi_resonance,
            'information_density': self.information_density,
            'structural_score': self.structural_score,
            'cognition_quality': self.cognition_quality,
            'total_qagi_score': self.total_qagi_score,
            'mechanism_score': self.mechanism_score,
            'measurable_outcome_score': self.measurable_outcome_score,
            'boundary_condition_score': self.boundary_condition_score,
            'failure_condition_score': self.failure_condition_score,
            'mechanism_text': self.mechanism_text,
            'measurable_outcome_text': self.measurable_outcome_text,
            'boundary_condition_text': self.boundary_condition_text,
            'failure_condition_text': self.failure_condition_text,
            'review_status': self.review_status,
            'review_labels': self.review_labels,
            'review_notes': self.review_notes,
            'run_mode': self.run_mode,
            'provider_purity': self.provider_purity,
            'fallback_used': self.fallback_used,
            'baseline_version': self.baseline_version,
            'content_hash': self.content_hash,
        }


class ThoughtMemoryDB:
    """
    Database for storing and retrieving thought/reflection records.
    
    Usage:
        db = ThoughtMemoryDB()
        
        # Save a thought
        record = ThoughtRecord(
            prompt="Generate a thought about...",
            generated_thought="...",
            model="qwen3:1.7b",
            backend="ollama_local"
        )
        db.save_thought(record)
        
        # Search similar thoughts
        similar = db.search_by_topic("distributed memory")
        
        # Get best thoughts for training
        best = db.get_training_set(min_structural_score=7.0)
    """
    
    def __init__(self, db_path: str = "thought_memory.db"):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main thought memory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS thought_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                generated_thought TEXT NOT NULL,
                model TEXT NOT NULL,
                backend TEXT NOT NULL,
                provider TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                reviewed_at TEXT DEFAULT '',
                
                -- Model-conditioned signals
                raw_phi_coherence REAL DEFAULT 0.0,
                raw_biomimetic_resonance REAL DEFAULT 0.0,
                z_phi_coherence REAL DEFAULT 0.0,
                z_biomimetic_resonance REAL DEFAULT 0.0,
                phi_resonance REAL DEFAULT 1.6180,
                information_density REAL DEFAULT 0.0,
                
                -- QAGI scores
                structural_score REAL DEFAULT 0.0,
                cognition_quality REAL DEFAULT 0.0,
                total_qagi_score REAL DEFAULT 0.0,
                
                -- Field scores
                mechanism_score REAL DEFAULT 0.0,
                measurable_outcome_score REAL DEFAULT 0.0,
                boundary_condition_score REAL DEFAULT 0.0,
                failure_condition_score REAL DEFAULT 0.0,
                
                -- Extracted text spans
                mechanism_text TEXT DEFAULT '',
                measurable_outcome_text TEXT DEFAULT '',
                boundary_condition_text TEXT DEFAULT '',
                failure_condition_text TEXT DEFAULT '',
                
                -- Review
                review_status TEXT DEFAULT 'pending',
                review_labels TEXT DEFAULT '[]',
                review_notes TEXT DEFAULT '',
                
                -- Run context
                run_mode TEXT DEFAULT 'standard',
                provider_purity REAL DEFAULT 1.0,
                fallback_used INTEGER DEFAULT 0,
                baseline_version TEXT DEFAULT '',
                
                -- Hash for deduplication
                content_hash TEXT NOT NULL,
                
                -- Indexes
                UNIQUE(content_hash)
            )
        ''')
        
        # Tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS thought_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thought_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (thought_id) REFERENCES thought_memory(id),
                UNIQUE(thought_id, tag)
            )
        ''')
        
        # Comparisons table (cloud vs local)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS thought_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                local_thought_id INTEGER NOT NULL,
                cloud_thought_id INTEGER NOT NULL,
                comparison_type TEXT DEFAULT 'same_prompt',
                created_at TEXT NOT NULL,
                notes TEXT DEFAULT '',
                FOREIGN KEY (local_thought_id) REFERENCES thought_memory(id),
                FOREIGN KEY (cloud_thought_id) REFERENCES thought_memory(id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_model ON thought_memory(model)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_backend ON thought_memory(backend)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_structural_score ON thought_memory(structural_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_review_status ON thought_memory(review_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON thought_memory(created_at)')
        
        conn.commit()
        conn.close()
    
    def save_thought(self, record: ThoughtRecord) -> int:
        """
        Save a thought record to the database.
        
        Returns:
            The ID of the saved record
        """
        if not record.content_hash:
            record.content_hash = record.compute_hash()
        if not record.created_at:
            record.created_at = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO thought_memory (
                    prompt, generated_thought, model, backend, provider, created_at,
                    raw_phi_coherence, raw_biomimetic_resonance,
                    z_phi_coherence, z_biomimetic_resonance,
                    phi_resonance, information_density,
                    structural_score, cognition_quality, total_qagi_score,
                    mechanism_score, measurable_outcome_score,
                    boundary_condition_score, failure_condition_score,
                    mechanism_text, measurable_outcome_text,
                    boundary_condition_text, failure_condition_text,
                    review_status, review_labels, review_notes,
                    run_mode, provider_purity, fallback_used, baseline_version,
                    content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.prompt, record.generated_thought, record.model, record.backend,
                record.provider, record.created_at,
                record.raw_phi_coherence, record.raw_biomimetic_resonance,
                record.z_phi_coherence, record.z_biomimetic_resonance,
                record.phi_resonance, record.information_density,
                record.structural_score, record.cognition_quality, record.total_qagi_score,
                record.mechanism_score, record.measurable_outcome_score,
                record.boundary_condition_score, record.failure_condition_score,
                record.mechanism_text, record.measurable_outcome_text,
                record.boundary_condition_text, record.failure_condition_text,
                record.review_status, record.review_labels, record.review_notes,
                record.run_mode, record.provider_purity, int(record.fallback_used),
                record.baseline_version, record.content_hash
            ))
            
            thought_id = cursor.lastrowid
            conn.commit()
            return thought_id
            
        except sqlite3.IntegrityError:
            # Duplicate content_hash, return existing ID
            cursor.execute(
                'SELECT id FROM thought_memory WHERE content_hash = ?',
                (record.content_hash,)
            )
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else -1
        
        finally:
            conn.close()
    
    def get_thought(self, thought_id: int) -> Optional[ThoughtRecord]:
        """Get a thought by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM thought_memory WHERE id = ?', (thought_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_record(row)
        return None
    
    def search_by_topic(self, topic: str, limit: int = 10) -> List[ThoughtRecord]:
        """Search thoughts by topic/keyword in prompt or generated text."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM thought_memory 
            WHERE prompt LIKE ? OR generated_thought LIKE ?
            ORDER BY structural_score DESC, created_at DESC
            LIMIT ?
        ''', (f'%{topic}%', f'%{topic}%', limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_record(row) for row in rows]
    
    def search_by_model(self, model: str, limit: int = 100) -> List[ThoughtRecord]:
        """Get all thoughts from a specific model."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM thought_memory 
            WHERE model = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (model, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_record(row) for row in rows]
    
    def get_best_thoughts(self, min_structural_score: float = 7.0, limit: int = 50) -> List[ThoughtRecord]:
        """Get thoughts with high structural scores for training set."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM thought_memory 
            WHERE structural_score >= ? AND review_status IN ('keep', 'benchmark-grade')
            ORDER BY structural_score DESC, cognition_quality DESC
            LIMIT ?
        ''', (min_structural_score, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_record(row) for row in rows]
    
    def get_training_set(self, min_structural_score: float = 7.0) -> List[Dict]:
        """Get curated training set as list of dicts."""
        thoughts = self.get_best_thoughts(min_structural_score)
        return [t.to_dict() for t in thoughts]
    
    def get_pending_reviews(self, limit: int = 50) -> List[ThoughtRecord]:
        """Get thoughts pending review."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM thought_memory 
            WHERE review_status = 'pending'
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_record(row) for row in rows]
    
    def update_review(self, thought_id: int, status: str, labels: List[str], notes: str = "") -> bool:
        """Update review status and labels for a thought."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE thought_memory 
            SET review_status = ?, review_labels = ?, review_notes = ?, reviewed_at = ?
            WHERE id = ?
        ''', (status, json.dumps(labels), notes, datetime.now().isoformat(), thought_id))
        
        conn.commit()
        conn.close()
        return True
    
    def add_tag(self, thought_id: int, tag: str) -> bool:
        """Add a tag to a thought."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO thought_tags (thought_id, tag, created_at)
                VALUES (?, ?, ?)
            ''', (thought_id, tag, datetime.now().isoformat()))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_thoughts_by_tag(self, tag: str, limit: int = 50) -> List[ThoughtRecord]:
        """Get all thoughts with a specific tag."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.* FROM thought_memory t
            JOIN thought_tags tg ON t.id = tg.thought_id
            WHERE tg.tag = ?
            ORDER BY t.structural_score DESC
            LIMIT ?
        ''', (tag, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_record(row) for row in rows]
    
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total thoughts
        cursor.execute('SELECT COUNT(*) FROM thought_memory')
        total = cursor.fetchone()[0]
        
        # By model
        cursor.execute('SELECT model, COUNT(*) FROM thought_memory GROUP BY model')
        by_model = dict(cursor.fetchall())
        
        # By review status
        cursor.execute('SELECT review_status, COUNT(*) FROM thought_memory GROUP BY review_status')
        by_status = dict(cursor.fetchall())
        
        # Average scores
        cursor.execute('SELECT AVG(structural_score), AVG(cognition_quality) FROM thought_memory')
        avg_structural, avg_cognition = cursor.fetchone()
        
        # By run mode
        cursor.execute('SELECT run_mode, COUNT(*) FROM thought_memory GROUP BY run_mode')
        by_mode = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_thoughts': total,
            'by_model': by_model,
            'by_review_status': by_status,
            'by_run_mode': by_mode,
            'avg_structural_score': avg_structural or 0.0,
            'avg_cognition_quality': avg_cognition or 0.0,
        }
    
    def compare_runs(self, local_thought_id: int, cloud_thought_id: int, notes: str = "") -> int:
        """Record a comparison between local and cloud runs."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO thought_comparisons (local_thought_id, cloud_thought_id, created_at, notes)
            VALUES (?, ?, ?, ?)
        ''', (local_thought_id, cloud_thought_id, datetime.now().isoformat(), notes))
        
        comparison_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return comparison_id
    
    def export_training_set(self, output_path: str, min_structural_score: float = 7.0) -> int:
        """Export training set to JSON file."""
        thoughts = self.get_best_thoughts(min_structural_score)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in thoughts], f, indent=2, default=str)
        
        return len(thoughts)
    
    def _row_to_record(self, row: tuple) -> ThoughtRecord:
        """Convert database row to ThoughtRecord."""
        return ThoughtRecord(
            id=row[0],
            prompt=row[1],
            generated_thought=row[2],
            model=row[3],
            backend=row[4],
            provider=row[5],
            created_at=row[6],
            reviewed_at=row[7],
            raw_phi_coherence=row[8],
            raw_biomimetic_resonance=row[9],
            z_phi_coherence=row[10],
            z_biomimetic_resonance=row[11],
            phi_resonance=row[12],
            information_density=row[13],
            structural_score=row[14],
            cognition_quality=row[15],
            total_qagi_score=row[16],
            mechanism_score=row[17],
            measurable_outcome_score=row[18],
            boundary_condition_score=row[19],
            failure_condition_score=row[20],
            mechanism_text=row[21],
            measurable_outcome_text=row[22],
            boundary_condition_text=row[23],
            failure_condition_text=row[24],
            review_status=row[25],
            review_labels=row[26],
            review_notes=row[27],
            run_mode=row[28],
            provider_purity=row[29],
            fallback_used=bool(row[30]),
            baseline_version=row[31],
            content_hash=row[32],
        )


# Convenience function for Space integration
def create_thought_from_generation(
    prompt: str,
    generated_thought: str,
    model: str,
    backend: str,
    qagi_score: Optional[Dict] = None,
    raw_metrics: Optional[Dict] = None,
) -> ThoughtRecord:
    """
    Create a ThoughtRecord from a generation.
    
    Args:
        prompt: The input prompt
        generated_thought: The generated text
        model: Model identifier (e.g., "qwen3:1.7b")
        backend: Backend identifier (e.g., "ollama_local")
        qagi_score: Optional QAGI score dict
        raw_metrics: Optional raw metrics dict with phi/biomimetic values
    
    Returns:
        ThoughtRecord ready to save
    """
    record = ThoughtRecord(
        prompt=prompt,
        generated_thought=generated_thought,
        model=model,
        backend=backend,
    )
    
    if qagi_score:
        record.structural_score = qagi_score.get('structural_score', 0.0)
        record.cognition_quality = qagi_score.get('cognition_quality', 0.0)
        record.total_qagi_score = qagi_score.get('total_qagi_score', 0.0)
        
        # Field scores
        cognition = qagi_score.get('cognition', {})
        record.mechanism_score = cognition.get('mechanism_score', 0.0)
        record.measurable_outcome_score = cognition.get('measurable_outcome_score', 0.0)
        record.boundary_condition_score = cognition.get('boundary_condition_score', 0.0)
        record.failure_condition_score = cognition.get('failure_condition_score', 0.0)
        
        # Extracted text
        record.mechanism_text = cognition.get('mechanism_text', '')
        record.measurable_outcome_text = cognition.get('measurable_outcome_text', '')
        record.boundary_condition_text = cognition.get('boundary_condition_text', '')
        record.failure_condition_text = cognition.get('failure_condition_text', '')
    
    if raw_metrics:
        record.raw_phi_coherence = raw_metrics.get('phi_coherence', 0.0)
        record.raw_biomimetic_resonance = raw_metrics.get('biomimetic_resonance', 0.0)
        record.z_phi_coherence = raw_metrics.get('z_phi_coherence', 0.0)
        record.z_biomimetic_resonance = raw_metrics.get('z_biomimetic_resonance', 0.0)
        record.information_density = raw_metrics.get('information_density', 0.0)
    
    return record


if __name__ == "__main__":
    # Test the database
    db = ThoughtMemoryDB("test_thought_memory.db")
    
    # Create a test record
    record = ThoughtRecord(
        prompt="Generate a thought about distributed memory resilience.",
        generated_thought="The distributed memory system uses hierarchical encoding...",
        model="qwen3:1.7b",
        backend="ollama_local",
        structural_score=8.5,
        cognition_quality=0.65,
    )
    
    # Save it
    thought_id = db.save_thought(record)
    print(f"Saved thought with ID: {thought_id}")
    
    # Retrieve it
    retrieved = db.get_thought(thought_id)
    print(f"Retrieved: {retrieved.prompt[:50]}...")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"Statistics: {stats}")
    
    print("\nThought Memory Database ready for Space integration.")