# scheduler

Developed a solution to a scheduler problem in a group of 3 people.

## Problem
Given a schedule and a number of tasks, the program schedules when each task
should be completed, taking into account the properties of the task, which 
include:
- the task's priority level
- the task's due date
- the task's estimated time span needed to complete
- if the task can be broken up into subtasks
- the number of activities that can be multitasked with the task
- a list of tasks that need to be completed (prerequisites) before this task

## Solution

### scheduler_csp.py
To solve this problem, we constructed 2 classes: Task and Slot.

#### Task
This class contains all the attributes associated with the task, as listed 
in the problem section.
This class has a method split(), which is called on a Task object to try 
split the task into subtasks.  It returns the list of subtasks, or a list 
containing itself if it cannot be split.
#### Slot
This class represents a timeslot in the schedule, with an attribute
-assigned, a list of tasks that have been assigned to this timeslot-
and 4 methods.
These methods include:
- assign(self, task)
- unassign(self, task)
- get_capacity(self, candidate=None)
If the Slot has not been assigned a Task, the slot is available, "inf" 
is returned.  If there a Task has been assigned to the Slot, the value
returned will be the smallest multitask value, indicating if more Tasks
can be assigned to this Slot.
- next(self, slots)
Returns the next timeslot in the schedule.

### propagators.py
Implemented 3 propagators:
- prop_BT
backtracking propagation
- prop_FC
forward checking
- prop_GAC
GAC propagation

### cspbase.py
Provided classes for CSP, containing classes for:
Variable, Constraints, CSP and BT

### scheduler_testing.py
A small testing suite to test program functionality
