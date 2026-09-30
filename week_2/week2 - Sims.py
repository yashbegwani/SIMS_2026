import pygame
import numpy as np
import random

"""1: sand
   0: air
  -1: bedrock
   2: water
   3: wood
   4: fire
   5: steam
  -2: leaves"""

# ---------- LOOK & FEEL ----------
BG_TOP = (8, 9, 18)            # void colour at the top
BG_BOTTOM = (26, 24, 42)       # void colour at the bottom (slightly lighter, like mist pooling)
FOG_COLOR_1 = (150, 155, 200)  # cool blue-grey fog
FOG_COLOR_2 = (175, 150, 200)  # faint violet fog

ROCK_TOP = (120, 110, 165)
ROCK_BOTTOM = (55, 50, 90)
ROCK_HIGHLIGHT = (185, 175, 225)
ROCK_SHADOW = (28, 24, 48)

SAND_BASE = (222, 196, 130)
WATER_BASE = (30, 100, 215)
WATER_SURFACE = (150, 215, 255)
WOOD_BASE = (110, 72, 38)
WOOD_GRAIN = (78, 48, 24)
LEAF_BASE = (46, 158, 64)
FIRE_COLORS = [(255, 60, 0), (255, 110, 0), (255, 170, 20), (255, 220, 60)]
STEAM_COLOR = (215, 220, 240)

n = 33
CELL = 30
timers = {}          # - shared by fire and smoke, Empty dict to hold countdown/lifespan
LIFETIME = 120       # 10 seconds at clock.tick(12)

grid = np.zeros((n, n))
grid[n-1] = -1  # a bedrock row at bottom

# fixed random texture per cell (same every run)
noise = np.random.RandomState(7).randint(-14, 15, (n, n))


def tick_lifetimes(grid):
    for pos in list(timers.keys()):
        timers[pos] -= 1
        if timers[pos] <= 0:
            y, x = pos
            grid[y][x] = 0
            del timers[pos]
    return grid

def spread(x,y):
    left_ok  = (x - 1 >= 0) and (grid[y][x - 1] == 0)
    right_ok = (x + 1 < n)  and (grid[y][x + 1] == 0)
    if left_ok:
        grid[y][x-1] = 2
    elif right_ok:
        grid[y][x+1] = 2
    elif left_ok and right_ok:
        grid[y][x+1] = 2
        grid[y][x-1] = 2

def check_down(x, y):
    if y + 1 >= n:
        return "bedrock"  # bottom of grid acts like a floor
    val = grid[y + 1][x]
    if val == 0:
        return "air"
    elif val == -1:
        return "bedrock"
    elif val == 1:
        return "sand"
    elif val == 2:
        return "water"
    elif val == -2:
        return "leaves"

def check_up(x, y):
    if y - 1 < 0:
        return "bedrock"  # top of grid, nowhere to rise into
    val = grid[y - 1][x]
    if val == 0:
        return "air"
    elif val == -1:
        return "bedrock"
    elif val == 1:
        return "sand"
    elif val == 2:
        return "water"
    elif val == 3:
        return "wood"
    elif val == 4:
        return "fire"
    elif val == -2:
        return "leaves"

def is_grid_full(grid):
    return not np.any(grid == 0)   # True if there are zero air cells left

def move_up(x, y):
    timers[(y-1, x)] = timers.pop((y, x), LIFETIME)
    grid[y][x] = 0
    grid[y - 1][x] = 5

def move_down(x, y):
    #for sand -
    if grid[y][x] == 1:
        grid[y][x] = 0
        grid[y + 1][x] = 1
    #for water -
    if grid[y][x] == 2:
        grid[y][x] = 0
        grid[y + 1][x] = 2

def sink_through_water(x, y):
    # sand moves down into water's spot, water moves up into sand's old spot
    grid[y][x] = 2
    grid[y + 1][x] = 1

def break_leaves(x, y):
    # The material (sand or water) breaks the leaf below it and takes its place
    material = grid[y][x]
    grid[y][x] = 0
    grid[y + 1][x] = material

def move_up_left(x, y):
    timers[(y-1, x-1)] = timers.pop((y, x), LIFETIME)
    grid[y][x] = 0
    grid[y - 1][x - 1] = 5

def move_up_right(x, y):
    timers[(y-1, x+1)] = timers.pop((y, x), LIFETIME)
    grid[y][x] = 0
    grid[y - 1][x + 1] = 5

