"""A* style route planner for drone movement across the map."""

import heapq
import math
from typing import List, Tuple, Optional
from .models import ZoneType
from .graph import Map
from .reservation import ReservationTable


class State:
    """Search state used by the priority queue."""

    def __init__(self, cost: float,
                 turn: int,
                 zone_name: str,
                 path: List[Tuple[str, int]],
                 g_score: float = 0.0
                 ) -> None:
        """Create a search state with path and scoring information."""
        self.cost = cost
        self.turn = turn
        self.zone_name = zone_name
        self.path = path
        self.g_score = g_score

    def __lt__(self, other: 'State') -> bool:
        """Compare states by heuristic cost, then actual path score."""
        if self.cost == other.cost:
            return self.g_score < other.g_score
        return self.cost < other.cost


class Pathfinder:
    """Compute valid drone paths while respecting reservations
    and zone rules."""

    def __init__(self, map_data: Map, reservation_table: ReservationTable):
        """Store the map and reservation table used during search."""
        self.map = map_data
        self.table = reservation_table

    def _heuristic(self, current_zone: str, target_zone: str) -> float:
        """Estimate the remaining distance between two zones."""
        current = self.map.zones[current_zone]
        target = self.map.zones[target_zone]

        dx = current.x - target.x
        dy = current.y - target.y
        return math.sqrt((dx * dx) + (dy * dy))

    def find_path_for_drone(self, start_zone_name: str,
                            end_zone_name: str,
                            start_turn:
                                int) -> Optional[List[Tuple[str, int]]]:
        """Find a path from the start zone to the end zone for one drone."""

        open_set: List[State] = []
        initial_state = State(0.0,
                              start_turn,
                              start_zone_name,
                              [(start_zone_name, start_turn)],
                              g_score=0.0
                              )
        heapq.heappush(open_set, initial_state)

        visited = set()

        while open_set:
            current = heapq.heappop(open_set)

            if current.zone_name == end_zone_name:
                return current.path

            state_key = (current.zone_name, current.turn)
            if state_key in visited:
                continue
            visited.add(state_key)

            curr_zone = self.map.zones[current.zone_name]

            if self.table.is_zone_available(curr_zone, current.turn + 1):
                new_path = list(current.path)
                new_path.append((curr_zone.name, current.turn + 1))
                new_g = current.g_score + 1.0

                wait_state = State(
                    cost=current.turn + 1 + self._heuristic(curr_zone.name,
                                                            end_zone_name),
                    turn=current.turn + 1,
                    zone_name=curr_zone.name,
                    path=new_path,
                    g_score=new_g
                )
                heapq.heappush(open_set, wait_state)

            for conn_name in curr_zone.connections:
                conn = self.map.connections[conn_name]
                neighbor_name = (conn.zone1.name
                                 if conn.zone2.name == curr_zone.name
                                 else conn.zone2.name)
                neighbor_zone = self.map.zones[neighbor_name]

                if neighbor_zone.zone_type == ZoneType.BLOCKED:
                    continue

                if neighbor_zone.zone_type == ZoneType.RESTRICTED:
                    if (self.table.is_connection_available(conn,
                                                           curr_zone,
                                                           neighbor_zone,
                                                           current.turn + 1)
                        and
                        self.table.is_zone_available(neighbor_zone,
                                                     current.turn + 2)):

                        conn_string = f"{curr_zone.name}-{neighbor_zone.name}"
                        new_path = list(current.path)
                        new_path.append((conn_string, current.turn + 1))
                        new_path.append((neighbor_zone.name, current.turn + 2))
                        new_g = current.g_score + 2.002
                        move_state = State(
                            cost=(current.turn + 2 +
                                  self._heuristic(neighbor_zone.name,
                                                  end_zone_name)),
                            turn=current.turn + 2,
                            zone_name=neighbor_zone.name,
                            path=new_path,
                            g_score=new_g
                        )
                        heapq.heappush(open_set, move_state)

                else:
                    if (self.table.is_connection_available(conn,
                                                           curr_zone,
                                                           neighbor_zone,
                                                           current.turn + 1)
                        and
                        self.table.is_zone_available(neighbor_zone,
                                                     current.turn + 1)):

                        new_path = list(current.path)
                        new_path.append((neighbor_zone.name, current.turn + 1))

                        cost_choice = (0.0 if neighbor_zone.zone_type ==
                                       ZoneType.PRIORITY
                                       else 1.0)
                        new_g = current.g_score + cost_choice + 0.001
                        move_state = State(
                            cost=(current.turn + cost_choice +
                                  self._heuristic(neighbor_zone.name,
                                                  end_zone_name)),
                            turn=current.turn + 1,
                            zone_name=neighbor_zone.name,
                            path=new_path,
                            g_score=new_g
                        )
                        heapq.heappush(open_set, move_state)

        return None
