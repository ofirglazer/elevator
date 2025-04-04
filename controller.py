import pygame
from elevator_model import ElevatorModel
from visualizer import ElevatorRenderer


def main(num_floors, num_elevators):
    pygame.init()

    model = ElevatorModel(num_floors, num_elevators)
    renderer = ElevatorRenderer(model)

    clock = pygame.time.Clock()
    FPS = 20  # frames per second
    ACCELERATION_FACTOR = 40
    running = True

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        model.update(ACCELERATION_FACTOR / FPS)
        model_state = model.get_state()
        renderer.render(model_state)

        clock.tick(FPS)


if __name__ == '__main__':
    num_floors = 4
    num_elevators = 2
    main(num_floors, num_elevators)
