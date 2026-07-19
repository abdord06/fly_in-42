from typing import Dict, Tuple, Set
from .models import Connection, Zone


class ReservationTable():
    def __init__(self) -> None:
        self.zone_reservations: Dict[Tuple[str, int], int] = {}
        self.connection_reservations: Dict[Tuple[str, str, int], int] = {}
        self.directional_swaps: Set[tuple[str, str, int]] = set()

    def is_zone_available(self, zone: Zone, turn: int) -> bool:
        key = (zone.name, turn)
        current_occupancy = self.zone_reservations.get(key, 0)
        return current_occupancy < zone.max_drones

    def reserve_zone(self, zone: Zone, turn: int) -> None:
        if not self.is_zone_available(zone, turn):
            raise ValueError(f"Erreur: zone {zone.name} full in turn {turn}")

        key = (zone.name, turn)
        self.zone_reservations[key] = self.zone_reservations.get(key, 0) + 1

    def is_connection_available(self, connection: Connection,
                                from_zone: Zone,
                                to_zone: Zone,
                                turn: int) -> bool:
        key = (connection.zone1.name, connection.zone2.name, turn)
        if (self.connection_reservations.get(key, 0) >=
                connection.max_link_capacity):
            return False

        direct_key = (to_zone.name, from_zone.name, turn)
        if direct_key in self.directional_swaps:
            return False

        return True

    def reserve_connection(self, connection: Connection,
                           from_zone: Zone,
                           to_zone: Zone,
                           turn: int) -> None:
        if not self.is_connection_available(connection,
                                            from_zone,
                                            to_zone,
                                            turn):
            raise ValueError(f"Erreur: connection {connection.zone1.name}-"
                             f"{connection.zone2.name} full in turn {turn}")

        key = (connection.zone1.name, connection.zone2.name, turn)

        self.connection_reservations[key] = self.connection_reservations.get(
            key, 0) + 1
        self.directional_swaps.add((from_zone.name, to_zone.name, turn))
