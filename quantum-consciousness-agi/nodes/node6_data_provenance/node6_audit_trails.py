"""
Node 6: Data Provenance (Metatron Nexus)

This module provides an immutable, blockchain-inspired audit trail for data
provenance. Each log entry is cryptographically linked to the previous one,
creating a tamper-evident chain.
"""
import hashlib
import json
import time
import logging
import os
import math
from typing import Dict, Any, List, Optional, Tuple

# Configure logging for the node
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

# --- Core Constants ---
PHI = (1 + math.sqrt(5)) / 2

class Node6AuditTrails:
    """
    Implements the functionality for Node 6, the Data Provenance service,
    conceptually mapped to the Metatron Nexus.
    """
    NODE_ID = 6
    NODE_NAME = "Data Provenance"
    PLATONIC_SOLID = "Metatron Nexus"
    GEOMETRY = {
        'faces': 13,  # Metatron's Cube has 13 circles
        'vertices': 13,
        'edges': 26   # Each circle connected to 2 others
    }

    def __init__(self, log_file_path: str = 'node6_provenance_log.jsonl'):
        """
        Initializes the Node 6 instance.

        Args:
            log_file_path: The path to the audit log file, which will be treated as an append-only ledger.
        """
        self.log_file = log_file_path
        self.status = "initializing"
        self.phi = PHI
        self.initialized_at: float | None = None
        self._initialize_log()
        self.status = "active"
        self.initialized_at = time.time()
        logger.info(f"Initialized {self.NODE_NAME} (Node {self.NODE_ID}). Log at '{self.log_file}'")

    def _hash_entry_content(self, entry_dict: Dict[str, Any]) -> str:
        """Hashes the content of a dictionary entry using SHA-256."""
        # The entry is sorted to ensure consistent, canonical hash results.
        canonical_string = json.dumps(entry_dict, sort_keys=True)
        return hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()

    def _initialize_log(self):
        """Creates the 'genesis block' or first entry if the log file does not exist."""
        try:
            # Use 'x' mode for atomic creation; fails if file already exists.
            with open(self.log_file, 'x') as f:
                genesis_entry_content = {
                    'index': 0,
                    'timestamp': time.time(),
                    'data': 'Genesis Entry: Provenance Log Initialized',
                    'previous_hash': '0' * 64
                }
                genesis_hash = self._hash_entry_content(genesis_entry_content)
                
                full_genesis_entry = {
                    'content': genesis_entry_content,
                    'hash': genesis_hash
                }
                f.write(json.dumps(full_genesis_entry) + '\n')
                logger.info("Created new provenance log with Genesis Entry.")
        except FileExistsError:
            logger.debug("Provenance log file already exists. Initialization not needed.")
            pass # File already exists, which is the expected state after first run.

    def get_last_entry(self) -> Optional[Dict[str, Any]]:
        """Reads and returns the last entry (the current head of the chain) from the log file."""
        last_line = None
        try:
            with open(self.log_file, 'rb') as f:
                # Go to the end of the file, but seek backwards to find the last newline
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR)
                last_line = f.readline().decode('utf-8')

            if last_line:
                return json.loads(last_line)
        except (FileNotFoundError, OSError, json.JSONDecodeError):
             # Fallback to reading the whole file if seeking fails (e.g., small file)
            try:
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                return json.loads(lines[-1]) if lines else None
            except (FileNotFoundError, json.JSONDecodeError):
                return None
        return None

    def add_log_entry(self, data: Any) -> Dict[str, Any]:
        """
        Adds a new entry to the immutable audit log, linking it to the previous entry.

        Args:
            data: The data to be recorded (must be JSON-serializable).

        Returns:
            The full log entry that was created and written to the log.
        """
        last_entry = self.get_last_entry()
        if not last_entry:
            # This case should ideally not happen after initialization.
            self._initialize_log()
            last_entry = self.get_last_entry()
            if not last_entry:
                 raise ConnectionError("Could not access or create the provenance log.")

        previous_hash = last_entry['hash']
        new_index = last_entry['content']['index'] + 1
        
        new_entry_content = {
            'index': new_index,
            'timestamp': time.time(),
            'data': data,
            'previous_hash': previous_hash
        }
        
        new_hash = self._hash_entry_content(new_entry_content)
        
        full_entry_to_log = {
            'content': new_entry_content,
            'hash': new_hash
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(full_entry_to_log) + '\n')
            
        logger.info(f"Added new entry #{new_index} to provenance log.")
        return full_entry_to_log

    def verify_chain(self) -> Tuple[bool, str]:
        """
        Verifies the integrity of the entire audit trail by checking all hash links.

        Returns:
            A tuple (is_valid, message) indicating the result of the verification.
        """
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return False, "Log file not found."

        if not lines:
            return True, "Log is empty, which is a valid state before the first entry."

        # Check subsequent blocks against the previous hash
        previous_entry_hash = '0' * 64
        for i, line in enumerate(lines):
            try:
                wrapper = json.loads(line)
                content = wrapper['content']
            except (json.JSONDecodeError, KeyError):
                return False, f"Invalid JSON or structure at entry index {i}."

            # Check if the chain is linked correctly
            if content['previous_hash'] != previous_entry_hash:
                return False, f"Chain broken at index {i}. Entry has previous_hash '{content['previous_hash']}' but expected '{previous_entry_hash}'."
            
            # Check if the entry's own hash is valid by recalculating it
            recalculated_hash = self._hash_entry_content(content)
            if recalculated_hash != wrapper['hash']:
                 return False, f"Entry at index {i} has been tampered with. Content does not match stored hash."

            previous_entry_hash = wrapper['hash']
        
        return True, "Provenance chain is valid and untampered."

    def get_health_status(self) -> Dict[str, Any]:
        """Returns the node's health, including a chain integrity check."""
        is_valid, message = self.verify_chain()

        if self.initialized_at is None:
            uptime = 0
            self.status = "failed_initialization"
        else:
            uptime = time.time() - self.initialized_at

        return {
            'node_id': self.NODE_ID,
            'node_name': self.NODE_NAME,
            'status': "active" if is_valid else "error_tampered_log",
            'platonic_solid': self.PLATONIC_SOLID,
            'geometry': self.GEOMETRY,
            'phi': self.phi,
            'initialized_at': self.initialized_at,
            'uptime_seconds': uptime,
            'log_file': self.log_file,
            'chain_verification': {
                'is_valid': is_valid,
                'message': message
            }
        }

    def get_geometry_info(self) -> Dict[str, int]:
        """Returns the geometric properties of the node's platonic solid."""
        return self.GEOMETRY