def move_left(x, y):
    #for sand -
    if grid[y][x] == 1:
        grid[y][x] = 0
        grid[y + 1][x - 1] = 1
    #for water -
    if grid[y][x] == 2:
        grid[y][x] = 0
        grid[y + 1][x - 1] = 2

def move_right(x, y):
    #for sand -
    if grid[y][x] == 1:
        grid[y][x] = 0
        grid[y + 1][x + 1] = 1
    #for water -
    if grid[y][x] == 2:
        grid[y][x] = 0
        grid[y + 1][x + 1] = 2

def move_sideways(x, y):
    #for sand -
    if grid[y][x] == 1:
        if y + 1 >= n:
            return  # already at bottom row, nowhere to go sideways-down to

        left_ok  = (x - 1 >= 0) and (grid[y + 1][x - 1] == 0)
        right_ok = (x + 1 < n)  and (grid[y + 1][x + 1] == 0)

        if left_ok and right_ok:
            if random.choice([1, 2]) == 1:
                move_left(x, y)
            else:
                move_right(x, y)
        elif right_ok:
            move_right(x, y)
        elif left_ok:
            move_left(x, y)
        # else: blocked both sides, stays put

    #for water -
    if grid[y][x] == 2:
        if y + 1 >= n:
            return  # already at bottom row, nowhere to go sideways-down to

        left_ok  = (x - 1 >= 0) and (grid[y + 1][x - 1] == 0)
        right_ok = (x + 1 < n)  and (grid[y + 1][x + 1] == 0)

        if left_ok and right_ok:
            if random.choice([1, 2]) == 1:
                move_left(x, y)
            else:
                move_right(x, y)
        elif right_ok:
            move_right(x, y)
        elif left_ok:
            move_left(x, y)
        else: #water spreads horizontally
            spread(x,y)

def move_up_sideways(x, y):
    if y - 1 < 0:
        return  # already at top row, nowhere to rise into

    left_ok  = (x - 1 >= 0) and (grid[y - 1][x - 1] == 0)
    right_ok = (x + 1 < n)  and (grid[y - 1][x + 1] == 0)

    if left_ok and right_ok:
        if random.choice([1, 2]) == 1:
            move_up_left(x, y)
        else:
            move_up_right(x, y)
    elif right_ok:
        move_up_right(x, y)
    elif left_ok:
        move_up_left(x, y)
    # else: blocked all three ways up, stays put

def move_fire_up(x, y):
    timers[(y-1, x)] = timers.pop((y, x), LIFETIME)
    grid[y][x] = 0
    grid[y - 1][x] = 4

def move_fire_up_left(x, y):
    timers[(y-1, x-1)] = timers.pop((y, x), LIFETIME)
    grid[y][x] = 0
    grid[y - 1][x - 1] = 4

def move_fire_up_right(x, y):
    timers[(y-1, x+1)] = timers.pop((y, x), LIFETIME)
    grid[y][x] = 0
    grid[y - 1][x + 1] = 4

def move_fire_up_sideways(x, y):
    if y - 1 < 0:
        return

    left_ok  = (x - 1 >= 0) and (grid[y - 1][x - 1] == 0)
    right_ok = (x + 1 < n)  and (grid[y - 1][x + 1] == 0)

    if left_ok and right_ok:
        if random.choice([1, 2]) == 1:
            move_fire_up_left(x, y)
        else:
            move_fire_up_right(x, y)
    elif right_ok:
        move_fire_up_right(x, y)
    elif left_ok:
        move_fire_up_left(x, y)

def step_fire_rise(grid):
    for y in range(1, n):
        for x in range(n):
            if grid[y][x] == 4:
                cell_above = check_up(x, y)
                if cell_above == "air":
                    move_fire_up(x, y)
                else:
                    move_fire_up_sideways(x, y)
    return grid

def step(grid):
    """bottom→top guarantees each grain moves at most once per step() call."""
    for y in range(n - 2, -1, -1):
        for x in range(n):
            if grid[y][x] in (1,2):
                cell_below = check_down(x, y)
                if cell_below == "air":
                    move_down(x, y)
                elif cell_below == "water" and grid[y][x] == 1: # ONLY sand sinks
                    sink_through_water(x, y)
                elif cell_below == "leaves":
                    break_leaves(x, y)
                elif cell_below in ("sand", "bedrock", "water"): # Water hits water and spreads
                    move_sideways(x, y)
    return grid


