import pygame
import random
import sys
import numpy as np
import pandas as pd

"""
The simulation requires a few command line arguments.
1. width: the width of the simulation field
2. height: the height of the simulation field
3. num_healthy: the number of people initially healthy
4. num_sick: the number of people initially sick
5. transmission_distance: the distance that possible transmissions can happen
6. transmission_prob: the probability that the disease transmits
7. recovery_time: the time to recover from the disease
8. fatality_prob: the probability of fataility due to the disease
"""

# simulation parameters
WIDTH, HEIGHT = int(sys.argv[1]), int(sys.argv[2])
DOT_RADIUS = 5
NUM_HEALTHY = int(sys.argv[3])
NUM_SICK = int(sys.argv[4])
TRANS_DIST = float(sys.argv[5])
TRANS_PROB = float(sys.argv[6])
RECOVERY_TIME = int(sys.argv[7])
FATALITY_PROB = float(sys.argv[8])

BACKGROUND_COLOR = (30, 30, 30)
HEALTHY_COLOR = (255, 255, 255)
SICK_COLOR = (255, 0, 0)
RECOVERED_COLOR = (0, 0, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

healthy_dots = []
sick_dots = []
recovered_dots = []
dead_dots = []

# Generate random positions and velocities for dots
for _ in range(NUM_HEALTHY):
    x = random.randint(DOT_RADIUS, WIDTH - DOT_RADIUS)
    y = random.randint(DOT_RADIUS, HEIGHT - DOT_RADIUS)
    # Velocity can be positive or negative
    vx = random.choice([-2, -1, 1, 2])
    vy = random.choice([-2, -1, 1, 2])

    # Each dot will be stored as a dict
    healthy_dots.append({
        'x': x,
        'y': y,
        'vx': vx,
        'vy': vy
    })

for _ in range(NUM_SICK):
    x = random.randint(DOT_RADIUS, WIDTH - DOT_RADIUS)
    y = random.randint(DOT_RADIUS, HEIGHT - DOT_RADIUS)
    # Velocity can be positive or negative
    vx = random.choice([-2, -1, 1, 2])
    vy = random.choice([-2, -1, 1, 2])

    # Each dot will be stored as a dict
    sick_dots.append({
        'x': x,
        'y': y,
        'vx': vx,
        'vy': vy,
        'recovery': RECOVERY_TIME
    })


def move_dots(dots: list) -> None:
    for dot in dots:
        dot['x'] += dot['vx']
        dot['y'] += dot['vy']

        # if on edge, then reverse direction to get out of edge
        if dot['x'] - DOT_RADIUS < 0 or dot['x'] + DOT_RADIUS > WIDTH:
            dot['vx'] = -dot['vx']
        if dot['y'] - DOT_RADIUS < 0 or dot['y'] + DOT_RADIUS > HEIGHT:
            dot['vy'] = -dot['vy']


def draw_dots(dots: list, color) -> None:
    for dot in dots:
        pygame.draw.circle(screen, color, (dot['x'], dot['y']), DOT_RADIUS)


def distance(d1, d2) -> float:
    return np.sqrt((d1['y'] - d2['y'])**2 + (d1['x'] - d2['x'])**2)


# if in distance + a random chance of catching the virus, then
# become sick.
def transmit(d1, d2) -> bool:
    in_proximity = distance(d1, d2) < TRANS_DIST
    caught = random.random() < TRANS_PROB

    return in_proximity and caught


# Main loop
running = True
tick = 0

while running:
    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # first thing to do is to check disease transmission
    # we'll deal with newly "recovered" first - so if on this tick
    # the sick person recovers, they can't transmit

    this_tick_sick = []
    this_tick_healthy = healthy_dots
    for sick in sick_dots:
        sick['recovery'] -= 1
        if sick['recovery'] <= 0:
            recovered_dots.append({
                'x': sick['x'],
                'y': sick['y'],
                'vx': sick['vx'],
                'vy': sick['vy']
            })
            continue
        elif random.random() < FATALITY_PROB:
            dead_dots.append(sick)
        else:
            this_tick_sick.append(sick)

        for healthy in healthy_dots:
            if transmit(sick, healthy):
                this_tick_sick.append({
                    'x': healthy['x'],
                    'y': healthy['y'],
                    'vx': healthy['vx'],
                    'vy': healthy['vy'],
                    'recovery': RECOVERY_TIME
                })
                this_tick_healthy.remove(healthy)

    sick_dots = this_tick_sick
    healthy_dots = this_tick_healthy

    # Now move dots
    move_dots(healthy_dots)
    move_dots(recovered_dots)
    move_dots(sick_dots)

    # Clear the screen
    screen.fill(BACKGROUND_COLOR)

    # Draw dots
    draw_dots(healthy_dots, HEALTHY_COLOR)
    draw_dots(sick_dots, SICK_COLOR)
    draw_dots(recovered_dots, RECOVERED_COLOR)

    # Update the display
    pygame.display.flip()

    # Limit frames per second
    clock.tick(60)

    if len(sick_dots) == 0:
        running = False

    tick += 1

pygame.quit()
sys.exit()
