'''
Construct and return Scheduler CSP models.
'''

from cspbase import *
from propagators import *
import itertools
from datetime import datetime, timedelta
from copy import copy, deepcopy



start = 6  #default start time
days31, days30 = [1,3,5,7,8,10,12], [4,6,9,11]
months = ["JAN","FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", 
"OCT", "NOV", "DEC"]

def scheduler_csp_model(tasks_list, start_date, initial_schedule, start_hrs=[]):
    '''
    OUTPUTS
    Return a CSP object representing a Scheduler CSP problem along with an 
    array of variables for the problem. That is, return

        scheduler_csp, variable_array

    where scheduler_csp is a csp representing a scheduler problem and 
    variable_array is a list of Variables in use by the csp.


    INPUTS
    tasks_list: A list of Tasks to be fit into the schedule.

    start_date: A datetime object with at least year, month, date specified. 
    This is the starting day of the schedule.

    initial_schedule: Specified as a list of m lists. Each of the m lists
        represents a day on the schedule. If a None is in the list it 
        represents an empty cell. Otherwise if a string 'L' or 'B' is in the 
        list then this represents a pre-set lecture or break in the schedule 
        that cannot be changed.
    
        These lists can have different lengths, where each space in these lists
        represents a timeslot for the day. If a sub-list is empty, this day is 
        skipped.
    
        E.g., the schedule
        ---------------------------------------------------
            |day1 |day2 |day3 |day4 |day5 | day6 | day7 |
        0600|     |     |     |     |     |      |      | 
        0700|     |     |     |     |     |      |      | 
        0800|     |     |     |     |     |      |      |
        0900| 'L' | 'L' | 'L' | 'L' | 'L' |      |      | 
        1000|     | 'L' |     | 'L' |     |      |      |
        1100|     |     |     |     |     |      |      | 
        1200| ‘L' | ‘B’ | ‘L’ | ‘B’ | ‘L’ | Skip | ‘B’  | 
        1300|     | ‘B’ |     | ‘B’ |     | This | ‘B’  | 
        1400| ‘B’ |     | ‘B’ |     | ‘B’ | Day! |      | 
        1500| ‘B’ |     | ‘B’ |     | ‘B’ |      |      | 
        1600|     |     |     |     |     |      |      | 
        1700| 'L' |     |     |     |     |      |      | 
        1800|     | 'L' |     | 'L' |     |      |      | 
        1900|     | 'L' |     | 'L' |     |      |      | 
        2000|     | ‘L’ |     | 'L' |     |      | 'B'  | 
        2100|     |     |     |     |     |      |      |
        -------------------------------------------------
        could be represented by the list of lists:
       [[None, None, None, 'L' , None, None, 'L' , None, 'B' , 'B' , None,
        'L' , None, None, None, None],
        [None, None, None, 'L' , 'L' , None, 'B' , 'B' , None, None, None, 
        None, 'L' , 'L' , 'L' , None],
        [None, None, None, None, None, None, 'L' , None, 'B' , 'B' , None, 
        'L' , None, None, None, None],
        [None, None, None, 'L' , 'L' , None, 'B' , 'B' , None, None, None, 
        None, 'L' , 'L' , 'L' , None],
        [None, None, None, None, None, None, 'L' , None, 'B' , 'B' , None, 
        'L' , None, None, None, None],
        [],
        [None, None, None, None, None, None, 'B' , 'B' , None, None, None, 
        None, None, None, 'B' , None]]
    
    start_hrs: Optional. a list of integer od length m specifying the starting 
    hours of every day in the initial schedule. Tasks are scheduled starting 
    from these hours.


    CONSTRAINTS
    The csp also contains a number of constraints:

        Prerequisite:  Some tasks must be done before a task. (Scope: binary 
        between two tasks in concern.)
        
        Subtasks in differnt Slots:  Subtasks of a task should not be done 
        simutaneously.(Scope: task Variables that are subtasks of the same task. 
        n-array all different constraint.)
        
        Priority constraint:  Some task are more urgent than others. This is 
        enforced by sorting the variable list passed into the csp and hence 
        the search engine so the engine assigns them in this order. This 
        implementation is used because it can not always be followed. 
        (Due to prerequisite requirements or insufficient space or others.)
        
        Due:  Tasks must be completed before due. This constraint has been 
        fused into the task Variables. When initializing Variables their 
        domains are limited to contain only Slots before due.
    
    The mutitasking constraint is integrated into cspbase under Variable and 
    does checking when assigning Variables. This constraint performs real 
    time checking. That is, without storing tuples.
    '''
    # Sort search list based on priority and due datetime
    tasks = list(tasks_list)
    tasks.sort(key=lambda x:(-x.pri,x.due))
    
    # Initialize Slots
    slots = init_slots(start_date, initial_schedule, start_hrs)
            
    # Split tasks into subtasks
    splitted = []
    var_array = []
    for t in tasks:
        ts = t.split()
        sub_t_vars = []
        
        # Initialize sub tasks as Variables
        for sub_t in ts:
            var = Variable(sub_t)
            
            if sub_t.pre and find_slot(str(sub_t.pre), slots):
                var.add_domain_values([find_slot(str(sub_t.pre), slots)], 
                    sub_t.span, slots)
            else:
                for s in slots:
                    if s.time < sub_t.due:
                        var.add_domain_values([s], sub_t.span, slots)
                    else:
                        break
                        
            sub_t_vars.append(var)
            
        var_array += sub_t_vars
        splitted.append(sub_t_vars)
                
    # Initialize CSP object
    scheduler_csp = CSP("ScheduleCSP", var_array)
    
    # No subtasks in same time slot constraints.
    for ts in splitted:
        c = Constraint("no_duplicate_"+ts[0].name[:ts[0].name.rfind("_")], ts)
        
        for d in domains_permutation(ts):
            dup = False
            for x in d:
                if x in d[:d.index(x)] or x in d[d.index(x)+1:]:
                    dup = True
                    break
            if not dup:
                c.add_satisfying_tuples([d])
                
        scheduler_csp.add_constraint(c)
        
    # Ordering constraints.
    for var in var_array:
        t=var.task
        for t0 in t.order:
            t0_vars = find_task_vars(t0.name, var_array)
            c = Constraint(t0.name+"_before_"+t.name, t0_vars+[var])
            
            for d in domains_permutation(t0_vars+[var]):
                if check_prerequisite(d[:-1], d[-1]):
                    c.add_satisfying_tuples([d])
                    
            scheduler_csp.add_constraint(c)
            
    
    return scheduler_csp, var_array
    
    
