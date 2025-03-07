import pygame
# import math
from enum import Enum


class State(Enum):
    IDLE = 0
    UP = 1
    DOWN = 2
    UP_SLOW = 3
    DOWN_SLOW = 4


pygame.init()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (120, 120, 120)

WIDTH, HEIGHT = 562, 800
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elevator System Sim")
BG_IMG = pygame.transform.scale(pygame.image.load("apartment-building.jpg"), (WIDTH, HEIGHT))
BUTTON_FONT = pygame.font.SysFont('Consolas', 10)
FPS = 20

NUM_FLOORS = 5  # 0 + number of floors
FLOOR_0 = 612
PX_FLOORS_DIF = 100
BUTTON_FLOORS_POS = 323
BUTTON_PANEL_X = 70
BUTTON_CTRL_X = 70


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


class Elevator:
    VEL = 0.05
    VEL_SLOW = 0.025
    elev_w = 63
    elev_h = 65

    def __init__(self):
        self.floor = 0.0
        self.state = State.IDLE
        self.goal = 0
        self.requests = [False] * NUM_FLOORS

        self.buttons_panel = []
        for floor in range(NUM_FLOORS):
            self.buttons_panel.append(Button(GRAY, BUTTON_PANEL_X, 400 - 30 * floor, str(floor)))

        self.ctrl_panel = [Button(GRAY, BUTTON_CTRL_X, 140 - 120, 'U'),
                           Button(GRAY, BUTTON_CTRL_X, 140 - 90, 'u'),
                           Button(GRAY, BUTTON_CTRL_X, 140 - 60, '-'),
                           Button(GRAY, BUTTON_CTRL_X, 140 - 30, 'd'),
                           Button(GRAY, BUTTON_CTRL_X, 140, 'D')]

    def __str__(self):
        return f"Elevator is at {self.floor} and is in {self.state}"

    def all_ctrl_gray(self):
        for button in self.ctrl_panel:
            button.color = GRAY

    def request(self, requested_floor):
        self.requests[requested_floor] = True

        if self.state == State.IDLE and requested_floor != int(self.floor):
            self.goal = requested_floor
            self.ctrl_panel[2].color = GRAY
            if self.goal > self.floor:
                self.state = State.UP
                self.ctrl_panel[0].color = RED
            elif self.goal < self.floor:
                self.state = State.DOWN
                self.ctrl_panel[4].color = RED
        elif self.state == State.UP:
            if requested_floor > self.floor:
                self.goal = requested_floor
        elif self.state == State.DOWN:
            if requested_floor < self.floor:
                self.goal = requested_floor

    def goto(self, floor):
        if self.state == State.IDLE:
            self.goal = floor
            if self.goal > self.floor:
                self.state = State.UP
                self.all_ctrl_gray()
                self.ctrl_panel[0].color = RED
            elif self.goal < self.floor:
                self.state = State.DOWN
                self.all_ctrl_gray()
                self.ctrl_panel[4].color = RED
            return 0
        else:
            return -1

    def update_movement(self):
        if self.state == State.UP:
            self.floor += self.VEL
        elif self.state == State.DOWN:
            self.floor -= self.VEL
        elif self.state == State.UP_SLOW:
            self.floor += self.VEL_SLOW
        elif self.state == State.DOWN_SLOW:
            self.floor -= self.VEL_SLOW

    def update_controller(self):
        # slow down near goal floor
        if self.state == State.UP:
            if self.goal - self.floor <= 1:
                self.ctrl_panel[0].color = GRAY
                self.ctrl_panel[1].color = RED
                self.state = State.UP_SLOW
        elif self.state == State.DOWN:
            if self.floor - self.goal <= 1:
                self.ctrl_panel[4].color = GRAY
                self.ctrl_panel[3].color = RED
                self.state = State.DOWN_SLOW
        # resume after stop
        elif self.state == State.IDLE:
            if not any(self.requests):
                # no more requests
                self.all_ctrl_gray()
                self.ctrl_panel[2].color = RED
            elif self.ctrl_panel[1].color == RED:
                # last movement was up
                self.ctrl_panel[1].color = GRAY
                next_request = self.next_request(up_direction=True)
                if next_request is not None:
                    # up requests remain
                    self.goal = next_request
                    self.state = State.UP
                    self.ctrl_panel[0].color = RED
                    self.ctrl_panel[2].color = GRAY
                else:
                    # switching from up to down
                    next_request = self.next_request(up_direction=False)
                    if next_request is not None:
                        self.goal = next_request
                        self.state = State.DOWN
                        self.ctrl_panel[4].color = RED
                        self.ctrl_panel[2].color = GRAY
            elif self.ctrl_panel[3].color == RED:
                # last movement was down
                self.all_ctrl_gray()
                next_request = self.next_request(up_direction=False)
                if next_request is not None:
                    # up requests remain
                    self.goal = next_request
                    self.state = State.DOWN
                    self.ctrl_panel[4].color = RED
                    self.ctrl_panel[2].color = GRAY
                else:
                    # switching from down to up
                    next_request = self.next_request(up_direction=True)
                    if next_request is not None:
                        self.goal = next_request
                        self.state = State.UP
                        self.ctrl_panel[0].color = RED
                        self.ctrl_panel[2].color = GRAY

        # stop at goal floor
        if abs(self.floor % 1) < self.VEL_SLOW:
            # at floor
            if int(self.floor) == self.goal:
                # at goal floor
                self.state = State.IDLE
                self.requests[int(self.floor)] = False
                self.ctrl_panel[2].color = RED

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

    def draw_inside_panel(self):
        pygame.draw.rect(win, BLACK, (BUTTON_PANEL_X - 7, 400 - 127, 34, 152))
        pygame.draw.rect(win, GRAY, (BUTTON_PANEL_X - 5, 400 - 125, 30, 150))
        for idx, button in enumerate(self.buttons_panel):
            # if not self.state == State.IDLE and idx == self.goal:
            if self.requests[idx]:
                button.color = RED
            else:
                button.color = GRAY
            button.draw(BLACK)

    def draw_control_panel(self):
        pygame.draw.rect(win, BLACK, (BUTTON_CTRL_X - 7, 140 - 127, 34, 152))
        pygame.draw.rect(win, GRAY, (BUTTON_CTRL_X - 5, 140 - 125, 30, 150))
        for button in self.ctrl_panel:
            button.draw(BLACK)

    def draw(self):
        floor_px = (NUM_FLOORS + 1 - self.floor) * PX_FLOORS_DIF + 35
        pygame.draw.rect(win, BLACK, (435, floor_px, self.elev_w, self.elev_h))
        pygame.draw.rect(win, BLUE, (437, floor_px + 2, self.elev_w - 4, self.elev_h - 4))

        self.draw_inside_panel()
        self.draw_control_panel()


def main():
    clock = pygame.time.Clock()

    elev = Elevator()
    buttons_floors = []
    for floor in range(NUM_FLOORS):
        buttons_floors.append(Button(GRAY, BUTTON_FLOORS_POS, FLOOR_0 - PX_FLOORS_DIF * floor + 20, str(floor)))

    sign = Button(BLACK, BUTTON_FLOORS_POS + 47, FLOOR_0 - 23, '0', GREEN)

    time_sec = 0
    running = True

    while running:

        clock.tick(FPS)
        time_sec += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:  # print(pygame.mouse.get_pos())
                mouse_pos = pygame.mouse.get_pos()
                for idx, button in enumerate(buttons_floors):
                    if button.is_over(mouse_pos):
                        elev.request(idx)
                for idx, button in enumerate(elev.buttons_panel):
                    if button.is_over(mouse_pos):
                        elev.request(idx)

        win.blit(BG_IMG, (0, 0))
        elev.update_movement()
        elev.update_controller()
        elev.draw()

        for button in buttons_floors:
            if elev.state == State.IDLE:
                button.color = GRAY
            else:
                button.color = RED
            button.draw(BLACK)

        sign.text = str(round(elev.floor))
        sign.draw(BLACK)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
