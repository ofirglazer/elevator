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

FLOORS = 4  # 0 + number of floors
FLOOR_0 = 612
FLOOR_1 = 512
FLOOR_2 = 412
FLOOR_3 = 312
FLOOR_4 = 212
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
    vel = 0.05
    elev_w = 63
    elev_h = 65

    def __init__(self):
        self.floor = 0
        self.state = State.IDLE
        self.goal = 0

        self.buttons_panel = [Button(GRAY, BUTTON_PANEL_X, 400, '0'),
                              Button(GRAY, BUTTON_PANEL_X, 400 - 30, '1'),
                              Button(GRAY, BUTTON_PANEL_X, 400 - 60, '2'),
                              Button(GRAY, BUTTON_PANEL_X, 400 - 90, '3'),
                              Button(GRAY, BUTTON_PANEL_X, 400 - 120, '4')]
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

    def update(self):
        if self.state == State.UP:
            self.floor += self.vel
        elif self.state == State.DOWN:
            self.floor -= self.vel
        self.floor = round(self.floor, 2)

        if self.floor == self.goal:
            self.state = State.IDLE
            self.all_ctrl_gray()
            self.ctrl_panel[2].color = RED

    def draw_inside_panel(self):
        pygame.draw.rect(win, BLACK, (BUTTON_PANEL_X - 7, 400 - 127, 34, 152))
        pygame.draw.rect(win, GRAY, (BUTTON_PANEL_X - 5, 400 - 125, 30, 150))
        for idx, button in enumerate(self.buttons_panel):
            if not self.state == State.IDLE and idx == self.goal:
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
        floor_px = (FLOORS + 1 - self.floor) * 102 + 110
        pygame.draw.rect(win, BLACK, (435, floor_px, self.elev_w, self.elev_h))
        pygame.draw.rect(win, BLUE, (437, floor_px + 2, self.elev_w - 4, self.elev_h - 4))

        self.draw_inside_panel()
        self.draw_control_panel()


def main():
    clock = pygame.time.Clock()

    elev = Elevator()
    buttons_floors = [Button(GRAY, BUTTON_FLOORS_POS, FLOOR_0 + 20, '0'),
                      Button(GRAY, BUTTON_FLOORS_POS, FLOOR_1 + 20, '1'),
                      Button(GRAY, BUTTON_FLOORS_POS, FLOOR_2 + 20, '2'),
                      Button(GRAY, BUTTON_FLOORS_POS, FLOOR_3 + 20, '3'),
                      Button(GRAY, BUTTON_FLOORS_POS, FLOOR_4 + 20, '4')]

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
                        elev.goto(idx)
                for idx, button in enumerate(elev.buttons_panel):
                    if button.is_over(mouse_pos):
                        elev.goto(idx)

        win.blit(BG_IMG, (0, 0))
        elev.update()
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