# ---------- DRAWING ----------
def clamp_color(c):
    return tuple(max(0, min(255, int(v))) for v in c)

def tint(color, d):
    return clamp_color((color[0] + d, color[1] + d, color[2] + d))

def cell_at(x, y):
    """grid value at (x, y), or None if outside the grid"""
    if 0 <= x < n and 0 <= y < n:
        return grid[y][x]
    return None

def make_background():
    bg = pygame.Surface((n * CELL, n * CELL))
    h = n * CELL
    for py in range(h):
        t = py / (h - 1)
        color = clamp_color([BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t for i in range(3)])
        pygame.draw.line(bg, color, (0, py), (n * CELL, py))
    return bg

def make_fog_layer(seed, cells_x, cells_y, alpha_max, color):
    """soft cloudy fog texture that tiles left-to-right so it can scroll forever"""
    rng = np.random.RandomState(seed)
    small = rng.rand(cells_y, cells_x)
    small[:, -1] = small[:, 0]          # make the left and right edges match
    surf = pygame.Surface((cells_x, cells_y), pygame.SRCALPHA)
    for yy in range(cells_y):
        for xx in range(cells_x):
            a = int((small[yy][xx] ** 1.6) * alpha_max)
            surf.set_at((xx, yy), (*color, a))
    return pygame.transform.smoothscale(surf, (n * CELL, n * CELL))

def make_vignette():
    """dark edges so the void feels like it goes on forever"""
    size = 66
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    c = (size - 1) / 2
    for yy in range(size):
        for xx in range(size):
            d = np.hypot(xx - c, yy - c) / c          # 0 in the centre, ~1.4 in the corners
            a = int(max(0.0, min(1.0, (d - 0.55) / 0.9)) * 170)
            surf.set_at((xx, yy), (0, 0, 8, a))
    return pygame.transform.smoothscale(surf, (n * CELL, n * CELL))

def draw_fog(screen, fog, frame, speed):
    w = n * CELL
    offset = int(frame * speed) % w
    screen.blit(fog, (-offset, 0))
    screen.blit(fog, (w - offset, 0))

