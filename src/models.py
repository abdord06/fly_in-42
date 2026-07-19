from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Tuple


class ZoneType(Enum):
    NORMAL = "normal"          # 1 turn
    RESTRICTED = "restricted"  # 2 turns
    PRIORITY = "priority"      # 1 turn, priority
    BLOCKED = "blocked"        # restricted


@dataclass
class Zone:
    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    max_drones: int = 1
    color: Optional[str] = None
    current_occupants: int = 0
    connections: List[Tuple[str, str]] = field(default_factory=list)

    def can_enter(self) -> bool:
        if self.zone_type == ZoneType.BLOCKED:
            return False
        return self.current_occupants < self.max_drones


@dataclass
class Connection:
    zone1: Zone
    zone2: Zone
    max_link_capacity: int = 1
    current_traffic: int = 0


@dataclass
class Drone:
    id: str
    current_location: Zone | Connection
    turns_remaining: int = 0
