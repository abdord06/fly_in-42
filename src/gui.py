"""Pygame visualization for the simulated drone routes."""

import pygame
from typing import Dict, List, Tuple
from .graph import Map


class Visualizer:
    """Render the map and animate drones along their planned paths."""

    def __init__(self, map_data: Map,
                 drone_paths: Dict[str, List[Tuple[str, int]]]) -> None:
        """Store the simulation state and prepare rendering resources."""
        self.map = map_data
        self.paths = drone_paths

        self.width = 1020
        self.height = 768
        self.padding = 100

        self.scale: float = 1.0
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0

        self.colors = {
            'red': (220, 50, 47),
            'green': (133, 153, 0),
            'blue': (38, 139, 210),
            'yellow': (181, 137, 0),
            'gray': (147, 161, 161),
            'default': (200, 200, 200),
            'drone': (42, 161, 152),
            'line': (88, 110, 117),
            'bg': (253, 246, 227)
        }

        self._calculate_scale()

        self.max_turn = (max(path[-1][1]
                             for path in
                             self.paths.values()) if self.paths else 0)
        self.current_turn = 0
        self.animation_progress = 0.0
        self.animation_speed = 0.015

        pygame.init()
        pygame.font.init()

        self.font_small = pygame.font.SysFont(None, 20)
        self.font_medium = pygame.font.SysFont(None, 22)
        self.font_large = pygame.font.SysFont(None, 36)

    def _calculate_scale(self) -> None:
        """Compute the viewport scale and offsets for the current map."""
        xs = [z.x for z in self.map.zones.values()]
        ys = [z.y for z in self.map.zones.values()]

        if not xs:
            self.scale = 1
            self.offset_x = self.width // 2
            self.offset_y = self.height // 2
            return

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        map_w = max(max_x - min_x, 1)
        map_h = max(max_y - min_y, 1)

        scale_x = (self.width - 2 * self.padding) / map_w
        scale_y = (self.height - 2 * self.padding) / map_h
        self.scale = min(scale_x, scale_y)

        self.offset_x = (self.padding - min_x * self.scale +
                         (self.width - 2 * self.padding - map_w *
                          self.scale) / 2)
        self.offset_y = (self.padding - min_y * self.scale +
                         (self.height - 2 *
                          self.padding - map_h * self.scale) / 2)

    def _get_coords(self, zone_name: str) -> Tuple[int, int]:
        """Convert a zone name into screen coordinates."""
        z = self.map.zones[zone_name]
        return (int(z.x * self.scale + self.offset_x),
                int(z.y * self.scale + self.offset_y))

    def _get_location_coords(self, loc_name: str) -> Tuple[int, int]:
        """Return screen coordinates for a zone or connection label."""
        if "-" in loc_name:
            z1_name, z2_name = loc_name.split("-")
            x1, y1 = self._get_coords(z1_name)
            x2, y2 = self._get_coords(z2_name)
            return ((x1 + x2) // 2, (y1 + y2) // 2)
        return self._get_coords(loc_name)

    def _draw_connections(self, screen: pygame.Surface) -> None:
        """Draw all connections on the map background."""
        for conn in self.map.connections.values():
            pos1 = self._get_coords(conn.zone1.name)
            pos2 = self._get_coords(conn.zone2.name)
            thickness = 2 if conn.max_link_capacity == 1 else 6
            pygame.draw.line(screen,
                             self.colors['line'],
                             pos1,
                             pos2,
                             thickness)

    def _draw_zones(self, screen: pygame.Surface) -> None:
        """Draw all zones with labels and colors."""
        for zone in self.map.zones.values():
            pos = self._get_coords(zone.name)

            color_name = getattr(zone, 'color', 'default')
            if color_name not in self.colors:
                color_name = 'default'

            rayon = 25 if zone.max_drones == 1 else 32
            pygame.draw.circle(screen, self.colors[color_name], pos, rayon)
            pygame.draw.circle(screen, (0, 0, 0), pos, rayon, 2)

            text = self.font_small.render(zone.name, True, (0, 0, 0))
            text_rect = text.get_rect(midbottom=(pos[0], pos[1] + 45))

            screen.blit(text, text_rect)

    def _get_drone_pos(self, path: List[Tuple[str, int]],
                       turn: int,
                       progress: float) -> Tuple[int, int]:
        """Interpolate a drone position for the current frame."""
        start_zone = path[0][0]
        start_turn = path[0][1]
        end_zone = path[0][0]
        end_turn = path[0][1]

        for i in range(len(path) - 1):
            if path[i][1] <= turn < path[i+1][1]:
                start_zone = path[i][0]
                start_turn = path[i][1]
                end_zone = path[i+1][0]
                end_turn = path[i+1][1]
                break
        if turn >= path[-1][1]:
            start_zone = end_zone = path[-1][0]

        x1, y1 = self._get_location_coords(start_zone)
        x2, y2 = self._get_location_coords(end_zone)
        total_turns = end_turn - start_turn

        if total_turns > 0:
            turns_passed = turn - start_turn

            real_progress = (turns_passed + progress) / total_turns

            x = int(x1 + (x2 - x1) * real_progress)
            y = int(y1 + (y2 - y1) * real_progress)
        else:
            x, y = x1, y1

        return (x, y)

    def _draw_drones(self, screen: pygame.Surface) -> None:
        """Draw all drones at their interpolated positions."""
        for drone_id, path in self.paths.items():
            pos = self._get_drone_pos(path,
                                      self.current_turn,
                                      self.animation_progress)

            pygame.draw.circle(screen, self.colors['drone'], pos, 14)
            pygame.draw.circle(screen, (255, 255, 255), pos, 14, 1)

            font = pygame.font.SysFont(None, 22)
            img = font.render(drone_id, True, (255, 255, 255))
            img_rect = img.get_rect(midtop=(pos[0], pos[1] - 7))
            screen.blit(img, img_rect)

    def run(self) -> None:
        """Start the interactive visualization loop."""
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly-in : 42 Drone Simulation")
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if self.current_turn < self.max_turn:
                self.animation_progress += self.animation_speed
                if self.animation_progress >= 1.0:
                    self.animation_progress = 0.0
                    self.current_turn += 1

            screen.fill(self.colors['bg'])

            self._draw_connections(screen)
            self._draw_zones(screen)
            self._draw_drones(screen)

            turn_text = self.font_large.render(f"Turn: {self.current_turn} "
                                               f"/ {self.max_turn}",
                                               True, (0, 0, 0))
            screen.blit(turn_text, (20, 20))

            pygame.display.update()
            clock.tick(60)

        pygame.quit()
