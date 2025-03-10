import pygame
from enum import Enum
import numpy as np
# import math


class State(Enum):
    IDLE = 0
    UP = 1
    DOWN = 2
    UP_SLOW = 3
    DOWN_SLOW = 4


class Direction(Enum):
    UP = 1
    DOWN = 2


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


WIDTH, HEIGHT = 800, 800

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multiple Elevator System Sim")
SIGN_FONT = pygame.font.SysFont('comicsansms', 30)
QUEUE_FONT = pygame.font.SysFont('comicsansms', 20)
# BUTTON_FONT = pygame.font.SysFont('Consolas', 10)
FPS = 20

NUM_FLOORS = 7  # 0 + number of floors above ground
NUM_ELEVATORS = 3
FLOOR0_Y = HEIGHT - 50
FLOORS_DIFF_Y = 100
ELEVATORS_DIFF_X = 200
BUILDING_X0 = 50

# BUTTON_FLOORS_POS = 323
# BUTTON_PANEL_X = 70
# BUTTON_CTRL_X = 70

'''
class Button:
    button_w = 20
    button_h = 20

    def __init__(self, color, x, y, text='', text_color=(0, 0, 0)):
        self.color = color
        self.ogcol = color
        self.x = x
        self.y = y
        self.text = text
        self.text_color = text_color

    def draw(self, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.button_w + 4, self.button_h + 4), 0)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.button_w, self.button_h), 0)

        if self.text != '':
            text = BUTTON_FONT.render(self.text, 1, self.text_color)
            win.blit(text, (self.x + (self.button_w / 2 - text.get_width() / 2),
                            self.y + (self.button_h / 2 - text.get_height() / 2)))

    def is_over(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if (self.x <= pos[0] <= self.x + self.button_w) and (self.y <= pos[1] <= self.y + self.button_h):
            # self.color = (128, 128, 128)
            return True
        else:
            self.color = self.ogcol
            return False
'''


