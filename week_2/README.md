# SIMS_2026


TO PLAY - 
Mouse: hold the left mouse button and move over the grid to place the selected material.

Keys (choose the material):

1: Sand
2: Water
3: Wood (grows a small tree with leaves)
4: Fire
5: Bedrock

Sand starts selected. Try fire on wood or leaves to burn them, and water on fire to make steam.

The game also ends by itself if the grid fills up completely.


Question 1. Why does the swap grid start as a copy of the current state, rather than being filled with zeros? What would happen to a grain that does not move if G′ started empty?

If the new grid starts empty (all zeros), any cell that doesn't move is never
written into it, so it simply disappears instead of staying in place. Starting
the new grid as a copy of the current one keeps every unmoved element where it
is, so only the cells that actually change need to be updated.

Question 2. Remove the randomised column order and replace it with a fixed left-to-right
scan. Run the simulation for a few hundred ticks. What happens to the shape of a sand pile?
Why?

becomes a triangle ig?