def init_slots(start_date, initial_schedule, start_hrs=[]):
    slots, t = [], copy(start_date)
    days_count = len(initial_schedule)
    if len(start_hrs) < days_count:
        start_hrs = [start]*days_count
    
    for d in range(days_count):
        for h in range(len(initial_schedule[d])):
            
            if initial_schedule[d][h] == None:
                slots.append(Slot(datetime(t.year,t.month,t.day,h+start_hrs[d]),
                 (d,h)))
                
        t += timedelta(days=1)        
    return slots


def domains_permutation(vars):
    '''
    Generates permutation of the domains of the vars list.
    '''
    if len(vars)==1:
        return [(d,) for d in vars[0].domain()]
    return [(d,)+c for c in domains_permutation(vars[1:]) for d in vars[0].domain()]
    
    
def find_slot(name, slots):
    '''
    Return a Slot whose name is the same as the given.
    '''
    for s in slots:
        if s.name == name:
            return s
    return None
            
def find_task_vars(name, vars):
    '''
    Return a list of task Variables whose names are the same as the given or 
    are the subtasks of the task with the name given.
    '''
    result = []
    for v in vars:
        if v.name == name or v.name[:v.name.rfind("_")] == name:
            result.append(v)
    return result


def check_prerequisite(prerequisite, second):
    '''
    Judge if candidate assignments to variables satisfy prerequisite constraint.
    Return True iff all spans of tasks in prerequisite list are done before 
    second. 
    '''
    for first in prerequisite:
        if first[-1].time >= second[0].time:
            return False
    return True
    
    
    