def make_steam_surfaces():
    surfaces = []
    for alpha in (90, 130, 170):
        s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        pygame.draw.circle(s, (*STEAM_COLOR, alpha), (CELL // 2, CELL // 2), CELL // 2 - 2)
        pygame.draw.circle(s, (*STEAM_COLOR, alpha // 2), (CELL // 2, CELL // 2), CELL // 2)
        surfaces.append(s)
    return surfaces

def draw_bedrock_cell(screen, x, y, px, py):
    t = y / (n - 1)
    base = [ROCK_TOP[i] + (ROCK_BOTTOM[i] - ROCK_TOP[i]) * t + noise[y][x] for i in range(3)]
    pygame.draw.rect(screen, clamp_color(base), (px, py, CELL, CELL))

    def is_rock(cx, cy):
        v = cell_at(cx, cy)
        return v is None or v == -1

    if not is_rock(x, y - 1):
        pygame.draw.rect(screen, ROCK_HIGHLIGHT, (px, py, CELL, 4))
    if not is_rock(x, y + 1):
        pygame.draw.rect(screen, ROCK_SHADOW, (px, py + CELL - 4, CELL, 4))
    if not is_rock(x - 1, y):
        pygame.draw.rect(screen, ROCK_SHADOW, (px, py, 3, CELL))
    if not is_rock(x + 1, y):
        pygame.draw.rect(screen, ROCK_SHADOW, (px + CELL - 3, py, 3, CELL))

def draw_sand_cell(screen, x, y, px, py):
    base = tint(SAND_BASE, noise[y][x])
    pygame.draw.rect(screen, base, (px, py, CELL, CELL))
    # little grain speckles
    pygame.draw.rect(screen, tint(base, -28), (px + 6 + (noise[y][x] % 5), py + 18, 3, 3))
    pygame.draw.rect(screen, tint(base, 22), (px + 19, py + 7 + (noise[y][x] % 4), 3, 3))
    # light top edge where sand meets air
    if cell_at(x, y - 1) == 0:
        pygame.draw.rect(screen, tint(base, 30), (px, py, CELL, 3))

def draw_water_cell(screen, x, y, px, py, frame):
    # gentle shimmer that ripples across the water
    shimmer = int(10 * np.sin(frame * 0.15 + x * 0.8 + y * 0.4))
    depth_dark = -min(40, y * 1)      # deeper water is a bit darker
    base = tint(WATER_BASE, shimmer + depth_dark)
    pygame.draw.rect(screen, base, (px, py, CELL, CELL))
    # bright surface line where water meets air
    if cell_at(x, y - 1) == 0:
        pygame.draw.rect(screen, WATER_SURFACE, (px, py, CELL, 4))
        pygame.draw.rect(screen, tint(WATER_SURFACE, -40), (px, py + 4, CELL, 2))

def draw_wood_cell(screen, x, y, px, py):
    base = tint(WOOD_BASE, noise[y][x] // 2)
    pygame.draw.rect(screen, base, (px, py, CELL, CELL))
    # vertical grain lines
    for gx in (7, 15, 23):
        pygame.draw.line(screen, WOOD_GRAIN, (px + gx, py + 2), (px + gx, py + CELL - 3), 2)
    pygame.draw.rect(screen, tint(base, -35), (px, py, CELL, CELL), 1)

def draw_leaf_cell(screen, x, y, px, py):
    base = tint(LEAF_BASE, noise[y][x])
    pygame.draw.rect(screen, base, (px, py, CELL, CELL))
    # lighter leaf blobs
    pygame.draw.circle(screen, tint(base, 30), (px + 9, py + 9), 5)
    pygame.draw.circle(screen, tint(base, -25), (px + 20, py + 20), 5)
    if cell_at(x, y - 1) == 0:
        pygame.draw.rect(screen, tint(base, 40), (px, py, CELL, 3))

def draw_fire_cell(screen, px, py):
    # flickers a different colour every frame
    outer = random.choice(FIRE_COLORS[:3])
    inner = random.choice(FIRE_COLORS[1:])
    pygame.draw.rect(screen, outer, (px, py, CELL, CELL))
    pygame.draw.rect(screen, inner, (px + 5, py + 5, CELL - 10, CELL - 10))
    pygame.draw.rect(screen, (255, 245, 170), (px + 11, py + 11, CELL - 22, CELL - 22))

def draw_grid(screen, grid, frame, background, steam_surfaces, fog_back, fog_front, vignette):
    screen.blit(background, (0, 0))
    draw_fog(screen, fog_back, frame, 0.5)      # slow, distant fog

    for y in range(n):
        for x in range(n):
            val = grid[y][x]
            if val == 0:
                continue
            px, py = x * CELL, y * CELL
            if val == -1:
                draw_bedrock_cell(screen, x, y, px, py)
            elif val == 1:
                draw_sand_cell(screen, x, y, px, py)
            elif val == 2:
                draw_water_cell(screen, x, y, px, py, frame)
            elif val == 3:
                draw_wood_cell(screen, x, y, px, py)
            elif val == -2:
                draw_leaf_cell(screen, x, y, px, py)
            elif val == 4:
                draw_fire_cell(screen, px, py)
            elif val == 5:
                screen.blit(steam_surfaces[(x + y) % 3], (px, py))

    draw_fog(screen, fog_front, frame, 1.2)     # faster fog drifting in front
    screen.blit(vignette, (0, 0))


def spawn_wood(grid, x0=None, y0=None):
    """grows a pine-tree shape from a sand seed."""
    if x0 is None or y0 is None:
        ys, xs = np.where(grid == 1)
        if len(ys) == 0:
            return grid

        i = random.randrange(len(ys))
        y0, x0 = ys[i], xs[i]

    if grid[y0+1][x0] == 0:
        pass # Optional: Prevent mid-air spawn if you wanted to here

    # 2-block trunk
    trunk_cells = [
        (1, 0) # Base is (0,0), so (1,0) makes it 2 blocks deep
    ]

    # Cloud-like canopy
    canopy_cells = [
        (-1, -1), (-1, 0), (-1, 1),
        (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
        (-3, -1), (-3, 0), (-3, 1)
    ]

    grid[y0][x0] = 3

    for dy, dx in trunk_cells:
        y, x = y0 + dy, x0 + dx
        if 0 <= y < n and 0 <= x < n and grid[y][x] in (0, 1):
            grid[y][x] = 3

    for dy, dx in canopy_cells:
        y, x = y0 + dy, x0 + dx
        if 0 <= y < n and 0 <= x < n and grid[y][x] == 0:
            grid[y][x] = -2

    return grid


def spawn_fire(grid, x0=None, y0=None):
    if x0 is None or y0 is None:
        ys, xs = np.where(grid == 0) #spawns a fire in an air ka location
        if len(ys) == 0:
            return grid
        i = random.randrange(len(ys))
        y0,x0 = ys[i],xs[i]
    grid[y0][x0] = 4
    timers[(y0, x0  )] = LIFETIME
    return(grid)

def fire_spread(grid):
    try:
        ys, xs = np.where(grid == 4)

        for x0,y0 in zip(xs,ys):
            # Fire now checks for both wood(3) and leaves(-2)
            if (grid[y0+1][x0] in (3, -2)):
                grid[y0+1][x0] = 4
                timers[(y0+1, x0)] = LIFETIME
            elif (grid[y0-1][x0] in (3, -2)):
                grid[y0-1][x0] = 4
                timers[(y0-1, x0)] = LIFETIME
            elif grid[y0][x0+1] in (3, -2):
                grid[y0][x0+1] = 4
                timers[(y0, x0+1)] = LIFETIME
            elif grid[y0][x0-1] in (3, -2):
                grid[y0][x0-1] = 4
                timers[(y0, x0-1)] = LIFETIME
        return(grid)
    except IndexError:
        return grid

def fire_extinguish(grid):
    try:
        ys, xs = np.where(grid == 4)

        for x0,y0 in zip(xs,ys):
            if (grid[y0+1][x0] == 2):
                grid[y0+1][x0] = 5
                timers.pop((y0, x0), None)
                timers[(y0+1, x0)] = LIFETIME
                timers[(y0, x0)] = LIFETIME
                grid[y0][x0] = 5

            elif (grid[y0-1][x0] == 2):
                grid[y0-1][x0] = 5
                timers.pop((y0, x0), None)
                timers[(y0-1, x0)] = LIFETIME
                timers[(y0, x0)] = LIFETIME
                grid[y0][x0] = 5

            elif grid[y0][x0+1] == 2:
                grid[y0][x0+1] = 5
                timers.pop((y0, x0), None)
                timers[(y0, x0+1)] = LIFETIME
                timers[(y0, x0)] = LIFETIME
                grid[y0][x0] = 5

            elif grid[y0][x0-1] == 2:
                grid[y0][x0-1] = 5
                timers.pop((y0, x0), None)
                timers[(y0, x0-1)] = LIFETIME
                timers[(y0, x0)] = LIFETIME
                grid[y0][x0] = 5

        return(grid)
    except IndexError:
        return grid

def step_smoke(grid):
    for y in range(1, n):   # top-to-bottom is fine here since smoke moves UP, away from unprocessed rows
        for x in range(n):
            if grid[y][x] == 5:
                cell_above = check_up(x, y)
                if cell_above == "air":
                    move_up(x, y)
                else:
                    move_up_sideways(x, y)
    return grid

pygame.init()
screen = pygame.display.set_mode((n * CELL, n * CELL))
clock = pygame.time.Clock()

background = make_background()
steam_surfaces = make_steam_surfaces()
fog_back = make_fog_layer(3, 9, 7, 70, FOG_COLOR_1)
fog_front = make_fog_layer(11, 7, 5, 45, FOG_COLOR_2)
vignette = make_vignette()

current_material = 1  # 1=sand, 2=water, 3=wood, 4=fire

count = 0
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_1:
                current_material = 1
            elif e.key == pygame.K_2:
                current_material = 2
            elif e.key == pygame.K_3:
                current_material = 3
            elif e.key == pygame.K_4:
                current_material = 4

    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        gx, gy = mx // CELL, my // CELL
        if 0 <= gx < n and 0 <= gy < n:
            if current_material == 1 and grid[gy][gx] == 0:
                grid[gy][gx] = 1
            elif current_material == 2 and grid[gy][gx] == 0:
                grid[gy][gx] = 2
            elif current_material == 3:
                grid = spawn_wood(grid, gx, gy)
            elif current_material == 4:
                grid = spawn_fire(grid, gx, gy)

    if is_grid_full(grid):
        running = False
    count += 1

    grid = step(grid)
    grid = fire_spread(grid)
    grid = fire_extinguish(grid)
    grid = step_smoke(grid)
    if count%6 == 0:
        grid = step_fire_rise(grid)
    grid = tick_lifetimes(grid)

    draw_grid(screen, grid, count, background, steam_surfaces, fog_back, fog_front, vignette)
    pygame.display.flip()
    clock.tick(12)

pygame.quit()