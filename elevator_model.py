from enum import Enum
import numpy

class State(Enum):
    IDLE = 0
    UP = 1
    DOWN = 2
    UP_SLOW = 3
    DOWN_SLOW = 4


class Direction(Enum):
    UP = 1
    DOWN = 2


class ElevatorModel:
    def __init__(self, num_floors, num_elevators):
        self.num_floors = num_floors  # 0 + number of floors above ground
        self.num_elevators = num_elevators
        self.time = 0

        self.elevators = []
        for elevator in range(self.num_elevators):
            self.elevators.append(Elevator(elevator))

        self.controller = Fifo(self.elevators)  # Testing(self.elevators)
        self.queues = [[] for _ in range(self.num_floors)]
        self.riders_in_elevator = [[] for _ in range(self.num_elevators)]
        self.riders_served = []

        # random generator
        seed = 120
        rider_per_hour = 60
        average_time_between_riders_sec = 3600 / rider_per_hour
        self.rng = numpy.random.default_rng(seed)
        self.lam = average_time_between_riders_sec
        self.next_rider_spawn_time = self.rng.poisson(self.lam)

    def __str__(self):
        return f"Building with {self.num_floors} floors and {self.num_elevators} elevators"

    def spawn_rider(self):
        if self.time >= self.next_rider_spawn_time:
            # spawn a new rider
            new_rider = Rider(self.num_floors, self.rng, self.time, self.controller)
            self.queues[new_rider.origin].append(new_rider)
            # print(f"new rider added to {new_rider.origin} floor")

            # get time for next rider spawn
            delta_time = self.rng.poisson(self.lam)
            self.next_rider_spawn_time = self.time + delta_time

    def get_state(self):
        return {
            "elevators_position": [elevator.floor for elevator in self.elevators],
            "queues": self.queues,
            "riders_in_elevator": self.riders_in_elevator
        }

    def update(self, delta_time):
        # TODO controller should only set goal to elevator, elevator start to move later by its own decision
        self.time += delta_time
        self.controller.update()
        for elevator in self.elevators:
            elevator.update(delta_time)
        self.spawn_rider()
        self.enter_exit_elevator()

    def enter_exit_elevator(self):
        for elevator, floor in enumerate(self.controller.doors_open):
            # check if at floor
            if floor is None:
                continue
            # exit if it is your floor
            for rider in self.riders_in_elevator[elevator].copy():
                if floor == rider.dest:
                    self.riders_in_elevator[elevator].remove(rider)
                    self.riders_served.append(rider)
                    print(f"rider {rider} arrived at destination")

            # enter if elevator is not full
            if len(self.riders_in_elevator[elevator]) < self.controller.elevators[elevator].capacity:
                for rider in self.queues[floor].copy():
                    rider.enter(elevator)
                    self.queues[floor].remove(rider)
                    self.riders_in_elevator[elevator].append(rider)

class Controller:

    def __init__(self, elevators):
        self.num_elevators = len(elevators)
        self.elevators = elevators
        self.requests = []
        self.doors_open = [None] * self.num_elevators

    def request(self, dest: int):
        raise NotImplementedError("request must be implemented in subclass")

    def assign_elevator(self):
        raise NotImplementedError("assign_elevator must be implemented in subclass")

    def update(self):
        raise NotImplementedError("update must be implemented in subclass")

    def call_elevator(self):
        raise NotImplementedError("update must be implemented in subclass")

    def open_doors(self):
        for idx, elevator in enumerate(self.elevators):
            if elevator.state == State.IDLE:
                self.doors_open[idx] = int(elevator.floor)
            else:
                self.doors_open[idx] = None


class Testing(Controller):

    def __init__(self, elevators):
        super().__init__(elevators)
        self.time = 0

    def assign_elevator(self):
        self.time += 1
        if self.time == 3:
            self.elevators[0].goto(2)
        elif self.time == 5:
            self.elevators[1].goto(1)

    def update(self):
        self.assign_elevator()

    def request(self, origin: int, dest: int):
        print(f"time {self.time}: received request from {origin} to go to {dest}")

    def elevator_floor_update(self):
        pass


