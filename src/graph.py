"""In-memory map graph representation used by the parser and simulator."""

from typing import Dict, List, Tuple, Optional
from .models import Zone, Connection


class Map:
    """Store zones, connections, and global map metadata."""

    def __init__(self) -> None:
        """Initialize an empty map structure."""
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[Tuple[str, str], Connection] = {}
        self.start_hub: Optional[Zone] = None
        self.end_hub: Optional[Zone] = None
        self.nb_drones: int = 0

    def add_zone(self, zone: Zone) -> None:
        """Register a zone by name."""
        self.zones[zone.name] = zone

    def add_connection(self, conn: Connection) -> None:
        """Register a connection in both travel directions."""
        self.connections[(conn.zone1.name, conn.zone2.name)] = conn
        self.connections[(conn.zone2.name, conn.zone1.name)] = conn

    def get_neighbors(self, zone_name: str) -> List[Zone]:
        """Return zones directly reachable from the given zone."""
        neighbors = []
        for (z1, z2), conn in self.connections.items():
            if z1 == zone_name:
                neighbors.append(self.zones[z2])
        return neighbors
