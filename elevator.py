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
BUTTON_POS = 323


class Button():
	button_w = 20
	button_h = 20
	def __init__(self, color, x, y, text=''):
		self.color = color
		self.ogcol = color
		self.x = x
		self.y = y
		self.text = text

	def draw(self, outline=None):
		# Call this method to draw the button on the screen
		if outline:
			pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.button_w + 4, self.button_h + 4), 0)

		pygame.draw.rect(win, self.color, (self.x, self.y, self.button_w, self.button_h), 0)

		if self.text != '':
			text = BUTTON_FONT.render(self.text, 1, (0, 0, 0))
			win.blit(text, (
			self.x + (self.button_w / 2 - text.get_width() / 2), self.y + (self.button_h / 2 - text.get_height() / 2)))

	def is_over(self, pos):
		# Pos is the mouse position or a tuple of (x,y) coordinates
		if (self.x <= pos[0] <=  self.x + self.button_w) and (self.y <= pos[1] <=  self.y + self.button_h):
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

	def __str__(self):
		return f"Elevator is at {self.floor} and is in {self.state}"

	def goto(self, floor):
		if self.state == State.IDLE:
			self.goal = floor
			if self.goal > self.floor:
				self.state = State.UP
			elif self.goal < self.floor:
				self.state = State.DOWN
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

	def draw(self):
		floor_px = (FLOORS + 1 - self.floor) * 102 + 110
		pygame.draw.rect(win, BLACK, (435, floor_px, self.elev_w, self.elev_h))
		pygame.draw.rect(win, BLUE, (437, floor_px + 2, self.elev_w - 4, self.elev_h - 4))


def main():
	clock = pygame.time.Clock()

	elev = Elevator()
	buttons = [Button(GREEN, BUTTON_POS, FLOOR_0 + 20, '0'), Button(GREEN, BUTTON_POS, FLOOR_1 + 20, '1'),
			   Button(GREEN, BUTTON_POS, FLOOR_2 + 20, '2'), Button(GREEN, BUTTON_POS, FLOOR_3 + 20, '3'),
			   Button(GREEN, BUTTON_POS, FLOOR_4 + 20, '4')]
	sign = Button(WHITE, BUTTON_POS + 47, FLOOR_0 - 23, '0')
	print(elev)
	time_sec = 0
	running = True

	while running:

		clock.tick(FPS)
		time_sec += 1

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			if event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = pygame.mouse.get_pos()
				for idx, button in enumerate(buttons):
					if button.is_over(mouse_pos):
						elev.goto(idx)
				#print(pygame.mouse.get_pos())



		'''	# simulated calls
		if time_sec == 10:
			elev.goto(3)
		elif time_sec == 70:
			elev.goto(1)'''

		elev.update()

		win.blit(BG_IMG, (0, 0))
		elev.draw()
		for button in buttons:
			if elev.state == State.IDLE:
				button.color = GREEN
			else:
				button.color = RED
			button.draw(BLACK)
		sign.text = str(round(elev.floor))
		sign.draw(BLACK)
		pygame.display.flip()

	pygame.quit()


if __name__ == "__main__":
	main()
