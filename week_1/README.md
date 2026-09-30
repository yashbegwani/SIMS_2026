# SIMS_2026

Question 1. A fast enough ball can end up outside the arena without the wall bounce ever
being detected. Why does the detection fail, and which of ∆t, |v|, ρ, R and g decide whether
it happens?

The simulation only checks the ball's position at the end of each time step. It never checks the path between two steps. In one step the ball moves a distance

|v|·Δt

If this is larger than the margin the test relies on, the ball can go from clearly inside to beyond the wall between two checks, and it is never seen touching the wall. This is called tunnelling.

Question 2. Set ew = 1, so that no energy is lost at a bounce, and let the ball run for a
few thousand steps. Does the peak height stay put, creep upward, or decay? Gravity and the
bounce rule are the only things acting, so if it changes at all, where is that energy coming
from?

in real life - time is continuous, so energy is conserved.
in simulation - time moves in small jumps (dt, e.g. 0.001 s). Each jump adds a tiny energy error, and thousands of steps add them up, so the peak creeps upward. -
