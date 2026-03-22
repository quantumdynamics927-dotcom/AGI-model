import math
import time

PHI = (1 + math.sqrt(5)) / 2


class Node1BaseOS:
    NODE_ID = 1
    NODE_NAME = "TMT-OS Base"
    PLATONIC_SOLID = "Cube"
    GEOMETRY = {
        "faces": 6,
        "vertices": 8,
        "edges": 12,
    }

    def __init__(self):
        self.status = "active"
        self.initialized_at = time.time()
        self.phi = PHI

    def get_phi(self):
        return self.phi

    def get_geometry_info(self):
        return self.GEOMETRY

    def get_health_status(self):
        return {
            "node_id": self.NODE_ID,
            "node_name": self.NODE_NAME,
            "status": self.status,
            "platonic_solid": self.PLATONIC_SOLID,
            "geometry": self.GEOMETRY,
            "phi": self.phi,
            "initialized_at": self.initialized_at,
            "uptime_seconds": max(0.0, time.time() - self.initialized_at),
        }
