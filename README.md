# Bahen-Elevator-Simulator
This is a simulator of a elevator with different algorithms on stopping on different floors to pick up passengers. This is an application of pygame.



# Preparation before running this simulation

- Install all packages in `Requirements.txt`



## Problem domain overview

The context of our elevator simulation is a building which has a specified number of floors (numbered starting at Floor 1) and elevators that can move between each floor. People can arrive at the elevators at any floor, and elevators move to pick up people and (hopefully) take them to their desired destination floor.

Our elevator simulation consists of three main parts:

1. The basic entities contained in the simulation: people and elevators.
2. The update algorithms that determine how the entities change over time (how new people appear in the simulation, how elevators decide to move across floors).
3. The main runner of the simulation, which is responsible for setting up the initial parameters of the simulation, running the simulation, determining when the simulation should end, and reporting the results of the simulation.



## People

Every round of the simulation, zero or more new people arrive at the elevators. A person in the simulation has three characteristics: which floor they started on, which floor they want to go to, and the number of *simulation rounds* they have been waiting to reach their target floor. The building’s floors are numbered starting at 1, meaning each person’s starting and target floor should be between 1 and the maximum floor number of the building, inclusive.

Each person’s waiting time increases both when they’re waiting at a floor, and when they’re traveling on an elevator.

## Elevators

The simulation has a fixed number of elevators that all begin the simulation at Floor 1 of the building. An elevator can move one floor (up or down) per simulation round, and so we only need to track which floor each elevator is on, and *don’t* need to worry about an elevator being “between floors”. Each elevator keeps track of its passengers (which people are currently on it), as well as its maximum capacity—if an elevator is full, no more people can board it. Each elevator must be able to track the order in which people boarded it.

## Arrival generation algorithms

At the start of each simulation round, new people may arrive at the elevators. There are different ways to decide how many people arrive at a given round, and the starting and target floors of each person. On this assignment, you’ll implement two different approaches described below.

### Random generation

Each round, a fixed number of people are randomly generated; their starting and target floors are all random, with the requirement that a person’s starting and target floor can’t be the same.

### Generation from file data

A **csv file** is a text file that uses commas to separate pieces of data. (“csv” stands for “comma-separated values”)

Our second approach for arrival generation is to read arrivals from a csv file, in the following format:

- Each line of the file represents all of the arrivals for a certain round number.
- On a single line, the first value is the *round number* that this line specifies. This is followed by an even number of other entries, divided into pairs of numbers. In each pair, the first number is the starting floor and the second number is the target floor of a new arrival. The arrivals occur in the order the pairs appear in the line. Each line must have at least one pair (i.e., store at least one new arrival).

For example, the following data file

```
1, 1, 4, 5, 3
3, 1, 2
5, 4, 2
```

represents the following arrivals:

- Round 1: one person whose starting floor is 1 and target floor is 4, and another person whose starting floor is 5 and target floor is 3, in that order.
- Round 3: one person whose starting floor is 1 and target floor is 2.
- Round 5: one person whose starting floor is 4 and target floor is 2.

You may make the following assumptions about input files for this assignment:

1. They are all in the format described above.
2. The round numbers are non-negative, and are less than the maximum number of rounds in the simulation. (Note: round numbers start at *zero*, not one.)
3. Each round number is unique (no two lines start with the same number). But *don’t* assume that the lines are in any particular order.
4. Each person has starting and target floors that are positive, and do not exceed the maximum number of floors in the simulation.
5. Each person has a target floor that’s different from their starting floor.

## Elevator moving algorithms

Each round, an *elevator moving algorithm* makes a decision about where each elevator should move. Because an elevator can only move one floor per round, this decision can have one of three outputs: the elevator should move up, move down, or stay in the same location.

A *moving algorithm* receives as input two values: a list of all the elevators in the simulation, and a dictionary mapping floor numbers to a list of people who are waiting on that floor. It outputs a list of decisions (one for each elevator) specifying in which direction it should move.

This is an extremely flexible model of how elevators move (in real-life, the use of elevator buttons makes this much more constrained), and the reason we do this is so that that you can implement a variety of fun and interesting elevator algorithms! On this assignment, you will implement the following three algorithms.

### Random algorithm

The algorithm makes a random decision for each elevator, choosing between each of the three possibilities with equal probability. These choices are made independently for each elevator.

### Pushy Passenger algorithm

This algorithm makes a decision independently for each elevator.

If the elevator is empty (has no passengers), it moves towards the *lowest* floor that has at least one person waiting, or stays still if there are no people waiting. Because the decisions are independent for each elevator, if at least one person is waiting, *all* empty elevators move to the same floor.

If the elevator isn’t empty, it moves towards the target floor of the *first*passenger who boarded the elevator.

### Short-sighted algorithm

This algorithm makes a decision independently for each elevator.

If the elevator is empty, it moves towards the *closest* floor that has at least one person waiting, or stays still if there are no people waiting. In the case of ties (e.g. if the elevator is at floor 3, and there are people waiting at floors 2 and 4), it moves towards the *lower* floor. ~~As in the previous algorithm, because the decisions are independent for each elevator, *all* empty elevators move to the same floor.~~ (*Updated*, the previous sentence didn’t make sense for this algorithm, and should be ignored.)

If the elevator isn’t empty, it moves towards the closest target floor of all passengers who are on the elevator, again breaking ties by moving towards the *lower* floor. In this case, the order in which people boarded does not matter.

## Simulation

The main simulation program itself is divided into three stages: initializing the simulation with a given configuration, running the simulation, and then calculating and reporting statistics at the end of the simulation.