def apply_sol(initial_schedule, csp):
    '''
    Inserts the assigned tasks into the initial_schedule.
    '''
    board = deepcopy(initial_schedule)
    
    for t in csp.get_all_vars():
        if not t.get_assigned_value():
            continue

        for s in t.get_assigned_value():

            d = s.pos[0]
            h = s.pos[1]

            trim_idx = t.name.rfind("_")
            name = t.name
            if name[trim_idx+1:].isdigit():
                name = t.name[:trim_idx]

            if board[d][h] == None:
                board[d][h] = [name]
            else:
                board[d][h].append(name)
            
    return board
    
        
        
        
def print_schedule(full_schedule, start_date):  
    '''
    Prints a pretty schedule board table. If csp is not given,
    The initial board is printed.
    '''
    line_len = 7  # Control number of days printed before page flip. 
    min_width = 15  # Control the minimum width of columns.
    
    schedule = deepcopy(full_schedule)
    days = copy(start_date)
    
    # Keep printing until no more page left
    while True:
        board = schedule[:line_len]
        width = [min_width] * len(board)
        
        # Align the lower end of the board so it can be transposed.
        max_len = max([len(d) for d in board] + [0])
        for day in board:
            while len(day) < max_len:
                day.append(None)
                
        # Get time range for print.
        mth, dayz = [], []
        for c in range(len(board)):
            dayz.append(str(days.day))  
            mth.append( months[days.month-1] if days.day==1 else '' ) 
            width[c] = max([len(mth[-1]), len(dayz[-1]), width[c]])                    
            days += timedelta(days=1)  
                
        # Calculate minimum width needed to print each column.
        for col in range(len(board)):
            for cell in board[col]:
                if type(cell) == list:
                    for task in cell:
                        width[col] = max(width[col], len(task))
        
        # Transpose the board for easier printing.
        board = [list(x) for x in zip(*board)]
        
        # Header of table. The [month and] days.
        header1, header2 = "      |", " Date |"
        for day in range(len(width)):
            header1 += " " + mth[day] + " "*(width[day]-len(mth[day])) +" |"
            header2 += " " + dayz[day] + " "*(width[day]-len(dayz[day])) +" |"
             
        horizontal = "-"*(sum(width)+3*len(width)+7)
        print (horizontal)
        if len(set(mth))>1:
            print (header1)
        print (header2)
        print (horizontal)
        
        # Rows of hours. If multi-tasking happen, span multiple lines.
        counter = 0
        for line in range(max_len):
            to_print = " "*(2-len(str(start+counter)))+str(start+counter)+":00 |"
            counter += 1
            
            # Rows of table, span one line for each.
            extra_count = 0
            while True:
                extra = False
                
                for l in range(len(board[line])):
                    to_print += " "
                    t=board[line][l]
                    
                    if t in ['L', 'B'] and extra_count ==0:
                        to_print += t+width[l]*" "+"|"
                        
                    elif type(t)==list and len(t)>extra_count:
                        to_print += t[extra_count]+" "*(width[l]-
                            len(t[extra_count]))+" |"
                        if len(t)>extra_count+1:
                            extra=True
                    else:
                        to_print += width[l]*" "+" |"
                        
                # Check if there is need to print multi-tasks.
                if not extra:
                    break
                
                # Get ready to print multi-tasks.
                extra_count +=1
                to_print+="\n      |"
                            
            print (to_print)
            print (horizontal)
        
        # Get ready to print next page.
        for z in range(line_len):
            schedule.pop(0)
            if not schedule:
                return