if __name__ == '__main__':
    """Demonstrates the functionality of the Node6AuditTrails class."""
    logger.info("--- Running Node 6 Data Provenance Standalone Demo ---")

    demo_log_file = 'temp_node6_demo_log.jsonl'
    if os.path.exists(demo_log_file):
        os.remove(demo_log_file)
        
    provenance_node = Node6AuditTrails(log_file_path=demo_log_file)

    # 1. Add some data to the log
    provenance_node.add_log_entry({'event': 'DATA_INGEST', 'source': 'sensor_A', 'value': 123.45})
    time.sleep(0.01) # ensure timestamp changes for the next entry
    provenance_node.add_log_entry({'event': 'TRANSFORM', 'function': 'normalize', 'params': {'mean': 50}})
    
    # 2. Verify the chain integrity
    is_valid, message = provenance_node.verify_chain()
    print(f"Initial chain verification: {is_valid} - {message}")
    assert is_valid

    # 3. Tamper with the log file to demonstrate tamper detection
    with open(demo_log_file, 'r+') as f:
        lines = f.readlines()
        # Change a value in the second entry (index 1) without updating its hash
        tampered_wrapper = json.loads(lines[1])
        tampered_wrapper['content']['data']['value'] = 999.99 # The tampered data
        lines[1] = json.dumps(tampered_wrapper) + '\n'
        # Go back to the beginning of the file to overwrite it
        f.seek(0)
        f.truncate()
        f.writelines(lines)
    
    print("\n--- Log file has been tampered with ---")

    # 4. Verify the chain again; it should now fail
    is_valid_tampered, message_tampered = provenance_node.verify_chain()
    print(f"Chain verification after tampering: {is_valid_tampered} - {message_tampered}")
    assert not is_valid_tampered
    assert "tampered" in message_tampered

    # Clean up the demo log file
    os.remove(demo_log_file)
    logger.info("--- Node 6 Demo Finished ---")