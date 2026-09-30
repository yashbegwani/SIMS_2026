import pygame
import numpy as np
import math

pygame.init()

def SPEED_COLOR(v):
    if v > 4000:
        return [255, 0, 150]    # hot pink - fastest
    if v > 3200 and v<4000:
        return [200, 0, 200]    # magenta
    if v > 2200 and v<3200:
        return [140, 0, 220]    # violet
    if v > 1500 and v<2200:
        return [80, 60, 230]    # indigo
    if v > 900 and v<1500:
        return [0, 150, 220]    # sky blue
    else:
        return [0, 220, 220]    # teal

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


n = 3

center = np.array([400.0, 400.0])

#creating velocity array - 
v = []
for i in range(n):
    theta = (2*3.14159*i)/n
    v.append([5000.0*math.cos(theta),-360.0*math.sin(theta)])
vel = np.array(v)

#creating array for initial position 
p = []
for i in range(n):
    p.append([400.0,400.0])
pos = np.array(p)

acc = np.array([0.0, 5000.0])
radius = 12.5
boundary_radius = 250


exe = True
while exe:
    dt = (clock.tick(60) / 10000)

    #exit condition - 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exe = False

    
    for i in range(n):
        
        # SIMPLE KINEMATICS FOR FALLING
        vel[i] += acc * dt
        pos[i] += vel[i] * dt
        
    #COLLISIONS -- 
        r_vector = pos[i] - center 
        dist = np.linalg.norm(r_vector)
        r_unit = r_vector / dist
        # WITH BOUNDARY
        if dist > (boundary_radius - radius): #radius is just the offset so balls doesnt clip through 
            
            vel[i] = vel[i] - 2 * np.dot(vel[i], r_unit) * r_unit
            #repositioning ball back onto the boundary's edge after it's detected ball went past it
            pos[i] = center + r_unit * (boundary_radius - radius) 

    # COLLISION b/w BALLS
    for i in range(n):
        for j in range(i + 1, n):
            ctc_dist = np.linalg.norm(pos[j] - pos[i]) # -- centre to centre distance vector

            if ctc_dist <= 2 * radius:
                ctc_unit = (pos[j] - pos[i]) / ctc_dist # -- centre to centre unit vector
                vrc = np.dot((vel[j] - vel[i]), ctc_unit) #relative velocity along the normal line i.e. along ctc unit vector

                if vrc < 0:  # collision only happens if vrc<0\
                    
                    # decompose into normal + tangential parts

                    ke_before = np.dot(vel[i], vel[i]) + np.dot(vel[j], vel[j])

                    u1n = np.dot(vel[i], ctc_unit) * ctc_unit
                    u1t = vel[i] - u1n

                    u2n = np.dot(vel[j], ctc_unit) * ctc_unit
                    u2t = vel[j] - u2n

                    # elastic, equal mass -> normal components swap, tangential unchanged
                    vel[i] = u1t + u2n
                    vel[j] = u2t + u1n

                    ke_after = np.dot(vel[i], vel[i]) + np.dot(vel[j], vel[j])
                    print(f"delta: {(ke_before-ke_after):.2f}")

                    # push balls apart by the overlap amt so they don't stay overlapping
                    overlap = 2 * radius - ctc_dist
                    #pos[i] = pos[i] - ctc_unit * (overlap / 2)
                    #pos[j] = pos[j] + ctc_unit * (overlap / 2)
    
    screen.fill((0, 0, 0))
    
    pygame.draw.circle(screen, (255, 255, 255), center.astype(int), boundary_radius, 3)
    for i in range(n):
        speed = np.linalg.norm(vel[i])
        color = SPEED_COLOR(speed)
        pygame.draw.circle(screen, color, pos[i].astype(int), radius)
    pygame.display.flip()

pygame.quit()