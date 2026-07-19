import re
from typing import Dict
from .models import Zone, Connection, ZoneType
from .graph import Map


class Parser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.map = Map()

    def parse(self) -> Map:
        with open(self.filepath, 'r') as file:
            lines = file.readlines()

        for line_num, line in enumerate(lines, start=1):
            line = line.split('#')[0].strip()
            if not line:
                continue

            try:
                if line.startswith("nb_drones:"):
                    self._parse_nb_drones(line)

                elif (line.startswith("start_hub:") or
                      line.startswith("end_hub:") or line.startswith("hub:")):
                    self._parse_zone(line)

                elif line.startswith("connection:"):
                    self._parse_connection(line)

                else:
                    raise ValueError(f"Syntax error: '{line}'.")

            except Exception as e:
                raise ValueError(f"Parsing error in line {line_num}: {e}")

        self._validate_map()
        return self.map

    def _extract_metadata(self, line: str) -> Dict[str, str]:
        metadata = {}
        match = re.search(r'\[(.*?)\]', line)
        if match:
            tags = match.group(1).split()
            for tag in tags:
                if '=' in tag:
                    key, value = tag.split('=', 1)
                    metadata[key] = value
                else:
                    metadata['color'] = tag
        return metadata

    def _parse_nb_drones(self, line: str) -> None:
        parts = line.split(':')
        nb = int(parts[1].strip())
        if nb <= 0:
            raise ValueError("nombre of drones should be > 0.")
        self.map.nb_drones = nb

    def _parse_zone(self, line: str) -> None:
        clean_line = re.sub(r'\[.*?\]', '', line).strip()
        parts = clean_line.split()

        hub_type = parts[0].strip(':')
        name = parts[1]

        if '-' in name:
            raise ValueError("name shouldn't have '-' in it.")

        x, y = int(parts[2]), int(parts[3])
        metadata = self._extract_metadata(line)
        zone_type = ZoneType.NORMAL
        max_drones = 1
        color = None
        if 'zone' in metadata:
            zone_type = ZoneType(metadata['zone'])
        if 'color' in metadata:
            color = metadata['color']
        if 'max_drones' in metadata:
            max_drones = int(metadata['max_drones'])

        zone = Zone(name=name, x=x, y=y, zone_type=zone_type,
                    max_drones=max_drones, color=color)

        if hub_type == "start_hub":
            if self.map.start_hub:
                raise ValueError("only one possible start zone.")
            self.map.start_hub = zone
        elif hub_type == "end_hub":
            if self.map.end_hub:
                raise ValueError("only one possible end zone.")
            self.map.end_hub = zone

        self.map.add_zone(zone)

    def _parse_connection(self, line: str) -> None:
        clean_line = re.sub(r'\[.*?\]', '', line).strip()
        parts = clean_line.split()

        connection_info = parts[1]
        zone_names = connection_info.split('-')

        if len(zone_names) != 2:
            raise ValueError("connection format should be: name1-name2.")

        z1_name, z2_name = zone_names[0], zone_names[1]

        if z1_name not in self.map.zones or z2_name not in self.map.zones:
            raise ValueError("one of the zones in connections is not declared")

        if ((z1_name, z2_name) in self.map.connections or
                (z2_name, z1_name) in self.map.connections):
            raise ValueError("connection Duplicated.")

        connection_name = (z1_name, z2_name)
        if connection_name not in self.map.zones[z1_name].connections:
            self.map.zones[z1_name].connections.append(connection_name)

        if connection_name not in self.map.zones[z2_name].connections:
            self.map.zones[z2_name].connections.append(connection_name)

        metadata = self._extract_metadata(line)
        max_capacity = int(metadata.get('max_link_capacity', 1))

        conn = Connection(zone1=self.map.zones[z1_name],
                          zone2=self.map.zones[z2_name],
                          max_link_capacity=max_capacity
                          )
        self.map.add_connection(conn)

    def _validate_map(self) -> None:
        if self.map.nb_drones == 0:
            raise ValueError("L'fichier map don't have nb_drones.")
        if not self.map.start_hub:
            raise ValueError("L'fichier map don't have start_hub.")
        if not self.map.end_hub:
            raise ValueError("L'fichier map don't have end_hub.")
