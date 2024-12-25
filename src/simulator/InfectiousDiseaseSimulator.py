import pandas as pd
import numpy as np
import random


class InfectiousDiseaseSimulator:
    def __init__(
        self, w: int, h: int, healthy: int,
        sick: int, trans_dist: int, trans_prob: float,
        fatality_prob: float, recovery_time: int
    ):
        """
        Arguments:
            visualise - whether to visualise each simulation or not.
            w - width of the simulation area
            h - height of the simulation area
            healthy - the amount of healthy people at the start of sim
            sick - the amount of sick people at the start of sim
            trans_dist - the distance in which people get sick
            trans_prob - the probability that the sickness gets transmitted
                while in the range of a sick persion
            fatality_prob - the probability that a sick person dies (per tick)
            recovery_time - the amount of ticks for the person to recover
        """

        self.data = []
        self.DOT_RADIUS = 5
        self.RECOVERY_TIME = recovery_time
        self.FATALITY = fatality_prob
        self.TRANS_DIST = trans_dist
        self.TRANS_PROB = trans_prob
        self.WIDTH = w
        self.HEIGHT = h
        self.NUM_HEALTHY = healthy
        self.NUM_SICK = sick
        self.t = 0

    def __random_dot(self, sick=False):
        x = random.randint(self.DOT_RADIUS, self.WIDTH - self.DOT_RADIUS)
        y = random.randint(self.DOT_RADIUS, self.HEIGHT - self.DOT_RADIUS)

        dx = random.choice([-1, 1])
        dy = random.choice([-1, 1])

        return_dict = {
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy
        }

        if sick:
            return_dict['recovery'] = self.RECOVERY_TIME

        return return_dict

    def setup(self):
        self.healthy = []
        self.sick = []
        self.recovered = []
        self.dead = []

        for _ in range(self.NUM_HEALTHY):
            self.healthy.append(self.__random_dot())

        for _ in range(self.NUM_SICK):
            self.sick.append(self.__random_dot(True))

    def tick(self) -> bool:
        def move_dots(dots: list) -> None:
            for dot in dots:
                dot['x'] += dot['dx']
                dot['y'] += dot['dy']

                # if on edge, then reverse direction to get out of edge
                if (dot['x'] - self.DOT_RADIUS < 0 or
                        dot['x'] + self.DOT_RADIUS > self.WIDTH):
                    dot['dx'] = -dot['dx']
                if (dot['y'] - self.DOT_RADIUS < 0
                        or dot['y'] + self.DOT_RADIUS > self.HEIGHT):
                    dot['dy'] = -dot['dy']

        self.t += 1

        curr_sick = []
        curr_healthy = self.healthy

        for sick in self.sick:
            sick['recovery'] -= 1
            if sick['recovery'] <= 0:
                self.recovered.append({
                    'x': sick['x'], 'y': sick['y'],
                    'dx': sick['dx'], 'dy': sick['dy']
                })
                continue
            elif random.random() < self.FATALITY:
                self.dead.append(sick)
            else:
                curr_sick.append(sick)

            for healthy in self.healthy:
                if self.__transmit(sick, healthy):
                    curr_sick.append({
                        'x': healthy['x'], 'y': healthy['y'],
                        'dx': healthy['dx'], 'dy': healthy['dy'],
                        'recovery': self.RECOVERY_TIME
                    })
                    curr_healthy.remove(healthy)

        self.sick = curr_sick
        self.healthy = curr_healthy

        move_dots(self.sick)
        move_dots(self.healthy)

        self.data.append({
            'tick': self.t,
            'num_sick': len(self.sick),
            'num_healthy': len(self.healthy),
            'num_recovered': len(self.recovered)
        })

        return len(self.sick) == 0

    def simulate(self):
        while True:
            response = self.tick()
            if response:
                break

    def write_data(self, path: str):
        pd.DataFrame(self.data).to_csv(path)

    def __distance(self, A, B) -> float:
        """
        Retrieve the Euclidean distance between dot a and b.
        """
        return np.sqrt((A['y'] - B['y'])**2 + (A['x'] - B['x'])**2)

    def __transmit(self, A, B) -> float:
        proximity = self.__distance(A, B) < self.TRANS_DIST
        caught = random.random() < self.TRANS_PROB

        return proximity and caught
