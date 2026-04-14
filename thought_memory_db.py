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
    
    # Evolution chain
    parent_thought_id: Optional[int] = None  # ID of thought this builds on
    generation_depth: int = 0  # 0 = original, 1 = builds on 1, etc.
    
    # Retrieval tracking
    retrieval_count: int = 0  # How many times this thought was retrieved
    last_retrieved_at: str = ""  # When last retrieved for context
    
    # Experiment grouping
    prompt_family: str = ""  # e.g., "distributed_memory_2x2"
    experiment_id: str = ""  # e.g., "exp_20260414_001"
    
    # Curation state (separate from review)
    curation_state: str = "raw"  # raw, reviewed, training_set, validation_set, archived
    
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
            'parent_thought_id': self.parent_thought_id,
            'generation_depth': self.generation_depth,
            'retrieval_count': self.retrieval_count,
            'last_retrieved_at': self.last_retrieved_at,
            'prompt_family': self.prompt_family,
            'experiment_id': self.experiment_id,
            'curation_state': self.curation_state,
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
                
                -- Evolution chain
                parent_thought_id INTEGER DEFAULT NULL,
                generation_depth INTEGER DEFAULT 0,
                
                -- Retrieval tracking
                retrieval_count INTEGER DEFAULT 0,
                last_retrieved_at TEXT DEFAULT '',
                
                -- Experiment grouping
                prompt_family TEXT DEFAULT '',
                experiment_id TEXT DEFAULT '',
                
                -- Curation state
                curation_state TEXT DEFAULT 'raw',
                
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
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_curation_state ON thought_memory(curation_state)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_prompt_family ON thought_memory(prompt_family)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_experiment_id ON thought_memory(experiment_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_parent_thought_id ON thought_memory(parent_thought_id)')
        
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
        
        # Calculate generation depth from parent
        if record.parent_thought_id and record.generation_depth == 0:
            parent = self.get_thought(record.parent_thought_id)
            if parent:
                record.generation_depth = parent.generation_depth + 1
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO thought_memory (
                    prompt, generated_thought, model, backend, provider, created_at,
                    parent_thought_id, generation_depth,
                    retrieval_count, last_retrieved_at,
                    prompt_family, experiment_id, curation_state,
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
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.prompt, record.generated_thought, record.model, record.backend,
                record.provider, record.created_at,
                record.parent_thought_id, record.generation_depth,
                record.retrieval_count, record.last_retrieved_at,
                record.prompt_family, record.experiment_id, record.curation_state,
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
        
        # By curation state
        cursor.execute('SELECT curation_state, COUNT(*) FROM thought_memory GROUP BY curation_state')
        by_curation = dict(cursor.fetchall())
        
        # Average scores
        cursor.execute('SELECT AVG(structural_score), AVG(cognition_quality) FROM thought_memory')
        avg_structural, avg_cognition = cursor.fetchone()
        
        # By run mode
        cursor.execute('SELECT run_mode, COUNT(*) FROM thought_memory GROUP BY run_mode')
        by_mode = dict(cursor.fetchall())
        
        # Evolution chain depth
        cursor.execute('SELECT MAX(generation_depth), AVG(generation_depth) FROM thought_memory')
        max_depth, avg_depth = cursor.fetchone()
        
        # Total retrievals
        cursor.execute('SELECT SUM(retrieval_count) FROM thought_memory')
        total_retrievals = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_thoughts': total,
            'by_model': by_model,
            'by_review_status': by_status,
            'by_curation_state': by_curation,
            'by_run_mode': by_mode,
            'avg_structural_score': avg_structural or 0.0,
            'avg_cognition_quality': avg_cognition or 0.0,
            'max_generation_depth': max_depth or 0,
            'avg_generation_depth': avg_depth or 0.0,
            'total_retrievals': total_retrievals,
        }
    
    # =========================================================================
    # RETRIEVAL METHODS
    # =========================================================================
    
    def retrieve_for_context(
        self,
        prompt: str,
        model: str = "",
        min_structural_score: float = 5.0,
        limit: int = 3,
        exclude_cloud: bool = True
    ) -> List[ThoughtRecord]:
        """
        Retrieve relevant thoughts for context before generation.
        
        Only retrieves reviewed/high-quality thoughts to avoid amplifying bad patterns.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query
        query = '''
            SELECT * FROM thought_memory 
            WHERE (prompt LIKE ? OR generated_thought LIKE ?)
            AND structural_score >= ?
            AND curation_state IN ('reviewed', 'training_set', 'validation_set')
        '''
        params = [f'%{prompt}%', f'%{prompt}%', min_structural_score]
        
        if model:
            query += ' AND model = ?'
            params.append(model)
        
        if exclude_cloud:
            query += " AND run_mode != 'comparison'"
        
        query += ' ORDER BY structural_score DESC, retrieval_count ASC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Update retrieval count for each retrieved thought
        now = datetime.now().isoformat()
        for row in rows:
            thought_id = row[0]
            cursor.execute('''
                UPDATE thought_memory 
                SET retrieval_count = retrieval_count + 1, last_retrieved_at = ?
                WHERE id = ?
            ''', (now, thought_id))
        
        conn.commit()
        conn.close()
        
        return [self._row_to_record(row) for row in rows]
    
    def get_evolution_chain(self, thought_id: int) -> List[ThoughtRecord]:
        """Get the full evolution chain for a thought (from root to this thought)."""
        chain = []
        current = self.get_thought(thought_id)
        
        while current:
            chain.append(current)
            if current.parent_thought_id:
                current = self.get_thought(current.parent_thought_id)
            else:
                break
        
        # Reverse to get root first
        return list(reversed(chain))
    
    def get_children(self, thought_id: int) -> List[ThoughtRecord]:
        """Get all thoughts that build on this thought."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM thought_memory 
            WHERE parent_thought_id = ?
            ORDER BY created_at ASC
        ''', (thought_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_record(row) for row in rows]
    
    # =========================================================================
    # CURATION METHODS
    # =========================================================================
    
    def update_curation_state(self, thought_id: int, state: str) -> bool:
        """Update curation state (raw, reviewed, training_set, validation_set, archived)."""
        valid_states = ['raw', 'reviewed', 'training_set', 'validation_set', 'archived']
        if state not in valid_states:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE thought_memory SET curation_state = ? WHERE id = ?
        ''', (state, thought_id))
        
        conn.commit()
        conn.close()
        return True
    
    def promote_to_training_set(self, thought_id: int) -> bool:
        """Promote a thought to the training set."""
        return self.update_curation_state(thought_id, 'training_set')
    
    def promote_to_validation_set(self, thought_id: int) -> bool:
        """Promote a thought to the validation set."""
        return self.update_curation_state(thought_id, 'validation_set')
    
    def get_by_curation_state(self, state: str, limit: int = 100) -> List[ThoughtRecord]:
        """Get thoughts by curation state."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM thought_memory 
            WHERE curation_state = ?
            ORDER BY structural_score DESC
            LIMIT ?
        ''', (state, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_record(row) for row in rows]
    
    def get_by_experiment(self, experiment_id: str) -> List[ThoughtRecord]:
        """Get all thoughts from a specific experiment."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM thought_memory 
            WHERE experiment_id = ?
            ORDER BY created_at ASC
        ''', (experiment_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_record(row) for row in rows]
    
    def get_by_prompt_family(self, prompt_family: str, limit: int = 100) -> List[ThoughtRecord]:
        """Get all thoughts from a specific prompt family."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM thought_memory 
            WHERE prompt_family = ?
            ORDER BY structural_score DESC
            LIMIT ?
        ''', (prompt_family, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_record(row) for row in rows]
    
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
        thoughts = self.get_by_curation_state('training_set')
        # Filter by structural score
        thoughts = [t for t in thoughts if t.structural_score >= min_structural_score]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in thoughts], f, indent=2, default=str)
        
        return len(thoughts)
    
    def export_validation_set(self, output_path: str) -> int:
        """Export validation set to JSON file."""
        thoughts = self.get_by_curation_state('validation_set')
        
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
            parent_thought_id=row[8],
            generation_depth=row[9],
            retrieval_count=row[10],
            last_retrieved_at=row[11],
            prompt_family=row[12],
            experiment_id=row[13],
            curation_state=row[14],
            raw_phi_coherence=row[15],
            raw_biomimetic_resonance=row[16],
            z_phi_coherence=row[17],
            z_biomimetic_resonance=row[18],
            phi_resonance=row[19],
            information_density=row[20],
            structural_score=row[21],
            cognition_quality=row[22],
            total_qagi_score=row[23],
            mechanism_score=row[24],
            measurable_outcome_score=row[25],
            boundary_condition_score=row[26],
            failure_condition_score=row[27],
            mechanism_text=row[28],
            measurable_outcome_text=row[29],
            boundary_condition_text=row[30],
            failure_condition_text=row[31],
            review_status=row[32],
            review_labels=row[33],
            review_notes=row[34],
            run_mode=row[35],
            provider_purity=row[36],
            fallback_used=bool(row[37]),
            baseline_version=row[38],
            content_hash=row[39],
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