class Building:

    def __init__(self):
        self.x = BUILDING_X0
        self.height = FLOORS_DIFF_Y * NUM_FLOORS
        self.y = FLOOR0_Y - self.height
        self.width = ELEVATORS_DIFF_X * (NUM_ELEVATORS + 1)

        self.floors_y = []
        for floor in range(NUM_FLOORS):
            self.floors_y.append(self.y + self.height - floor * FLOORS_DIFF_Y)

        self.elevators = []
        for elevator in range(NUM_ELEVATORS):
            self.elevators.append(Elevator(elevator, self.x + (elevator + 1) * ELEVATORS_DIFF_X, 0, self.floors_y))

        self.controller = Fifo(self.elevators)
        head_queue_x = self.x + ELEVATORS_DIFF_X - Elevator.ELEVATOR_W // 2
        self.riders = Riders(self.controller, self.floors_y, head_queue_x)

    def update(self):
        for elevator in self.elevators:
            elevator.update_movement()
        self.controller.update()
        self.riders.update()

    def draw(self):
        pygame.draw.rect(win, Color.GRAY.value, (self.x, self.y, self.width, self.height))

        for floor in range(NUM_FLOORS):
            pygame.draw.line(win, Color.BLACK.value, (self.x, self.floors_y[floor]),
                             (self.x + self.width, self.floors_y[floor]), 2)

            floor_sign = SIGN_FONT.render(f"Floor {str(floor)}", 1, Color.BLACK.value)
            win.blit(floor_sign, (self.x + 5, self.floors_y[floor] - FLOORS_DIFF_Y * 5 // 6))

            queue_sign = QUEUE_FONT.render(f"{len(self.riders.queues[floor])} in queue", 1, Color.BLACK.value)
            win.blit(queue_sign, (self.x + 5, self.floors_y[floor] - 50))

        for elevator in range(NUM_ELEVATORS):
            elevator_x = self.x + (elevator + 1) * ELEVATORS_DIFF_X
            pygame.draw.line(win, Color.BLUE.value, (elevator_x, self.y), (elevator_x, self.floors_y[0]))
            elevator_sign = SIGN_FONT.render(f"Elevator {str(elevator)}", 1, Color.BLUE.value)
            win.blit(elevator_sign, (elevator_x - 55, self.y - 40))

        for elevator in self.elevators:
            elevator.draw()

        self.riders.draw([elevator.y for elevator in self.elevators])


class Controller:

    def __init__(self, elevators):
        self.elevators = elevators
        self.requests = []
        self.doors_open = [None] * NUM_ELEVATORS

    def request(self, dest: int):
        raise NotImplementedError("request must be implemented in subclass")

    def assign_elevator(self):
        raise NotImplementedError("assign_elevator must be implemented in subclass")

    def update(self):
        raise NotImplementedError("update must be implemented in subclass")

    def open_doors(self):
        for idx, elevator in enumerate(self.elevators):
            if elevator.state == State.IDLE:
                self.doors_open[idx] = elevator.floor
            else:
                self.doors_open[idx] = None

    def elevator_floor_update(self):
        raise NotImplementedError("elevator_floor_update must be implemented in subclass")


class Testing(Controller):
    def assign_elevator(self):
        self.elevators[0].goto(4)
        self.elevators[1].goto(1)

    def update(self):
        self.elevator_floor_update()

    def request(self, origin: int, dest: int):
        print(f"Received request from {origin} to go to {dest}")

    def elevator_floor_update(self):
        pass

    '''
    '''


class Fifo(Controller):
    def assign_elevator(self):
        pass

    def update(self):
        self.open_doors()
        if self.requests:
            self.process_request()

    def elevator_floor_update(self):
        pass

    def request(self, dest: int):
        print(f"Received request to {dest}")
        self.requests.append(dest)

    def process_request(self):
        request = self.requests.pop(0)
        fulfilled = False
        # look for idle elevator in the destination floor
        for elevator in self.elevators:
            if elevator.state == State.IDLE and elevator.floor == request:
                fulfilled = True
                break

        # if no idle elevator is in origin floor, assign any idle elevator to go to the origin floor
        if fulfilled == False:
            for elevator in self.elevators:
                if elevator.state == State.IDLE:
                    fulfilled = True
                    elevator.goto(request)
                    break

        # if not served, return the request
        if fulfilled == False:
            self.requests.insert(0, request)

        '''
        if self.state == State.IDLE and requested_floor != int(self.floor):
            self.goal = requested_floor
            self.ctrl_panel[2].color = Color.GRAY
            if self.goal > self.floor:
                self.state = State.UP
                self.ctrl_panel[0].color = Color.RED
            elif self.goal < self.floor:
                self.state = State.DOWN
                self.ctrl_panel[4].color = Color.RED
        elif self.state == State.UP:
            if requested_floor > self.floor:
                self.goal = requested_floor
        elif self.state == State.DOWN:
            if requested_floor < self.floor:
                self.goal = requested_floor
        '''


class Rider:
    rider_size = 20

    def __init__(self, rng, spawn_time, controller):
        # rng is random generator

        # 50% from floor 0 and up, the other 50% distributed between all floors
        origin_floor_prob = [0.5] + (NUM_FLOORS - 1) * [0.5 / (NUM_FLOORS - 1)]
        # if origin NOT 0, probability to select 0 or others ** must zero origin floor when using
        prob_dest_is_0 = 0.8

        origin_floor = rng.choice(range(NUM_FLOORS), p=origin_floor_prob)
        if origin_floor == 0:
            dest_floor = rng.choice(range(1, NUM_FLOORS))
        else:
            dest_prob = [prob_dest_is_0] + (NUM_FLOORS - 1) * [(1 - prob_dest_is_0) / (NUM_FLOORS - 2)]
            dest_prob[origin_floor] = 0
            dest_floor = rng.choice(range(NUM_FLOORS), p=dest_prob)

        self.origin = int(origin_floor)
        self.dest = int(dest_floor)
        self.spawn_time = spawn_time
        self.controller = controller

        colors = list(Color)
        colors.remove(Color.GRAY)
        colors.remove(Color.BLUE)
        self.color = rng.choice(colors)
        self.call_elevator()

    def draw(self, x, y):
        pygame.draw.circle(win, self.color.value, (x, y), self.rider_size // 2)

    def call_elevator(self):
        self.controller.request(self.origin)

    def enter(self, elevator):
        print(f"Entering elevator {elevator}")

    def __str__(self):
        return f"Rider from floor {self.origin} to {self.dest}, spawned at {self.spawn_time}  color {self.color.name}"


class Riders:
    def __init__(self, controller, floors_y, head_queue_x):
        self.controller = controller
        self.floors_y = floors_y
        self.head_queue_x = head_queue_x - Rider.rider_size // 2
        self.riders = []
        self.queues = [[] for _ in range(NUM_FLOORS)]
        self.riding = [[] for _ in range(NUM_ELEVATORS)]
        self.time = 0
        self.next_spawn_time = 0

        seed = 120
        self.rng = np.random.default_rng(seed)
        rider_per_hour = 60
        average_time_between_riders_sec = 3600 / rider_per_hour
        self.lam = average_time_between_riders_sec

    def spawn(self):
        if self.time >= self.next_spawn_time:
            self.add_rider()
            delta_time = self.rng.poisson(self.lam)
            self.next_spawn_time = self.time + delta_time

    def add_rider(self):
        new_rider = Rider(self.rng, self.time, self.controller)
        self.riders.append(new_rider)
        self.queues[new_rider.origin].append(new_rider)

    def update(self):
        self.time += 1
        self.spawn()
        self.enter_elevators()

    def enter_elevators(self):
        for elevator, floor in enumerate(self.controller.doors_open):
            if floor is not None:
                for rider in self.queues[floor].copy():
                    rider.enter(elevator)
                    self.queues[floor].remove(rider)
                    self.riding[elevator].append(rider)


    def draw(self, elevators_y):
        for queue in self.queues:
            for idx, rider in enumerate(queue):
                rider.draw(self.head_queue_x - int((idx + 0.5) * rider.rider_size),
                           self.floors_y[rider.origin] - rider.rider_size // 2)

        for elevator_idx, riders in enumerate(self.riding):
            for rider_idx, rider in enumerate(riders):
                rider.draw(50 + ELEVATORS_DIFF_X * (elevator_idx + 1) + rider_idx * rider.rider_size,
                           elevators_y[elevator_idx] + rider.rider_size)



class Elevator:
    VEL = 5
    VEL_SLOW = 2
    ELEVATOR_W = 80
    ELEVATOR_H = 60

    def __init__(self, elevator_id, x, floor, floors_y):
        self.id = elevator_id
        self.floor = floor
        self.floors_y = [y - self.ELEVATOR_H for y in floors_y]
        self.x = x - self.ELEVATOR_W // 2
        self.y = self.floors_y[self.floor]
        self.at_floor = True
        self.state = State.IDLE
        self.direction = Direction.UP
        self.goal = 0

        '''
        self.ctrl_panel = [Button(Color.GRAY, BUTTON_CTRL_X, 140 - 120, 'U'),
                           Button(Color.GRAY, BUTTON_CTRL_X, 140 - 90, 'u'),
                           Button(Color.GRAY, BUTTON_CTRL_X, 140 - 60, '-'),
                           Button(Color.GRAY, BUTTON_CTRL_X, 140 - 30, 'd'),
                           Button(Color.GRAY, BUTTON_CTRL_X, 140, 'D')]
        '''

    def __str__(self):
        return f"Elevator {self.id} is at {self.floor} and is in {self.state}"

    '''
    def all_ctrl_gray(self):
        for button in self.ctrl_panel:
            button.color = Color.GRAY 
    '''

    def goto(self, floor):
        if self.state == State.IDLE:
            self.goal = floor
            if self.goal > self.floor:
                self.state = State.UP
                self.direction = Direction.UP
                # self.all_ctrl_gray()
                # self.ctrl_panel[0].color = Color.RED
            elif self.goal < self.floor:
                self.state = State.DOWN
                self.direction = Direction.DOWN
                # self.all_ctrl_gray()
                # self.ctrl_panel[4].color = Color.RED
            else:
                return -2
            return 0
        else:
            return -1

    def update_movement(self):
        self.passing_floors()

        if self.state == State.UP:
            self.y -= self.VEL
        elif self.state == State.DOWN:
            self.y += self.VEL
        elif self.state == State.UP_SLOW:
            self.y -= self.VEL_SLOW
        elif self.state == State.DOWN_SLOW:
            self.y += self.VEL_SLOW

    def passing_floors(self):

        # detect floors
        if self.y in self.floors_y:
            self.at_floor = True
            self.floor = self.floors_y.index(self.y)
        else:
            self.at_floor = False

        # check when passing floor
        if self.at_floor:
            # slow down near goal floor
            if self.state == State.UP and self.goal - self.floor == 1:
                self.state = State.UP_SLOW
            elif self.state == State.DOWN and self.floor - self.goal == 1:
                self.state = State.DOWN_SLOW
            # stop at goal
            elif self.goal == self.floor:
                self.state = State.IDLE

            # if self.goal - self.floor <= 1:
                # self.ctrl_panel[0].color = Color.GRAY
                # self.ctrl_panel[1].color = Color.RED
        '''        
        elif self.state == State.DOWN:
            if self.floor - self.goal <= 1:
                self.ctrl_panel[4].color = Color.GRAY
                self.ctrl_panel[3].color = Color.RED
                self.state = State.DOWN_SLOW
        # resume after stop
        elif self.state == State.IDLE:
            if not any(self.requests):
                # no more requests
                self.all_ctrl_gray()
                self.ctrl_panel[2].color = Color.RED
            elif self.ctrl_panel[1].color == Color.RED:
                # last movement was up
                self.ctrl_panel[1].color = Color.GRAY
                next_request = self.next_request(up_direction=True)
                if next_request is not None:
                    # up requests remain
                    self.goal = next_request
                    self.state = State.UP
                    self.ctrl_panel[0].color = Color.RED
                    self.ctrl_panel[2].color = Color.GRAY
                else:
                    # switching from up to down
                    next_request = self.next_request(up_direction=False)
                    if next_request is not None:
                        self.goal = next_request
                        self.state = State.DOWN
                        self.ctrl_panel[4].color = Color.RED
                        self.ctrl_panel[2].color = Color.GRAY
            elif self.ctrl_panel[3].color == Color.RED:
                # last movement was down
                self.all_ctrl_gray()
                next_request = self.next_request(up_direction=False)
                if next_request is not None:
                    # up requests remain
                    self.goal = next_request
                    self.state = State.DOWN
                    self.ctrl_panel[4].color = Color.RED
                    self.ctrl_panel[2].color = Color.GRAY
                else:
                    # switching from down to up
                    next_request = self.next_request(up_direction=True)
                    if next_request is not None:
                        self.goal = next_request
                        self.state = State.UP
                        self.ctrl_panel[0].color = Color.RED
                        self.ctrl_panel[2].color = Color.GRAY

        # stop at goal floor
        if abs(self.floor % 1) < self.VEL_SLOW:
            # at floor
            if int(self.floor) == self.goal:
                # at goal floor
                self.state = State.IDLE
                self.requests[int(self.floor)] = False
                self.ctrl_panel[2].color = Color.RED
        '''

    '''
    def next_request(self, up_direction):
        # next request UP
        if up_direction:
            for floor in range(int(self.floor), NUM_FLOORS):
                if self.requests[floor]:
                    return floor
        # next request DOWN
        else:
            for floor in range(int(self.floor), -1, -1):
                if self.requests[floor]:
                    return floor
        return None
    '''

    '''
    def draw_inside_panel(self):
        pygame.draw.rect(win, Color.BLACK, (BUTTON_PANEL_X - 7, 400 - 127, 34, 152))
        pygame.draw.rect(win, Color.GRAY, (BUTTON_PANEL_X - 5, 400 - 125, 30, 150))
        for idx, button in enumerate(self.buttons_panel):
            # if not self.state == State.IDLE and idx == self.goal:
            if self.requests[idx]:
                button.color = Color.RED
            else:
                button.color = Color.GRAY
            button.draw(Color.BLACK)

    def draw_control_panel(self):
        pygame.draw.rect(win, Color.BLACK, (BUTTON_CTRL_X - 7, 140 - 127, 34, 152))
        pygame.draw.rect(win, Color.GRAY, (BUTTON_CTRL_X - 5, 140 - 125, 30, 150))
        for button in self.ctrl_panel:
            button.draw(Color.BLACK)
    '''

    def draw(self):
        pygame.draw.rect(win, Color.BLUE.value, (self.x, self.y, self.ELEVATOR_W, self.ELEVATOR_H))

        # self.draw_inside_panel()
        # self.draw_control_panel()


def main():
    clock = pygame.time.Clock()
    building = Building()

    # test code to generate some movement
    building.controller.assign_elevator()
    building.update()

    # sign = Button(Color.BLACK, BUTTON_FLOORS_POS + 47, FLOOR0_Y - 23, '0', Color.GREEN)

    time_sec = 0
    running = True

    while running:

        clock.tick(FPS)
        time_sec += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        '''
            if event.type == pygame.MOUSEBUTTONDOWN:  # print(pygame.mouse.get_pos())
                mouse_pos = pygame.mouse.get_pos()
                for idx, button in enumerate(buttons_floors):
                    if button.is_over(mouse_pos):
                        elev.request(idx)
                for idx, button in enumerate(elev.buttons_panel):
                    if button.is_over(mouse_pos):
                        elev.request(idx)
        '''
        building.update()

        win.fill(Color.WHITE.value)
        building.draw()

        # elev.update_movement()
        # elev.update_controller()
        # elev.draw()
        '''
        for button in buttons_floors:
            if elev.state == State.IDLE:
                button.color = Color.GRAY
            else:
                button.color = Color.RED
            button.draw(Color.BLACK)

        sign.text = str(round(elev.floor))
        sign.draw(Color.BLACK)'''
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
