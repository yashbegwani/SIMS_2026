# SIMS_2026
Question 1. Why does the swap grid start as a copy of the current state, rather than being filled with zeros? What would happen to a grain that does not move if G′ started empty?

If the new grid starts empty (all zeros), any cell that doesn't move is never
written into it, so it simply disappears instead of staying in place. Starting
the new grid as a copy of the current one keeps every unmoved element where it
is, so only the cells that actually change need to be updated.

Question 2. Remove the randomised column order and replace it with a fixed left-to-right
scan. Run the simulation for a few hundred ticks. What happens to the shape of a sand pile?
Why?

becomes a triangle ig?
