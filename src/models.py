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
    current_occupants: int = 0
    connections: List[Tuple[str, str]] = field(default_factory=list)

    def can_enter(self) -> bool:
        """Return whether the zone can accept another drone."""
        if self.zone_type == ZoneType.BLOCKED:
            return False
        return self.current_occupants < self.max_drones


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
    turns_remaining: int = 0
