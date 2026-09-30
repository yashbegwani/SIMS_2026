# SIMS_2026
Project 1: Bouncing Balls in a Circular Boundary
Simulated motion under gravity using numerical integration (vel += acc*dt, pos += vel*dt).
Learned how step size dt affects accuracy, and why discrete time steps add small energy errors that can build up.
Applied vector math (dot products, unit vectors) for reflection off a curved wall.
Modelled elastic collisions between equal-mass balls by splitting velocity into normal and tangential parts.
Handled overlap and collision-detection edge cases, such as repositioning balls after a hit.
Mapped speed to colour to visualise energy.

Project 2: Falling Sand Simulation
Built a cellular automaton, where each grid cell follows simple local rules.
Implemented materials (sand, water, wood, fire, steam, leaves) and their interactions, such as sand sinking in water, fire burning wood, and water turning fire to steam.
Used timers to manage lifetimes of temporary particles like fire and steam.
Practised bounds checking and handling edge cases on a grid.
Added visuals in pygame: gradients, shimmer, fog layers, and a vignette.
Handled mouse and keyboard input for an interactive simulation.

TO PLAY - 
Mouse: hold the left mouse button and move over the grid to place the selected material.

Keys (choose the material):

1: Sand
2: Water
3: Wood (grows a small tree with leaves)
4: Fire

Sand starts selected. Try fire on wood or leaves to burn them, and water on fire to make steam.

The game also ends by itself if the grid fills up completely.