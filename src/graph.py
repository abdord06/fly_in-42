from typing import Dict, List, Tuple, Optional
from .models import Zone, Connection


class Map:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[Tuple[str, str], Connection] = {}
        self.start_hub: Optional[Zone] = None
        self.end_hub: Optional[Zone] = None
        self.nb_drones: int = 0

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone

    def add_connection(self, conn: Connection) -> None:
        self.connections[(conn.zone1.name, conn.zone2.name)] = conn
        self.connections[(conn.zone2.name, conn.zone1.name)] = conn

    def get_neighbors(self, zone_name: str) -> List[Zone]:
        """Katjbd ga3 les zones li mlass9in m3a wa7d l'zone"""
        neighbors = []
        for (z1, z2), conn in self.connections.items():
            if z1 == zone_name:
                neighbors.append(self.zones[z2])
        return neighbors
