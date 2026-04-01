"""
Node 8: Quantum Observer (Octave)

This node monitors blockchain events, confirms NFT minting, and observes
quantum computations for "collapse" events. It is mapped to the Octave,
representing a higher harmonic of awareness of the system's state.
"""
import time
import logging
from typing import Dict, Any, List, Optional

# The following are type hints for dependency injection. They are not imported
# directly to maintain loose coupling between the nodes.
# if False:
#     from TMT-OS.node4_nft_layer import Node4NFTLayer
#     from qvae_bridge import QVAEBridge

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - [Node8-Observer] - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

class Node8QuantumObserver:
    """
    Implements Node 8 functionality for monitoring on-chain and quantum events.
    It acts as a listener to other nodes, such as the NFT Layer and QVAE Bridge.
    """
    NODE_ID = 8
    NODE_NAME = "Quantum Observer"
    PLATONIC_SOLID = "Octave" # Conceptual Mapping (8th harmonic)
    GEOMETRY = {
        'description': "Represents the 8th step in a harmonic series, observing the system from a higher level of abstraction."
    }

    def __init__(self, nft_layer_node: 'Node4NFTLayer', qvae_bridge_node: 'QVAEBridge'):
        """
        Initializes the observer.
        
        Args:
            nft_layer_node: An instance of Node4NFTLayer to observe for minting events.
            qvae_bridge_node: An instance of QVAEBridge to observe for quantum job results.
        """
        self.status = "active"
        self.nft_layer = nft_layer_node
        self.qvae_bridge = qvae_bridge_node
        self.notifications: List[str] = []
        
        # Register itself as a listener to the blockchain mock object within the NFT node
        if self.nft_layer and hasattr(self.nft_layer.blockchain, 'add_listener'):
            self.nft_layer.blockchain.add_listener(self)
        else:
            logger.warning("Could not register as a listener to the provided NFT layer node.")
        
        logger.info(f"Initialized {self.NODE_NAME} (Node {self.NODE_ID}, {self.PLATONIC_SOLID}).")

    def on_mint_event(self, mint_event: Dict[str, Any]):
        """
        Callback method triggered by the MockBlockchain upon a successful mint event.
        """
        token_id = mint_event.get('token_id')
        owner = mint_event.get('owner')
        logger.info(f"EVENT DETECTED: New asset (Token {token_id}) was minted to owner {owner}.")
        
        # Trigger confirmation and notification process
        self.confirm_minting(token_id)
        notification_msg = f"NFT Mint Confirmed: Token ID {token_id} is now verifiably owned by {owner}."
        self.send_notification("MINT_CONFIRMATION", notification_msg)

    def confirm_minting(self, token_id: int, required_confirmations: int = 3):
        """Simulates waiting for a number of blockchain confirmations to consider a transaction final."""
        logger.info(f"Waiting for {required_confirmations} blockchain confirmations for Token ID {token_id}...")
        for i in range(required_confirmations):
            time.sleep(0.05) # Simulate block time
            logger.debug(f"Confirmation {i+1}/{required_confirmations} received for Token ID {token_id}.")
        logger.info(f"Token ID {token_id} is now considered finalized on the mock chain.")

    def detect_quantum_collapse(self, job_id: str, collapse_threshold: float = 0.9) -> bool:
        """
        Observes a quantum job's result and detects if a "collapse" to a dominant state occurred.
        A collapse is defined as one outcome having a probability above the threshold.
        """
        if not self.qvae_bridge:
            logger.error("QVAE Bridge not configured for this observer.")
            return False
            
        job_status = self.qvae_bridge.get_job_status(job_id)
        if not job_status or job_status.get('status') != 'completed':
            logger.warning(f"Cannot detect collapse: Job {job_id} is not yet complete.")
            return False

        results = job_status.get('result', {})
        if not results:
            logger.warning(f"Job {job_id} has no results to analyze.")
            return False

        total_shots = sum(results.values())
        if total_shots == 0:
            return False

        most_probable_state = max(results, key=results.get)
        probability = results[most_probable_state] / total_shots

        if probability >= collapse_threshold:
            msg = (
                   f"QUANTUM COLLAPSE DETECTED in job {job_id}. "
                   f"State '{most_probable_state}' observed with {probability:.2%} probability.")
            self.send_notification("QUANTUM_COLLAPSE", msg)
            return True
        else:
            msg = (f"No significant quantum collapse detected in job {job_id}. "
                   f"Highest probability was {probability:.2%}, below the {collapse_threshold:.0%} threshold.")
            logger.info(msg)
            return False

    def send_notification(self, event_type: str, message: str):
        """
        Simulates sending a notification to other systems or users.
        In this mock implementation, it just logs the message and appends it to a local list.
        """
        notification = f"[{event_type}] {time.ctime()}: {message}"
        self.notifications.append(notification)
        logger.info(f"NOTIFICATION SENT: {notification}")

    def get_health_status(self) -> Dict[str, Any]:
        """Returns the current operational status and metrics of the node."""
        return {
            'node_id': self.NODE_ID,
            'node_name': self.NODE_NAME,
            'status': self.status,
            'notifications_sent': len(self.notifications)
        }

if __name__ == '__main__':
    # This demo requires instances of other nodes to be created first.
    import sys
    import os
    import importlib
    
    # Add project root to path to allow importing other node modules
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Dynamically import Node 4 due to the hyphen in its parent directory 'TMT-OS'
    node4_module = importlib.import_module("TMT-OS.node4_nft_layer")
    Node4NFTLayer = node4_module.Node4NFTLayer
    from qvae_bridge import get_bridge

    logger.info("--- Running Node 8 Quantum Observer Standalone Demo ---")

    # 1. Instantiate the nodes this observer depends on
    node4 = Node4NFTLayer()
    node9 = get_bridge() # Uses singleton pattern from qvae_bridge

    # 2. Instantiate the observer, connecting it to the NFT layer's blockchain
    observer = Node8QuantumObserver(nft_layer_node=node4, qvae_bridge_node=node9)

    # 3. Trigger a mint event, which the observer should detect via its listener
    logger.info("\n--- Triggering a mint event for the observer to detect ---")
    node4.create_asset("0xObserverTest", {"name": "Observable Asset"})
    
    assert len(observer.notifications) > 0, "Observer should have sent a notification."
    assert "MINT_CONFIRMATION" in observer.notifications[-1]

    # 4. Simulate quantum jobs and check for collapse detection
    logger.info("\n--- Simulating quantum jobs to check for collapse detection ---")
    
    # Manually create a job with a "collapsed" result for testing
    job_id_collapsed = f"job_manual_{int(time.time())}"
    node9.jobs[job_id_collapsed] = {
        'status': 'completed',
        'result': {'01011': 950, '10100': 50}, # 95% probability -> collapse
    }
    
    # Manually create a job with a "superpositioned" result
    job_id_superposed = f"job_manual_{int(time.time())+1}"
    node9.jobs[job_id_superposed] = {
        'status': 'completed',
        'result': {'01011': 510, '10100': 490}, # ~50/50 probability -> no collapse
    }

    # Run collapse detection on both jobs
    did_collapse = observer.detect_quantum_collapse(job_id_collapsed)
    assert did_collapse, "Should have detected collapse in the first job."
    
    did_not_collapse = observer.detect_quantum_collapse(job_id_superposed)
    assert not did_not_collapse, "Should not have detected collapse in the second job."
    
    logger.info("\n--- Node 8 Demo Finished ---")
