# import pygame
# import math
from enum import Enum


class State(Enum):
	IDLE = 0
	UP = 1
	DOWN = 2
	UP_SLOW = 3
	DOWN_SLOW = 4


# pygame.init()
'''
WIDTH, HEIGHT = 400, 800
WHITE = (255, 255, 255)
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elevator System Sim")

# BG_IMG = pygame.image.load("stars-galaxy.jpg")
FPS = 10'''
FLOORS = 4  # 0 + number of floors


class Controller:
	pass


class Elevator:
	vel = 0.2
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
		self.floor = round(self.floor, 1)

		if self.floor == self.goal:
			self.state = State.IDLE


'''    def draw(self):
		pygame.draw.circle(win, WHITE, (WIDTH // 2, HEIGHT // 2), 30)'''


def main():

	elev = Elevator()
	print(elev)
	time_sec = 0
	# running = True

	while time_sec <= 50:
		time_sec += 1
		if time_sec == 10:
			elev.goto(3)
		elif time_sec == 30:
			elev.goto(1)

		elev.update()
		print(f"time: {time_sec}, elevator is at {elev.floor} and is {elev.state}")


if __name__ == "__main__":
	main()
