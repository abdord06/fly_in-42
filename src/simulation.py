from typing import Dict, List, Tuple
from .graph import Map
from .pathfinder import Pathfinder
from .reservation import ReservationTable


class Simulation:
    def __init__(self, map_data: Map):
        self.map = map_data
        self.table = ReservationTable()
        self.pathfinder = Pathfinder(self.map, self.table)
        self.map.start_hub.max_drones = 999999
        self.map.end_hub.max_drones = 999999
        self.drone_paths: Dict[str, List[Tuple[str, int]]] = {}

    def plan_all_routes(self) -> bool:
        for i in range(self.map.nb_drones):
            drone_id = f"D{i}"

            path = self.pathfinder.find_path_for_drone(
                start_zone_name=self.map.start_hub.name,
                end_zone_name=self.map.end_hub.name,
                start_turn=0
            )

            if not path:
                print(f"Error: no path found for drone {drone_id}.")
                return False

            self.drone_paths[drone_id] = path

            self._reserve_path_in_table(path)

        return True

    def _reserve_path_in_table(self, path: List[Tuple[str, int]]) -> None:
        for i in range(len(path) - 1):
            curr_zone_name, curr_turn = path[i]
            next_zone_name, next_turn = path[i + 1]

            if curr_zone_name == next_zone_name:
                if '-' not in next_zone_name:
                    self.table.reserve_zone(self.map.zones[next_zone_name],
                                            next_turn)
                continue

            if '-' in curr_zone_name and '-' not in next_zone_name:
                self.table.reserve_zone(self.map.zones[next_zone_name],
                                        next_turn)

            if '-' not in curr_zone_name and '-' in next_zone_name:
                z1, z2 = next_zone_name.split('-')
                target_name = z2 if z1 == curr_zone_name else z1
                conn = self.map.connections[curr_zone_name, target_name]
                current_zone = self.map.zones[curr_zone_name]
                if conn:
                    self.table.reserve_connection(conn,
                                                  current_zone,
                                                  self.map.zones[target_name],
                                                  next_turn
                                                  )
                continue

            if '-' not in curr_zone_name and '-' not in next_zone_name:
                conn = self.map.connections[curr_zone_name,
                                            next_zone_name]
                curr_zone = self.map.zones[curr_zone_name]
                next_zone = self.map.zones[next_zone_name]
                if conn:
                    self.table.reserve_connection(conn,
                                                  curr_zone,
                                                  next_zone,
                                                  next_turn)
                self.table.reserve_zone(next_zone, next_turn)

    def run_and_print(self) -> None:
        if not self.plan_all_routes():
            return

        max_turn = max(path[-1][1] for path in self.drone_paths.values())

        for current_turn in range(1, max_turn + 1):
            turn_output = []

            for drone_id, path in self.drone_paths.items():
                prev_pos = self._get_position_at_turn(path, current_turn - 1)
                curr_pos = self._get_position_at_turn(path, current_turn)

                if curr_pos and prev_pos and curr_pos != prev_pos:
                    turn_output.append(f"{drone_id}-{curr_pos}")

            if turn_output:
                print(" ".join(turn_output))

    def _get_position_at_turn(self, path: List[Tuple[str, int]],
                              target_turn: int) -> str:
        for zone_name, turn in path:
            if turn == target_turn:
                return zone_name
        return path[-1][0]
