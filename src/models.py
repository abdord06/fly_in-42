"""Data models describing zones, connections, and drones."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Tuple


class ZoneType(Enum):
    """Supported zone behavior categories."""

    NORMAL = "normal"          # 1 turn
    RESTRICTED = "restricted"  # 2 turns
    PRIORITY = "priority"      # 1 turn, priority
    BLOCKED = "blocked"        # restricted


@dataclass
class Zone:
    """A named location on the map with occupancy and traversal rules."""

    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    max_drones: int = 1
    color: Optional[str] = None
    connections: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class Connection:
    """An undirected link between two zones."""

    zone1: Zone
    zone2: Zone
    max_link_capacity: int = 1


@dataclass
class Drone:
    """A drone and its current location state."""

    id: str
    current_location: Zone | Connection
