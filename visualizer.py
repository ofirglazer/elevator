import pygame
pygame.font.get_fonts()
from enum import Enum

class Color(Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    LIME = (0, 255, 0)
    GRAY = (180, 180, 180)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    SILVER = (192, 192, 192)
    MAROON = (128, 0, 0)
    OLIVE = (128, 128, 0)
    GREEN = (0, 128, 0)
    PURPLE = (128, 0, 128)
    TEAL = (0, 128, 128)
    NAVY = (0, 0, 128)

class ElevatorRenderer:

    def __init__(self, model):
        # taken from the model
        self.num_floors = model.num_floors  # 0 + number of floors above ground
        self.num_elevators = model.num_elevators

        # graphics constants
        self.width = 600
        self.height = 600
        self.margin = 10
        self.floor_height = (self.height - 2 * self.margin) // self.num_floors
        self.elevator_height = int(self.floor_height * 0.75)
        self.elevator_spacing = (self.width - 2 * self.margin) // (self.num_elevators + 1)
        self.elevator_width = int(self.elevator_spacing * 0.5)
        self.sign_height_in_floor = 0.75  # of the floor

        self.chute_x = []
        for elevator_id in range(self.num_elevators):
            self.chute_x.append(self.margin + self.elevator_spacing * (elevator_id + 1))

        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Multiple Elevator System Sim")
        self.sign_font = pygame.font.SysFont('comicsansms', 30)
        #self.queue_font = pygame.font.SysFont('comicsansms', 20)

    def draw_building(self, model_state):
        # building outline
        self.window.fill(Color.BLACK.value)
        pygame.draw.rect(self.window, Color.GRAY.value, (self.margin, self.margin, self.width, self.height))

        # floor lines
        for floor in range(self.num_floors):
            pygame.draw.line(self.window, Color.BLACK.value,
                             (self.margin, (self.height - self.margin - self.floor_height * floor)),
                             (self.margin + self.width, (self.height - self.margin - self.floor_height * floor)), 2)

            floor_sign = self.sign_font.render(f"Floor {str(floor)}", 1, Color.BLACK.value)
            floor_sign_y = self.height - self.margin - int(self.floor_height * (floor + self.sign_height_in_floor))
            self.window.blit(floor_sign,
                             (self.margin, floor_sign_y))
            '''
            queue_sign = QUEUE_FONT.render(f"{len(self.riders.queues[floor])} in queue", 1, Color.BLACK.value)
            self.window.blit(queue_sign, (self.x + SIGN_SPACE_FROM_LEFT,
                                  self.floors_y[floor] - int(FLOORS_DIFF_Y * QUEUE_SIGN_DISTANCE_FROM_FLOOR))) '''
        # elevators chutes
        for elevator_id in range(self.num_elevators):
            # elevator_y = self.height - self.margin - self.floor_height * floor - self.elevator_height
            pygame.draw.line(self.window, Color.BLUE.value,
                             (self.chute_x[elevator_id], self.height - self.margin),
                             (self.chute_x[elevator_id], self.margin), 2)
            # elevator_sign = SIGN_FONT.render(f"Elevator {str(elevator)}", 1, Color.BLUE.value)
            # self.window.blit(elevator_sign, (elevator_x - 55, self.y - 40))

        '''
        self.riders.draw([elevator.y for elevator in self.elevators])'''

    def draw_elevators(self, model_state):
        for elevator in range(self.num_elevators):
            elevator_y = (self.height - self.margin
                          - self.floor_height * model_state["elevators_position"][elevator] - self.elevator_height)
            pygame.draw.rect(self.window, Color.BLUE.value, (self.chute_x[elevator], elevator_y,
                                                             self.elevator_width, self.elevator_height))
            #queue_length = len(model_state["riders_in_elevator"][elevator])
            #queue_sign = self.sign_font.render(f"{queue_length} in queue", 1, Color.BLACK.value)
            #self.window.blit(queue_sign, (0, 0))

    def draw_queues(self, model_state):
        for floor in range(self.num_floors):
            for rider in model_state["queues"][floor]:
                print("rider")

    def render(self, model_state):
        self.draw_building(model_state)
        self.draw_elevators(model_state)
        self.draw_queues(model_state)



        pygame.display.flip()


if __name__ == '__main__':
    pass