from enum import Enum
import numpy

class State(Enum):
    IDLE_CLOSED = 0
    IDLE_OPEN = 1
    UP = 2
    DOWN = 3
    UP_SLOW = 4
    DOWN_SLOW = 5


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
        seed = 1
        rider_per_hour = 600
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
        self.enter_exit_elevators()

    def enter_exit_elevators(self):
        for idx, elevator in enumerate(self.elevators):
            # check if door is open
            if not elevator.state == State.IDLE_OPEN:
                continue
            floor = int(elevator.floor)

            # exit if it is your floor
            for rider in self.riders_in_elevator[idx].copy():
                if floor == rider.dest:
                    self.riders_in_elevator[idx].remove(rider)
                    self.riders_served.append(rider)
                    print(f"{rider} arrived at destination")

            # enter if elevator is not full
            if len(self.riders_in_elevator[idx]) < elevator.capacity:
                for rider in self.queues[floor].copy():
                    rider.enter(elevator)
                    self.queues[floor].remove(rider)
                    self.riders_in_elevator[idx].append(rider)

class Controller:

    def __init__(self, elevators):
        self.num_elevators = len(elevators)
        self.elevators = elevators
        self.requests = []

    def request(self, dest: int):
        raise NotImplementedError("request must be implemented in subclass")

    def assign_elevator(self):
        raise NotImplementedError("assign_elevator must be implemented in subclass")

    def update(self):
        raise NotImplementedError("update must be implemented in subclass")

    def call_elevator(self):
        raise NotImplementedError("update must be implemented in subclass")


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
        if self.requests:
            self.process_next_request()

    def request(self, elevator: int, dest: int):
        print(f"Received request to {dest} in elevator {elevator}")
        # self.requests.append(dest)
        elevator.goto(dest)

    def call_elevator(self, floor):
        print(f"Received request to {floor}")
        self.requests.append(floor)

    def process_next_request(self):
        request = self.requests.pop(0)
        fulfilled = False

        # look for idle elevator in the destination floor
        for elevator in self.elevators:
            if elevator.state == State.IDLE_CLOSED and int(elevator.floor) == request:
                fulfilled = True
                break

        # if no idle elevator is in origin floor, assign any idle elevator to go to the origin floor
        if not fulfilled:
            for elevator in self.elevators:
                if elevator.state == State.IDLE_CLOSED and elevator.goal is None:
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

    riders_total = 0

    def __init__(self, num_floors, rng, spawn_time, controller):
        ''' rng is random generator
        1. randomizing origin floor: 50% from floor 0 and up, the other 50% distributed between all floors
        2. randomizing destination floor: if origin NOT 0, most probable to go to 0
        '''

        # unique ID for each rider
        self.id = self.riders_total
        Rider.riders_total += 1

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
        self.controller.call_elevator(self.origin)

    def enter(self, elevator):
        print(f"Entering elevator {elevator}")
        self.controller.request(elevator, self.dest)

    def __str__(self):
        return f"Rider from floor {self.origin} to {self.dest}, spawned at {self.spawn_time}"


class Elevator:
    time_to_floor = 2  # seconds
    time_to_floor_slow = 20  # seconds

    def __init__(self, elevator_id, initial_floor=0.0, capacity=4):
        self.id = elevator_id
        self.floor = initial_floor
        self.capacity = capacity
        self._at_floor = True
        self.state = State.IDLE_OPEN
        self._direction = Direction.UP
        self.goal = None

    def __str__(self):
        return f"Elevator {self.id} is at {self.floor} and is in {self.state}"

    def goto(self, floor):
        self.goal = floor

    def update(self, delta_time):
        # print(f"elevator {self.id} is in state {self._state.value}")

        if self.state == State.IDLE_OPEN:
            if not self.goal is None:
                self.state = State.IDLE_CLOSED  # TODO add timeout
                return

        if self.state == State.IDLE_CLOSED:
            if self.goal is None:
                return
            if int(self.floor) == self.goal:
                self.state = State.IDLE_OPEN
                print(f"elevator {self.id} is in state {self.state.value}")
                self.goal = None
                print(f"Elevator {self.id} arrived at floor {self.floor}")
            elif self.goal > self.floor:
                self.state = State.UP
                self._direction = Direction.UP
                self.slow_if_near()
            elif self.goal < self.floor:
                self.state = State.DOWN
                print(f"elevator {self.id} changed state to down")
                self._direction = Direction.DOWN
                self.slow_if_near()
            return  # not check if at floor before elevator moves

        # if on the move
        if self.state == State.UP:
            self.floor += delta_time / self.time_to_floor
        elif self.state == State.DOWN:
            self.floor -= delta_time / self.time_to_floor
        elif self.state == State.UP_SLOW:
            self.floor += delta_time / self.time_to_floor_slow
        elif self.state == State.DOWN_SLOW:
            self.floor -= delta_time / self.time_to_floor_slow

        self._at_floor = self._detect_at_floor(delta_time)
        if self._at_floor:
            self.action_at_floor()

    def action_at_floor(self):
        # just arrived to goal floor
        if round(self.floor) == self.goal:
            self.state = State.IDLE_CLOSED
            self.floor = round(self.floor, 0)
            print(f"elevator {self.id} changed state to IDLE_CLOSED at goal floor")
        else:
            self.slow_if_near()

    def _detect_at_floor(self, delta_time):
        if self.state == State.UP_SLOW or self.state == State.DOWN_SLOW:
            step_size = delta_time / self.time_to_floor_slow
        else:
            step_size = delta_time / self.time_to_floor

        if abs(self.floor - round(self.floor)) < step_size:
            return True
        else:
            return False

    def slow_if_near(self):  # slow down near goal floor
        if self.state == State.UP and self.goal - round(self.floor) == 1:
            self.state = State.UP_SLOW
        elif self.state == State.DOWN and round(self.floor) - self.goal == 1:
            self.state = State.DOWN_SLOW


if __name__ == "__main__":
    model = ElevatorModel(5, 2)
    print(model.get_state())
    for _ in range(200):
        model.update(1)
