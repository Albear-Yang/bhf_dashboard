import pygame
import sys
from enum import Enum

# Constants
WINDOW_SCALE = 20  # size of each grid cell in pixels
BRUSH_WIDTH = 5    # brush height in cells
PHOTO_DIM = (30, 30)  # global map dimensions

# Example: vertical crops
CROP_LIST = [
    (10, 5, 3, 5),
    (10, 15, 3, 5),
    (10, 25, 3, 5),
]

class CropUnit(Enum):
    CROP = 2
    PADDING = 1
    WEED = 0

class Side(Enum):
    RIGHT = 0
    LEFT = 1
    TOP = 2
    BOTTOM = 3

class PlanArm:
    def __init__(self, photo_dim: tuple[int, int], list_crop: list[tuple[int, int, int, int]], brush_width: int):
        self.map_width, self.map_height = photo_dim
        # initialize full map as weeds
        self.map = [[CropUnit.WEED for _ in range(self.map_width)] for _ in range(self.map_height)]
        self.brush_width = brush_width
        # mark crops and padding
        for c_x, c_y, c_w, c_h in list_crop:
            pad_x = c_w // 2
            pad_y = c_h // 2
            # padding zone
            for yy in range(max(0, c_y - pad_y), min(self.map_height, c_y + pad_y + 1)):
                for xx in range(max(0, c_x - pad_x), min(self.map_width, c_x + pad_x + 1)):
                    self.map[yy][xx] = CropUnit.PADDING
            # crop center
            if 0 <= c_y < self.map_height and 0 <= c_x < self.map_width:
                self.map[c_y][c_x] = CropUnit.CROP

    def empty_plan(self, arm_pos: tuple[int, int], map_dim: tuple[int, int], which_corner: tuple[Side, Side]) -> list[tuple[int, int]]:
        """
        Generate a zigzag path within a weed-only subregion.

        Args:
            arm_pos: top-left origin of subregion (x0, y0)
            map_dim: dimensions of subregion (width, height)
            which_corner: (horizontal start side, vertical start side)
        Returns:
            List of (x,y) coordinates for the brush center, ending in a favourable position.
        """
        path: list[tuple[int, int]] = []
        x0, y0 = arm_pos
        width, height = map_dim
        if width <= 0 or height <= 0:
            return []
        # initial sweep directions
        horizontal = 1 if which_corner[0] == Side.LEFT else -1
        vertical = 1 if which_corner[1] == Side.TOP else -1

        # Zigzag sweep within the subregion (banded by brush height)
        y_range = (range(0, height, self.brush_width)
                   if vertical == 1 else range(height - 1, -1, -self.brush_width))
        for y_start in y_range:
            # compute center line for this band
            mid_y = y0 + y_start + (self.brush_width // 2) * vertical
            # horizontal pass
            x_range = (range(0, width) if horizontal == 1 else range(width - 1, -1, -1))
            for dx in x_range:
                path.append((x0 + dx, mid_y))
            # move vertically to next band center
            for _ in range(self.brush_width):
                last_x, last_y = path[-1]
                path.append((last_x, last_y + vertical))
            # flip horizontal direction
            horizontal *= -1

        # Handle leftover rows if height not divisible by brush_height
        leftover = height % self.brush_width
        if leftover:
            # starting offset for leftover band
            last_offset = y_range[-1]
            # next band's start
            next_offset = last_offset + (self.brush_width * vertical)
            mid_y = y0 + next_offset + (leftover // 2) * vertical
            x_range = (range(0, width) if horizontal == 1 else range(width - 1, -1, -1))
            for dx in x_range:
                path.append((x0 + dx, mid_y))

        # Bring the arm to the side of the subregion (favourable position)
        if path:
            last_x, last_y = path[-1]
            # horizontal return
            target_x = x0 + (width - 1 if which_corner[0] == Side.RIGHT else 0)
            while last_x < target_x:
                last_x += 1
                path.append((last_x, last_y))
            while last_x > target_x:
                last_x -= 1
                path.append((last_x, last_y))
            # vertical return
            target_y = y0 + (0 if which_corner[1] == Side.TOP else height - 1)
            while last_y < target_y:
                last_y += 1
                path.append((last_x, last_y))
            while last_y > target_y:
                last_y -= 1
                path.append((last_x, last_y))

        return path

    def global_plan(self) -> list[tuple[int, int]]:
        """
        Sweep the full map by horizontal bands, avoiding crops and padding.
        """
        visited = [[False] * self.map_width for _ in range(self.map_height)]
        full_path: list[tuple[int, int]] = []
        for y in range(0, self.map_height, self.brush_width):
            x = 0
            while x < self.map_width:
                if self.map[y][x] != CropUnit.WEED or visited[y][x]:
                    x += 1
                    continue
                start = x
                while x < self.map_width:
                    ok = True
                    for dy in range(self.brush_width):
                        yy = y + dy
                        if yy >= self.map_height or self.map[yy][x] != CropUnit.WEED or visited[yy][x]:
                            ok = False
                            break
                    if not ok:
                        break
                    x += 1
                region_width = x - start
                if region_width > 0:
                    sub = self.empty_plan((start, y), (region_width, self.brush_width), (Side.LEFT, Side.TOP))
                    full_path.extend(sub)
                    for dx in range(region_width):
                        for dy in range(self.brush_width):
                            yy, xx = y + dy, start + dx
                            if 0 <= yy < self.map_height and 0 <= xx < self.map_width:
                                visited[yy][xx] = True
        return full_path

# -- Visualization: Subregion within Global Map --
def visualize_subregion(top_left: tuple[int, int], sub_dim: tuple[int, int], corner: tuple[Side, Side]):
    plan = PlanArm(PHOTO_DIM, CROP_LIST, BRUSH_WIDTH)
    path = plan.empty_plan(top_left, sub_dim, corner)
    covered = set()
    for cx, cy in path:
        for d in range(-(BRUSH_WIDTH // 2), BRUSH_WIDTH // 2 + 1):
            py = cy + d
            if 0 <= py < PHOTO_DIM[1]:
                covered.add((cx, py))

    pygame.init()
    screen = pygame.display.set_mode((PHOTO_DIM[0] * WINDOW_SCALE, PHOTO_DIM[1] * WINDOW_SCALE))
    pygame.display.set_caption(f"Subregion Sweep at {top_left} size {sub_dim}")
    clock = pygame.time.Clock()
    idx = 0
    running = True
    last_pos = None
    while running:
        for y in range(PHOTO_DIM[1]):
            for x in range(PHOTO_DIM[0]):
                unit = plan.map[y][x]
                if unit == CropUnit.WEED:
                    base = (0, 100, 0)
                elif unit == CropUnit.PADDING:
                    base = (200, 200, 0)
                else:
                    base = (255, 0, 0)
                screen.fill(base, (x * WINDOW_SCALE, y * WINDOW_SCALE, WINDOW_SCALE, WINDOW_SCALE))
        for (x, y) in covered:
            screen.fill((0, 0, 255), (x * WINDOW_SCALE, y * WINDOW_SCALE, WINDOW_SCALE, WINDOW_SCALE))
        if idx < len(path):
            bx, by = path[idx]
            last_pos = (bx, by)
            idx += 1
        elif last_pos:
            bx, by = last_pos
        else:
            bx, by = (-1, -1)
        if bx >= 0:
            rect = pygame.Rect(
                bx * WINDOW_SCALE,
                (by - BRUSH_WIDTH // 2) * WINDOW_SCALE,
                WINDOW_SCALE,
                BRUSH_WIDTH * WINDOW_SCALE
            )
            pygame.draw.rect(screen, (0, 255, 255), rect)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
        pygame.display.flip()
        clock.tick(10)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Example: sweep a 10x19 subregion at position (5,5) with return to favourable position
    visualize_subregion((7, 10), (10, 11), (Side.RIGHT, Side.BOTTOM))
