import pygame
import numpy as np
import random

"""1: sand
   0: air
   9: bedrock
   2: water
   3: wood
   4: fire
   5: steam
  -2: leaves"""

COLORS = {
     9: (60, 60, 65),     # bedrock
     0: (20, 20, 30),     # air/void
     1: (194, 178, 128),  # sand
     2: (30, 70, 170),    # water
     3: (101, 67, 33),    # wood
     4: (240, 90, 20),    # fire
     5: (200, 200, 220),  # steam
    -2: (34, 139, 34)     # leaves
}

n = 33
CELL = 30
timers = {}
LIFETIME = 120

SPHERE_RADIUS = 1   # size of the water blob you drop
SPREAD_RANGE = 2    # how many cells sideways water can spread after landing

grid = np.zeros((n, n))
grid[n-1] = 9

# how many sideways spreads each water cell has left (refills whenever it falls)
flow = np.zeros((n, n), dtype=int)

# fixed per-cell shade, gives each cell a bit of texture
noise = np.random.randint(-14, 15, (n, n))

# water cells that already spread sideways this step (so they don't move twice)
spread_done = set()

def tick_lifetimes(grid):
    for pos in list(timers.keys()):
        y, x = pos
        if grid[y][x] not in (4, 5):    # cell changed (e.g. you drew bedrock), drop stale timer
            del timers[pos]
            continue
        timers[pos] -= 1
        if timers[pos] <= 0:
            grid[y][x] = 0
            del timers[pos]
    return grid

def spread(x,y):
    if flow[y][x] <= 0:
        return  # used up its spread, stays still (no more endless jiggling)
    left_ok  = (x - 1 >= 0) and (grid[y][x - 1] == 0)
    right_ok = (x + 1 < n)  and (grid[y][x + 1] == 0)
    if left_ok and right_ok:
        dx = random.choice([-1, 1])
    elif left_ok:
        dx = -1
    elif right_ok:
        dx = 1
    else:
        return
    grid[y][x] = 0
    grid[y][x + dx] = 2
    flow[y][x + dx] = flow[y][x] - 1
    spread_done.add((x + dx, y))

def check_down(x, y):
    if y + 1 >= n:
        return "bedrock"
    val = grid[y + 1][x]
    if val == 0:
        return "air"
    elif val == 9:
        return "bedrock"
    elif val == 1:
        return "sand"
    elif val == 2:
        return "water"
    elif val == 3:
        return "wood"
    elif val == -2:
        return "leaves"

def check_up(x, y):
    if y - 1 < 0:
        return "bedrock"
    val = grid[y - 1][x]
    if val == 0:
        return "air"
    elif val == 9:
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
    return not np.any(grid == 0)

def move_up(x, y):
    timers[(y-1, x)] = timers.pop((y, x), LIFETIME)
    grid[y][x] = 0
    grid[y - 1][x] = 5

def move_down(x, y):
    if grid[y][x] == 1:
        grid[y][x] = 0
        grid[y + 1][x] = 1
    if grid[y][x] == 2:
        grid[y][x] = 0
        grid[y + 1][x] = 2
        flow[y + 1][x] = SPREAD_RANGE   # falling refills the spread

def sink_through_water(x, y):
    grid[y][x] = 2
    grid[y + 1][x] = 1
    flow[y][x] = SPREAD_RANGE

def break_leaves(x, y):
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
    if grid[y][x] == 1:
        grid[y][x] = 0
        grid[y + 1][x - 1] = 1
    if grid[y][x] == 2:
        grid[y][x] = 0
        grid[y + 1][x - 1] = 2
        flow[y + 1][x - 1] = SPREAD_RANGE

def move_right(x, y):
    if grid[y][x] == 1:
        grid[y][x] = 0
        grid[y + 1][x + 1] = 1
    if grid[y][x] == 2:
        grid[y][x] = 0
        grid[y + 1][x + 1] = 2
        flow[y + 1][x + 1] = SPREAD_RANGE

def move_sideways(x, y):
    if grid[y][x] == 1:
        if y + 1 >= n:
            return
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

    if grid[y][x] == 2:
        if y + 1 >= n:
            return
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
        else:
            spread(x,y)

def move_up_sideways(x, y):
    if y - 1 < 0:
        return
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
    spread_done.clear()
    for y in range(n - 2, -1, -1):
        for x in range(n):
            if (x, y) in spread_done:
                continue  # this water already spread sideways this step
            if grid[y][x] in (1,2):
                cell_below = check_down(x, y)
                if cell_below == "air":
                    move_down(x, y)
                elif cell_below == "water" and grid[y][x] == 1:
                    sink_through_water(x, y)
                elif cell_below == "leaves":
                    break_leaves(x, y)
                elif cell_below in ("sand", "bedrock", "water", "wood"):
                    move_sideways(x, y)
    return grid

