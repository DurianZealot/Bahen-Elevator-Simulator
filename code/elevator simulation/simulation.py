"""CSC148 Assignment 1 - Simulation

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This contains the main Simulation class that is actually responsible for
creating and running the simulation. You'll also find the function `sample_run`
here at the bottom of the file, which you can use as a starting point to run
your simulation on a small configuration.

Note that we have provided a fairly comprehensive list of attributes for
Simulation already. You may add your own *private* attributes, but should not
remove any of the existing attributes.
"""
# You may import more things from these modules (e.g., additional types from
# typing), but you may not import from any other modules.

from typing import Dict, List, Any
import algorithms
import pygame
from entities import Person, Elevator
from visualizer import Visualizer


class Simulation:
    """The main simulation class.

    === Attributes ===
    arrival_generator: the algorithm used to generate new arrivals.
    elevators: a list of the elevators in the simulation
    moving_algorithm: the algorithm used to decide how to move elevators
    num_floors: the number of floors
    visualizer: the Pygame visualizer used to visualize this simulation
    waiting: a dictionary of people waiting for an elevator
             (keys are floor numbers, values are the list of waiting people)
    num_iteration: the number of simulation rounds that took place
    total_people: the number of people that arrived at some point during the
                  simulation (all people generated by the generator methods)
    people_completed: the number of people who reached their target destination
                      by the end of the simulation
    max_time: the maximum time someone spent before reaching their target floor
    during the simulation (note that this includes time spent waiting on a floor
    and travelling on an elevator)
    avg_time: the average time someone spent before reaching their target floor,
              rounded down to the nearest integer

    arrival_generator: algorithms.ArrivalGenerator
    elevators: List[Elevator]
    moving_algorithm: algorithms.MovingAlgorithm
    num_floors: int
    visualizer: Visualizer
    waiting: Dict[int, List[Person]]
    num_iterations: int
    total_people: int
    people_completed: int
    max_time: int
    all_wait_time: List[int]
    """

    def __init__(self,
                 config: Dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration."""

        # Initialize the visualizer.
        # Note that this should be called *after* the other attributes
        # have been initialized.
        self.num_iterations = 0
        self.total_people = 0
        self.people_completed = 0
        self.max_time = -1
        self.all_wait_time = []

        self.arrival_generator = config['arrival_generator']
        self.elevators = []
        self.moving_algorithm = config['moving_algorithm']
        self.num_floors = config['num_floors']
        self.waiting = dict().fromkeys([floor for floor in
                                        range(1, config['num_floors'] + 1)])

        for key in self.waiting.keys():
            self.waiting[key] = []

        for _ in range(config['num_elevators']):
            self.elevators.append(Elevator(config['elevator_capacity'],
                                           config['num_floors']))

        self.visualizer = Visualizer(self.elevators,  # should be self.elevators
                                     self.num_floors,
                                     # should be self.num_floors
                                     config['visualize'])

    ############################################################################
    # Handle rounds of simulation.
    ############################################################################

    # --- HELPER FUNCTIONS --- #

    def _get_num_iteratons(self, num_rounds: int) -> None:

        """ set the self.iterations the number of rounds.
        """
        self.num_iterations = num_rounds

    def _update_list_of_passengers_wait_time(self,
                                             passengers: List[Person]) -> None:
        """ Update a list of passengers' wait time
        """
        for passenger in passengers:
            passenger.increase_wait_time()

    def _update_wait_time_of_passengers_waiting(self) -> None:

        """ Update the wait time of passengers waiting OUTSIDE of elevators.
        """
        for floor in self.waiting.keys():
            if len(self.waiting[floor]) != 0:
                self._update_list_of_passengers_wait_time(self.waiting[floor])

    def _update_wait_time_of_passengers_in_elevator(self) -> None:

        """ Update the wait time of passengers INSIDE elevators.
        """
        for elevator in self.elevators:
            if len(elevator.passengers) != 0:
                self._update_list_of_passengers_wait_time(elevator.passengers)

    def run(self, num_rounds: int) -> Dict[str, Any]:

        """Run the simulation for the given number of rounds.

        Return a set of statistics for this simulation run, as specified in the
        assignment handout.

        Precondition: num_rounds >= 1.

        Note: each run of the simulation starts from the same initial state
        (no people, all elevators are empty and start at floor 1).
        """

        # Stage 0: update the num_iterations
        self._get_num_iteratons(num_rounds)

        for i in range(num_rounds):
            self.visualizer.render_header(i)

            # Stage 1-1: update the wait time of passengers waiting OUTSIDE
            self._update_wait_time_of_passengers_waiting()

            # Stage 1-2: update the wait time of passengers IN ELEVATOR
            self._update_wait_time_of_passengers_in_elevator()

            # Stage 2: generate new arrivals
            self._generate_arrivals(i)

            # Stage 3: leave elevators
            self._handle_leaving()

            # Stage 4: board elevators
            self._handle_boarding()

            # Stage 5: move the elevators using the moving algorithm
            self._move_elevators()

            self.visualizer.render()

            # Pause for 1 second
            self.visualizer.wait(1)

        return self._calculate_stats()

    def _generate_arrivals(self, round_num: int) -> None:

        """Generate and visualize new arrivals."""
        round_num_new_arrivals = self.arrival_generator.generate(round_num)

        # update self.waiting attribute with new arrivals
        # update self.total_people
        for floor in round_num_new_arrivals.keys():
            for person in round_num_new_arrivals[floor]:
                self.waiting[floor].append(person)
                self.total_people += 1

        self.visualizer.show_arrivals(round_num_new_arrivals)

        """
        # print the arrival information
        print(f'The round is {round_num}')
        for floor, people in round_num_new_arrivals.items():
            if len(people) > 0:
                print(f'The floor {floor} has people waiting:')
            else:
                print(f'The floor {floor} has no people waiting for elevator.')

            for passenger in people:
                print(f"The passenger's start floor is {passenger.start}, "
                      f"and target floor is {passenger.target}")
        """

    def _handle_leaving(self) -> None:

        """Handle people leaving elevators."""

        # iterate through all elevators
        for elevator in self.elevators:
            arrived_passengers = []
            # iterate through all passengers in the elevator
            for passenger in elevator.passengers:
                if passenger.target == elevator.track_floor():
                    arrived_passengers.append(passenger)
                    self._update_arrival_passengers(passenger)
            for passenger in arrived_passengers:
                elevator.passengers.remove(passenger)
                self.visualizer.show_disembarking(passenger, elevator)

        # assertion
        for elevator in self.elevators:
            for passenger in elevator.passengers:
                assert passenger.target != elevator.track_floor()

    def _handle_boarding(self) -> None:

        """Handle boarding of people and visualize."""

        # the argument into the self.visualizer.show_boarding(person, elevator)

        # iterate through all the elevators
        for elevator in self.elevators:
            if elevator.fullness() != 1.0:
                boarding_passengers = []
                for waiting_passenger in self.waiting[elevator.track_floor()]:
                    if elevator.fullness() < 1.0:
                        boarding_passengers.append(waiting_passenger)
                        elevator.load(waiting_passenger)
                        self.visualizer.show_boarding(waiting_passenger,
                                                      elevator)
                    else:  # after loading some passengers, the elevator is full
                        break  # stop the iteration on the waiting list
                for passenger in boarding_passengers:
                    self.waiting[elevator.track_floor()].remove(passenger)

                    assert passenger not in self.waiting[elevator.track_floor()]

        # assertion
        for elevator in self.elevators:
            assert (elevator.fullness() == 1.0 or
                    len(self.waiting[elevator.track_floor()]) == 0)

    def _move_elevators(self) -> None:

        """Move the elevators in this simulation.

        Use this simulation's moving algorithm to move the elevators.
        """
        directions = self.moving_algorithm.move_elevators(self.elevators,
                                                          self.waiting,
                                                          self.num_floors)

        for elevator, direction in zip(self.elevators, directions):
            elevator.move_floor(direction)

        self.visualizer.show_elevator_moves(self.elevators, directions)

    ############################################################################
    # Statistics calculations
    ############################################################################

    def _calculate_stats(self) -> Dict[str, int]:

        """Report the statistics for the current run of this simulation.

        max_time: the maximum time someone spent before reaching their target
        floor during the simulation (note that this includes time spent waiting
        on a floor and travelling on an elevator)

        min_time: the minimum time someone spent before reaching their target
        floor

        avg_time: the average time someone spent before reaching their target
        floor, rounded down to the nearest integer

        """
        return {
            'num_iterations': self.num_iterations,
            'total_people': self.total_people,
            'people_completed': self.people_completed,
            'max_time': self._return_max_wait_time(),
            'min_time': self._return_min_time(),
            'avg_time': self._return_average_wait_time()
        }

    def _update_arrival_passengers(self, passenger: Person) -> None:

        # Add new arrival passenger's wait time to self.all_wait_time
        self.all_wait_time.append(passenger.wait_time)
        # Update the number of arrival passengers
        self.people_completed += 1

        # Update the maximum wait_time of passenger if neccessary
        if passenger.wait_time > self.max_time:
            self.max_time = passenger.wait_time

    def _return_min_time(self) -> int:

        """ Return the minimum of wait_time of all arrival passengers.
        """
        return min(self.all_wait_time) if len(self.all_wait_time) != 0 else -1

    def _return_average_wait_time(self) -> int:

        """ Return the average wait time of all arrival passengers.
        Rounded the average_wait_time down to the nearest integer
        DO int(average_wait_time) !
        int(8.99999) = 8
        But NOT round(average_wait_time) !
        round(8.9999) = 9
        """
        return int(sum(self.all_wait_time) / len(self.all_wait_time)) if \
            len(self.all_wait_time) != 0 else -1

    def _return_max_wait_time(self) -> int:

        """ Return the maximum wait time of all arrival passengers.
        """
        return self.max_time


def sample_run() -> Dict[str, int]:
    """Run a sample simulation, and return the simulation statistics."""
    config = {
        'num_floors': 6,
        'num_elevators': 6,
        'elevator_capacity': 3,
        'num_people_per_round': 2,
        # Random arrival generator with 6 max floors and 2 arrivals per round.
        'arrival_generator': algorithms.RandomArrivals(6, 2),
        'moving_algorithm': algorithms.RandomAlgorithm(),
        'visualize': True
    }

    sim = Simulation(config)
    stats = sim.run(15)
    return stats


if __name__ == '__main__':
    # Uncomment this line to run our sample simulation (and print the
    # statistics generated by the simulation).
    print(sample_run())

    # import python_ta
    """
    python_ta.check_all(config={
        'extra-imports': ['entities', 'visualizer', 'algorithms', 'time'],
        'max-nested-blocks': 4,
        'max-attributes': 12,
        'disable': ['R0201']
    })
    """