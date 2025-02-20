#import pygame
# import math
from enum import Enum


class State(Enum):
	IDLE = 0
	UP = 1
	DOWN = 2
	UP_SLOW = 3
	DOWN_SLOW = 4

#pygame.init()
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
    def _init_(self):
        self.floor =  0
        self.state = State.IDLE
        self.goal = 0
        
    def _str_(self):
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
        	
     def 

'''    def draw(self):
        pygame.draw.circle(win, WHITE, (WIDTH // 2, HEIGHT // 2), 30)'''


def main():
	
	elev = Elevator()
	print(elev)
	time_sec = 0
	running = True
	
	while time_sec <= 10:
	     time_sec += 1
	     print(f"time: {time_sec}, elevator state is {elev.state}")
      
      
if _name_ == "_main_":
    main()