class Task:
    '''
    Class for defining a task value.  
    '''
    def __init__(self, name, due, span=1, subtask=False, multi=1, 
        prerequisite=[], pre_enter=None, priority=1):
        '''
        Create a task object with descriptions:
            Name, 
            Due time, a datetime object, specifying the year, month, date, hour.
            The time span needed to complete the task，
            A boolean value specifying if the task can be broken up into subtasks,
            The number of activities that can be done simultaneously,
            An optional prerequisite list (containing Task objects that must be 
                completed before this one),
            A datetime Object that acts as the pre-entered start time,
            A priority level. The larger the higher.
        '''
        self.name = name                #str
        self.due = due                  #datetime
        self.multi = multi              #int
        self.span = span                #int
        self.subtask = subtask          #boolean
        self.order = prerequisite       #[Task]
        self.pre = pre_enter            #datetime
        self.pri = priority             #int
        
    def split(self):
        '''
        Attempt to split a task into subtasks. Returns the list of subtasks, or 
        return a list containing itself if it cannot be split.
        '''
        if self.subtask and self.pre is None:
            return [Task(self.name+"_"+str(i), self.due, multi=self.multi, 
            prerequisite=self.order, priority=self.pri) for i in range(self.span)]
        else:
            return [self]
            
    def __repr__(self):
        return (str(self.name) + ":[" + str(self.due) + " due, " 
        + str(self.span) + "h needed, multi="+str(self.multi)+"]")
        
        
        
class Slot:
    def __init__(self, time, pos=None):
        '''
        Create a Slot object representing a timeslot in the schedule. Maintains 
        a list of task Variables assigned to it. 
        '''
        self.time = time
        self.assigned = []
        self.name = str(self.time)
        self.pos = pos
        
    def assign(self, t):
        '''Add the task Variable.'''
        self.assigned.append(t)
        
    def unassign(self, t):
        '''Remove the task Variable.'''
        if t in self.assigned:
            self.assigned.remove(t)
        else:
            print ("Warning: "+t.name+" is not assigned to "+self.name)
            
    def get_capacity(self, candidate=None):
        '''
        Returns the amount of space the Slot has.  If no Task has been 
        assigned to the Slot

        '''
        if candidate:
            c_multi = candidate.task.multi
        else:
            c_multi = float("inf")
        return min([t.task.multi for t in self.assigned]+[c_multi])-len(self.assigned)

    def next(self, slots):
        '''
        Return the name of the Slot right after this one. Strictly follows 
        time. So if the schedule ends at 8pm today and this slot is 8pm today,
        Slot 9pm would not be found and None is returned.
        '''
        return find_slot(str(self.time+timedelta(hours=1)), slots)
        
    def __repr__(self):
        return str(self.name)+ ":" + str([a.name for a in self.assigned])
        
        
        
        
        
if __name__ == '__main__':
    print ("\n##########Task class test##########")
    # Task object example initialization here:
    # Task init elements: name, dueDay, dueTime, [span=1, subtask=False, 
    # multi=1, prerequisite=[], pre_enter=None, priority=1]
    task1 = Task("dummy1", datetime(2016, 1, 5, 8), multi=2)
    task2 = Task("prerequisite-test", datetime(2016, 1, 4, 8), 2, True, 3, 
        [task1], priority=3)
    task3 = Task("multi-test", datetime(2016, 1, 5, 9), multi=2)
    task4 = Task("pre-entered", datetime(2016, 1, 3, 6), 
        pre_enter=datetime(2016, 1, 2, 7))
    task5 = Task("priority-test", datetime(2016, 1, 5, 6), span=2, multi=2, 
        priority=2)
    print (task1)
    print (task2.split())
    
    
    print ("\n##########Slot class test##########")
    # Slot object example initialization here:
    slot1 = Slot(datetime(2016, 1, 3, 6))
    slot1.assign(Variable(task2))
    print (slot1.get_capacity())
    
    
    print ("\n##########Var_array initialization test##########")
    initial_schedule = [[None, 'L'],['B', None], [None, None], [None, None]]
    # scheduler_csp_model example call here:
    csp = scheduler_csp_model([task1, task2, task3, task4, task5], 
        datetime(2016, 1, 1), initial_schedule)
    vars = csp[1]
    #for v in vars:
    #    print (v,": ", v.domain())
        
    
    print ("\n##########BT tests##########")  # Full basic usage below
    bt = BT(csp[0])
    #bt.trace_on()
    bt.bt_search(prop_FC)
    output = apply_sol(initial_schedule, bt.csp)
    
    print ("\n\nThe Initial table is,\n")
    # print_schedule example call here:
    print_schedule(initial_schedule,datetime(2016, 1, 1))
    print ("\n\nThe resulting table is, \n")
    print_schedule(output,datetime(2016, 1, 1))