def shade(color, d):
    return tuple(max(0, min(255, c + d)) for c in color)

def draw_grid(screen, grid):
    for y in range(n):
        for x in range(n):
            val = int(grid[y][x])
            if val == 0:
                continue
            if val == 5:  # smoke = circle
                center = (x * CELL + CELL // 2, y * CELL + CELL // 2)
                pygame.draw.circle(screen, COLORS[5], center, CELL // 2 - 3)
            elif val == 4:  # fire flickers
                color = shade(COLORS[4], random.randint(-40, 40))
                pygame.draw.rect(screen, color, (x * CELL, y * CELL, CELL, CELL))
            else:
                color = shade(COLORS[val], noise[y][x])
                pygame.draw.rect(screen, color, (x * CELL, y * CELL, CELL, CELL))

def spawn_water(grid, x0, y0, r=SPHERE_RADIUS):
    """drops a round blob of water (made of rect cells) centred on the click."""
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                y, x = y0 + dy, x0 + dx
                if 0 <= y < n and 0 <= x < n and grid[y][x] == 0:
                    grid[y][x] = 2
                    flow[y][x] = SPREAD_RANGE
    return grid

def spawn_wood(grid, x0=None, y0=None):
    """grows a pine-tree shape from a sand seed."""
    if x0 is None or y0 is None:
        ys, xs = np.where(grid == 1)
        if len(ys) == 0:
            return grid
        i = random.randrange(len(ys))
        y0, x0 = ys[i], xs[i]

    trunk_cells = [(1, 0)]
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
        ys, xs = np.where(grid == 0)
        if len(ys) == 0:
            return grid
        i = random.randrange(len(ys))
        y0, x0 = ys[i], xs[i]
    grid[y0][x0] = 4
    timers[(y0, x0)] = LIFETIME
    return grid

def fire_spread(grid):
    try:
        ys, xs = np.where(grid == 4)
        for x0, y0 in zip(xs, ys):
            if grid[y0+1][x0] in (3, -2):
                grid[y0+1][x0] = 4
                timers[(y0+1, x0)] = LIFETIME
            elif grid[y0-1][x0] in (3, -2):
                grid[y0-1][x0] = 4
                timers[(y0-1, x0)] = LIFETIME
            elif grid[y0][x0+1] in (3, -2):
                grid[y0][x0+1] = 4
                timers[(y0, x0+1)] = LIFETIME
            elif grid[y0][x0-1] in (3, -2):
                grid[y0][x0-1] = 4
                timers[(y0, x0-1)] = LIFETIME
        return grid
    except IndexError:
        return grid

def fire_extinguish(grid):
    ys, xs = np.where(grid == 4)
    for y0, x0 in zip(ys, xs):
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            y, x = y0 + dy, x0 + dx
            if 0 <= y < n and 0 <= x < n and grid[y][x] == 2:
                grid[y][x] = 0          # water is deleted
                grid[y0][x0] = 5        # fire becomes smoke
                timers[(y0, x0)] = LIFETIME
                break
    return grid

def step_smoke(grid):
    for y in range(1, n):
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

current_material = 1  # 0=erase, 1=sand, 2=water, 3=wood, 4=fire, 5=bedrock

count = 0
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_0:
                current_material = 0
            elif e.key == pygame.K_1:
                current_material = 1
            elif e.key == pygame.K_2:
                current_material = 2
            elif e.key == pygame.K_3:
                current_material = 3
            elif e.key == pygame.K_4:
                current_material = 4
            elif e.key == pygame.K_5:
                current_material = 5
        # water drops one blob per click (not every frame while held)
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and current_material == 2:
            gx, gy = e.pos[0] // CELL, e.pos[1] // CELL
            if 0 <= gx < n and 0 <= gy < n:
                grid = spawn_water(grid, gx, gy)

    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        gx, gy = mx // CELL, my // CELL
        if 0 <= gx < n and 0 <= gy < n:
            if current_material == 0:
                grid[gy][gx] = 0   # erase anything, including bedrock
            elif current_material == 1 and grid[gy][gx] == 0:
                grid[gy][gx] = 1
            elif current_material == 3:
                grid = spawn_wood(grid, gx, gy)
            elif current_material == 4:
                grid = spawn_fire(grid, gx, gy)
            elif current_material == 5 and grid[gy][gx] == 0:
                grid[gy][gx] = 9

    if is_grid_full(grid):
        running = False
    count += 1

    grid = step(grid)
    grid = fire_spread(grid)
    grid = fire_extinguish(grid)
    grid = step_smoke(grid)
    if count % 6 == 0:
        grid = step_fire_rise(grid)
    grid = tick_lifetimes(grid)

    screen.fill(COLORS[0])
    draw_grid(screen, grid)
    pygame.display.flip()
    clock.tick(12)

pygame.quit()
