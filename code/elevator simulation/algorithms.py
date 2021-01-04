"""CSC148 Assignment 1 - Algorithms

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains two sets of algorithms: ones for generating new arrivals to
the simulation, and ones for making decisions about how elevators should move.

As with other files, you may not change any of the public behaviour (attributes,
methods) given in the starter code, but you can definitely add new attributes
and methods to complete your work here.

See the 'Arrival generation algorithms' and 'Elevator moving algorithsm'
sections of the assignment handout for a complete description of each algorithm
you are expected to implement in this file.
"""
import csv
from enum import Enum
from random import sample, choice
from typing import Dict, List, Optional
from entities import Person, Elevator


###############################################################################
# Arrival generation algorithms
###############################################################################
class ArrivalGenerator:
    """An algorithm for specifying arrivals at each round of the simulation.

    === Attributes ===
    max_floor: The maximum floor number for the building.
               Generated people should not have a starting or target floor
               beyond this floor.
    num_people: The number of people to generate, or None if this is left
                up to the algorithm itself.

    === Representation Invariants ===
    max_floor >= 2
    num_people is None or num_people >= 0
    """
    max_floor: int
    num_people: Optional[int]

    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        """Initialize a new ArrivalGenerator.

        Preconditions:
            max_floor >= 2
            num_people is None or num_people >= 0
        """
        self.max_floor = max_floor
        self.num_people = num_people

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        You can choose whether to include floors where no people arrived.
        """
        raise NotImplementedError


class RandomArrivals(ArrivalGenerator):
    """Generate a fixed number of random people each round.

    Generate 0 people if self.num_people is None.

    For our testing purposes, this class *must* have the same initializer header
    as ArrivalGenerator. So if you choose to to override the initializer, make
    sure to keep the header the same!

    Hint: look up the 'sample' function from random.
    """
    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """" Randomly gernerate a list of persons each round
        dict:
        key: floor
        values: list of new arrivals
        """
        arrivals = dict().fromkeys([i for i in range(1, self.max_floor + 1)])

        for key in arrivals.keys():
            arrivals[key] = []

        if self.num_people:

            for n in range(self.num_people):
                start, target = sample(range(1, self.max_floor + 1), 2)
                assert start != target
                arrivals[start].append(Person(start, target))

        return arrivals


class FileArrivals(ArrivalGenerator):
    """Generate arrivals from a CSV file.
    === Attributes ===
    max_floor: The maximum floor number for the building.
               Generated people should not have a starting or target floor
               beyond this floor.
    num_people: The number of people to generate, or None if this is left
                up to the algorithm itself.
    _arrivals_from_file: All arrives at all rounds

    === Presentation Invariants ===
    max_floor >= 2
    num_people >= 0

    """
    max_floor: int
    filename: str
    _arrival_from_file: List

    def __init__(self, max_floor: int, filename: str) -> None:
        """Initialize a new FileArrivals algorithm from the given file.

        The num_people attribute of every FileArrivals instance is set to None,
        since the number of arrivals depends on the given file.

        Precondition:
            <filename> refers to a valid CSV file, following the specified
            format and restrictions from the assignment handout.
        """

        ArrivalGenerator.__init__(self, max_floor, None)
        self._arrivals_from_file = []

        # We've provided some of the "reading from csv files" boilerplate code
        # for you to help you get started.

        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                self._arrivals_from_file.append([int(i) for i in line])

        # sort the arrival list according to round order
        self._arrivals_from_file.sort()

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """ Return the a round of new arrivals.
        """
        arrivals = dict().fromkeys(i for i in range(1, self.max_floor + 1))

        # to initialize the new arrivals dictionary, each floor has a list of
        # new arrivals
        for key in arrivals.keys():
            arrivals[key] = []

        # to add the new arrivals of round_num into the new arrivals dictionary
        for round in self._arrivals_from_file:
            if round[0] == round_num:
                index = 1
                while index+1 < len(round):
                    start, target = round[index], round[index + 1]
                    arrivals[start].append(Person(start, target))
                    index += 2

        return arrivals


###############################################################################
# Elevator moving algorithms
###############################################################################

class Direction(Enum):
    """
    The following defines the possible directions an elevator can move.
    This is output by the simulation's algorithms.

    The possible values you'll use in your Python code are:
        Direction.UP, Direction.DOWN, Direction.STAY
    """
    UP = 1
    STAY = 0
    DOWN = -1


def give_direction(target_floor: int, floor_elevator: int) -> Direction:
    """ Return the direction according to the target floor and the current_floor
    """
    # Case 1: if the target_floor is higher
    if target_floor > floor_elevator:
        return Direction.UP
    # Case 2: if the target_floor is lower
    elif target_floor < floor_elevator:
        return Direction.DOWN
    # Case 3: if the target_floor is the same
    return Direction.STAY


def return_the_closet_floor(floor_diff: List[int]) -> int:
    """ Return the closet floor of all floors that have people waiting for
    elevator.

    If there is tie floor, return the lower floor

    === Precondition ===
    - floor_diff[0] = max_floor + 1
    - all floors that no people waiting for
      the elevator has a value of max_floor+1
    - the index of value in floor_diff is the floor num
    - there must be people waiting for the elevator

    """
    closet = min(floor_diff)
    tie = []

    for index, diff in enumerate(floor_diff):
        if diff == closet:
            tie.append(index)

    return min(tie)  # alternative : tie[0]


def give_direction_waiting(waiting_list: Dict[int, List[Person]],
                           elevator: Elevator,
                           max_floor: int) -> Direction:
    """ For shortsighted algorithm! When the elevator is empty!
    """
    floor_diff = [max_floor+1, ]  # floor starts from 1
    people_waiting = False
    for floor in sorted(waiting_list.keys()):
        # if the floor is the elevator is on
        # or if there is no person waiting for elevator
        if floor == elevator.track_floor() or len(waiting_list[floor]) == 0:
            floor_diff.append(max_floor+1)
        else:  # when there is person waiting for the elevator
            floor_diff.append(abs(elevator.track_floor() - floor))
            people_waiting = True

    if not people_waiting:  # when there is no person waiting for elevator
        return Direction.STAY  # the elevator stay still
    else:
        return give_direction(return_the_closet_floor(floor_diff),
                              elevator.track_floor())


def give_direction_in_elevator(elevator: Elevator, max_floor: int) -> Direction:
    """ For shortsighted algorithm! When the elevator is not empty
    """
    floor_diff = [max_floor + 1 for i in range(max_floor + 1)]

    for passenger in elevator.passengers:
        floor_diff[passenger.target] = abs(elevator.track_floor() -
                                           passenger.target)

    return give_direction(return_the_closet_floor(floor_diff),
                          elevator.track_floor())


class MovingAlgorithm:
    """An algorithm to make decisions for moving an elevator at each round.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        """
        raise NotImplementedError


class RandomAlgorithm(MovingAlgorithm):
    """A moving algorithm that picks a random direction for each elevator.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        """

        list_of_directions = []

        # iterate through all elevators
        for elevator in elevators:
            # case 1: when the elevator is on top floor
            if elevator.current_floor == max_floor:
                list_of_directions.append(choice([Direction.DOWN,
                                                 Direction.STAY]))

            # case 2: when the elevator is on Floor 1
            elif elevator.current_floor == 1:
                list_of_directions.append(choice([Direction.UP,
                                                  Direction.STAY]))
            # other cases
            else:
                list_of_directions.append(choice(list(Direction)))

        # assertion make sure no elevator will move out of bound
        for direction, elevator in zip(list_of_directions, elevators):
            temp = elevator.track_floor() + direction.value
            assert 1 <= temp <= max_floor

        return list_of_directions


class PushyPassenger(MovingAlgorithm):
    """A moving algorithm that preferences the first passenger on each elevator.

    If the elevator is empty, it moves towards the *lowest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the target floor of the
    *first* passenger who boarded the elevator.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """ Return a list of directions for all elevators
        """
        directions = []
        people_waiting = False

        # iterate through all elevators
        for elevator in elevators:
            # Case 1: if the elevator is empty
            if len(elevator.passengers) == 0:
                # iterate the list of waiting passengers on all floors
                for floor in sorted(waiting.keys()):
                    # if there is at least one person waiting for elevators
                    if len(waiting[floor]) >= 1:
                        directions.append(give_direction(floor,
                                                         elevator.track_floor()
                                                         )
                                          )
                        # if there is at least one person waiting for elevators
                        people_waiting = True
                        break
                # if there is no person waiting for elevators
                if not people_waiting:
                    directions.append(Direction.STAY)

            # Case 2: if the elevator is not empty:
            else:
                directions.append(give_direction(elevator.passengers[0].target,
                                                 elevator.track_floor()))

        # assertion to ensure the elevator does not move out of bound
        for direction, elevator in zip(directions, elevators):
            temp = elevator.track_floor() + direction.value
            assert 1 <= temp <= max_floor

        return directions


class ShortSighted(MovingAlgorithm):
    """A moving algorithm that preferences the closest possible choice.

    If the elevator is empty, it moves towards the *closest* floor that has at
    least one person waiting (lower floor if there is tie),
    or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the closest target floor of
    all passengers who are on the elevator. (lower floor if there is tie)

    In this case, the order in which people boarded does *not* matter.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """ Return a list of directions for all elevators
        """
        directions = []

        # iterate through all elevators
        for elevator in elevators:
            # if the elevator is empty
            if len(elevator.passengers) == 0:
                directions.append(give_direction_waiting(waiting,
                                                         elevator,
                                                         max_floor))

            # if the elevator is not empty
            else:
                directions.append(give_direction_in_elevator
                                  (elevator, max_floor)
                                  )
        return directions


if __name__ == '__main__':
    # Don't forget to check your work regularly with python_ta!
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['__init__'],
        'extra-imports': ['entities', 'random', 'csv', 'enum'],
        'max-nested-blocks': 4,
        'max-attributes': 12,
        'disable': ['R0201']
    })