class Fifo(Controller):
    def assign_elevator(self):
        pass

    def update(self):
        self.open_doors()
        if self.requests:
            self.process_next_request()

    def request(self, elevator: int, dest: int):
        print(f"Received request to {dest} in elevator {elevator}")
        # self.requests.append(dest)
        self.elevators[elevator].goto(dest)

    def call_elevator(self, floor):
        print(f"Received request to {floor}")
        self.requests.append(floor)

    def process_next_request(self):
        request = self.requests.pop(0)
        fulfilled = False

        # look for idle elevator in the destination floor
        for elevator in self.elevators:
            if elevator.state == State.IDLE and int(elevator.floor) == request:
                fulfilled = True
                break

        # if no idle elevator is in origin floor, assign any idle elevator to go to the origin floor
        if not fulfilled:
            for elevator in self.elevators:
                if elevator.state == State.IDLE:
                    fulfilled = True
                    elevator.goto(request)
                    break

        # if not served, return the request
        if not fulfilled:
            self.requests.insert(0, request)

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

class Rider:

    def __init__(self, num_floors, rng, spawn_time, controller):
        ''' rng is random generator
        1. randomizing origin floor: 50% from floor 0 and up, the other 50% distributed between all floors
        2. randomizing destination floor: if origin NOT 0, most probable to go to 0
        '''

        # generating probabilities
        origin_floor_prob = [0.5] + (num_floors - 1) * [0.5 / (num_floors - 1)]
        # if origin NOT 0, probability to select 0 or others ** must zero origin floor **
        prob_dest_is_0 = 0.8

        # randomizing origin and destination floors
        origin_floor = rng.choice(range(num_floors), p=origin_floor_prob)
        if origin_floor == 0:
            dest_floor = int(rng.choice(range(1, num_floors)))
        else:
            dest_prob = [prob_dest_is_0] + (num_floors - 1) * [(1 - prob_dest_is_0) / (num_floors - 2)]
            dest_prob[origin_floor] = 0
            dest_floor = rng.choice(range(num_floors), p=dest_prob)

        self.origin = int(origin_floor)
        self.dest = int(dest_floor)
        self.spawn_time = spawn_time
        self.controller = controller
        print(f"time {self.spawn_time}: new rider spawned at {self.origin} to go to {self.dest}")
        self.controller.call_elevator(self.origin)

    def enter(self, elevator):
        print(f"Entering elevator {elevator}")
        self.controller.request(elevator, self.dest)

    def __str__(self):
        return f"Rider from floor {self.origin} to {self.dest}, spawned at {self.spawn_time}"


class Elevator:
    time_to_floor = 2  # seconds
    time_to_floor_slow = 4  # seconds

    def __init__(self, elevator_id, initial_floor=0.0, capacity=4):
        self.id = elevator_id
        self.floor = initial_floor
        self.capacity = capacity
        self.at_floor = True
        self.state = State.IDLE
        self.direction = Direction.UP
        self.goal = None

    def __str__(self):
        return f"Elevator {self.id} is at {self.floor} and is in {self.state}"

    def goto(self, floor):
        if self.state == State.IDLE:
            self.goal = floor
            if self.goal > self.floor:
                self.state = State.UP
                self.direction = Direction.UP
            elif self.goal < self.floor:
                self.state = State.DOWN
                self.direction = Direction.DOWN
            else:
                return -2
            return 0
        else:
            return -1

    def update(self, delta_time):
        self.process_passing_floors()

        if self.state == State.UP:
            self.floor += delta_time / self.time_to_floor
        elif self.state == State.DOWN:
            self.floor -= delta_time / self.time_to_floor
        elif self.state == State.UP_SLOW:
            self.floor += delta_time / self.time_to_floor_slow
        elif self.state == State.DOWN_SLOW:
            self.floor -= delta_time / self.time_to_floor_slow
        self.floor = round(self.floor, 2)  # make sure the float sums up well
        # print(f"Elevator {self.id} is at floor {self.floor}")

    def process_passing_floors(self):
        # TODO modify detection logic for passing teh floor in float number
        # detect if at floor
        if (self.floor).is_integer() and self.goal is not None:  # if at a floor and not just waiting for directions
            self.at_floor = True
        else:
            self.at_floor = False

        # check when passing floor
        if self.at_floor:
            # slow down near goal floor
            if self.state == State.UP and self.goal - int(self.floor) == 1:
                self.state = State.UP_SLOW
            elif self.state == State.DOWN and int(self.floor) - self.goal == 1:
                self.state = State.DOWN_SLOW
            # stop at goal floor
            elif self.goal == int(self.floor):
                self.state = State.IDLE
                self.goal = None
                print(f"Elevator {self.id} arrived at floor {self.floor}")


if __name__ == "__main__":
    model = ElevatorModel(5, 2)
    print(model.get_state())
    for _ in range(200):
        model.update(1)
