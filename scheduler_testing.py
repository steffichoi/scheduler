from scheduler_csp import *
import copy
from random import shuffle


'''    def __init__(self, name, day, time, span=1, subtask=False, multi=1, prerequisite=[], pre_enter=None, priority=1):
        
        Create a task object with descriptions:
            Name, 
            Due day, 
            Due time, 
            The time span needed to complete the task，
            A boolean value specifying if the task can be broken up into subtasks,
            The number of activities that can be done simultaneously,
            An optional prerequisite list (containing Task objects that must be 
                completed before this one),
            A Slot name that act as the pre-entered time,
            A number lifting the Task priority.

             self.name = name                #str
        self.dueDay = day               #str
        self.dueTime = time             #int
        self.multi = multi              #int
        self.span = span                #int
        self.subtask = subtask          #boolean
        self.order = prerequisite       #[Task]
        self.pre = pre_enter            #str
        self.pri = priority             #int
        
'''

def check_const(tasks, initial, final, startdate):
    '''
    tasks = tasks to be planned
    initial = initial schedule
    final = final schedule

    checking for each task:
    1. tasks done on time
    2. tasks allocated enough time
    3. tasks broken/not broken
    4. simultaneous # of activities not violated


    checking for old and new schedules
    2. lectures/breaks stay the same
    3. tasks not in conflict with lectures/breaks
    4. tasks pre-entered should stay where they are ! 
    5. tasks not overflowing a day's tasks
    

    '''
    failed = False 
    #checking for each task:
    for i in range(len(tasks)):
        #find all slots allocated for it
        assignments = []
        broken = False
        for j in range(len(final)):
            for k in range(len(final[j])):
                if ( final[j][k] and tasks[i].name in final[j][k]):
                    temp = [j, k, len(final[j][k])]
                    
                    #3 checking if task is broken unexpectedly?
                    if( not(tasks[i].subtask) and assignments):
                        
                        if((temp[0] == assignments[-1][0] and temp[1] != assignments[-1][1]+1) or
                        ( (temp[0] == (assignments[-1][0] + 1)) and temp[1] != 0) or
                            (temp[0] > assignments[-1][0] + 1)):
                                print('Task ' + task.name + 'is broken when it is not supposed to be')
                                #continue
                        
                    assignments.append(temp)


        
        if(not(assignments)):
            print('Task '+tasks[i].name+' was not allocated!!!!!!! ')
            continue
     
        
        #1. done on time
        index = (tasks[i].due - startdate).days
        
        if( (assignments[len(assignments) - 1][0] > index) or ( assignments[len(assignments) - 1][0] == index and  assignments[len(assignments) - 1][1] >= index)):
            failed = True
            print('Task '+tasks[i].name+' finished after its due date!')
            continue
        
        #2. not enough/ too much time?
        if( len(assignments) != tasks[i].span):
            failed = True
            print('it used time: '+str(len(assignments)))
            print('Task '+tasks[i].name+' was not allocated enough hours!')
            continue

        
        #4. simultaneous # of activities respected?
        for assign in assignments:
            if(assign[2] > tasks[i].multi):
                failed = True
                print('Error: Task ' + 'violated number of concurrent task on day '+assign[0]+' and hour '+assign[1])
                continue

        #print('PASS: task ['+task.name+'] ')

    #Following are just checking for consistency betweenn old and new schedules. 
    #Meant as a sanity check. Just incase our code changes the original schedule in unexpected ways. 

    #1.checking number of days are the same:
    if(len(initial) != len(final)):
        failed = True
        print('Error: Number of days changed.')
        
    for i in range(len(initial)):
        #5: number of hours should stay the same!
        if(len(initial[i]) != len(final[i])):
            failed = True
            print('Error: Number of hours changed on day '+i)
        for j in range(len(initial[i])):
            #3: breaks/lectures must remain where they were and not in conflict with any task
            if(initial[i][j]):
                if( ('B' in initial[i][j]) and (len(final[i][j]) != 1 or final[i][j][0] != 'B') ):
                    failed = True
                    print('Error: Break on day '+i+' and hour '+j+' has some problems in the final result!!')
                elif(('L' in initial[i][j]) and (len(final[i][j]) != 1 or final[i][j][0] != 'L') ):
                    failed = True
                    print('Error: Lecture on day '+i+' and hour '+j+' has some problems in the final result!!')
                elif(len(initial[i][j])>1):               
                    #4. : pre entered tasks must remain where they are !
                    for pre_entered in intial[i][j]:
                        if(not(pre_entered in final[i][j])):
                            failed = True
                            print('Error: Pre entered task '+pre_entered+' on day '+i+' disappeared in the final result!!')
                
    if(not(failed)):
        print('SUCCESS')
    else:
        print('SOME FAILURES')
    return failed

    
def compose_tasks_for_deadline_testing(schedule, startdate, multiplicity = 1, timespan = 1, opt = -1, invalid = 0):

    '''
    def __init__(self, name, due, span=1, subtask=False, multi=1, prerequisite=[], pre_enter=None, priority=1):
        
        self.name = name                #str
        self.due = due                  #datetime
        self.multi = multi              #int
        self.span = span                #int
        self.subtask = subtask          #boolean
        self.order = prerequisite       #[Task]
        self.pre = pre_enter            #datetime
        self.pri = priority             #int
    '''
     
    tasks = []
    num = 0
    duration = 0
    for day in schedule:
        for hour in day:
            if(not(hour)):
                if(num == timespan):
                    if(opt != -1 and schedule.index(day) >= opt):
                        shuffle(tasks)
                        return [tasks, duration]
                    duration = duration + 1
                    num = 1
                else:
                    num = num + 1
                    duration = duration + 1
                    if(tasks):
                        continue
                
                for i in range(multiplicity):
                    if(tasks):
                        name = "task"+str(len(tasks))
                    else:
                        name = "task0"
                    tasks.append(Task(name, startdate + timedelta(schedule.index(day)*24 + 6+ day.index(hour) + 1), timespan, True, multiplicity ))
                    
    
    if(invalid == 1):        
        # we are adding one extra task to make it impossible to schedule these tasks!
        tasks.append(Task("extra", startdate + timedelta(len(schedule)*24), 1, True, 1 ))

    shuffle(tasks)
    return [tasks, duration]



def compose_initial_schedule(days, hours, spacing = 1):
    schedule = []
    L_or_B_or_N = 0
    spaces = 0
    for i in range(days):
        day = []
        for j in range(hours):
            if(L_or_B_or_N  == 0):
                day.append('L')
                L_or_B_or_N = 1
            elif(L_or_B_or_N  == 1):
                day.append('B')
                L_or_B_or_N = 2
                spaces = 0
            else:
                day.append(None)
                if(spaces < spacing):
                    spaces = spaces + 1
                    L_or_B_or_N = 2
                else:
                    L_or_B_or_N = 0
        schedule.append(day)
    return schedule 
                



    
def constraint_satisfaction_testing():

    '''
    This function checks for the resulting schedule's compliance to constraints.
    It creates tasks that have deadline right after them.
    For each task, we check:

       1. deadlines are respected
       2. multiplicity is respected
       
    '''
    


    #Test 1: Make the deadlines extremely early and check:
    #1. Deadlines are respected!
    #2. Multiplicity is respected!

    
#Using BT
    print('constraint_satisfaction_testing 1 (BT) Starts. ')
    print('\n\n\n\n')
    print('Building CSP and Search:')
    old1 = compose_initial_schedule(8, 6)

    old1_copy = copy.deepcopy(old1)
    [tasks1, duration] = compose_tasks_for_deadline_testing(old1, datetime(2016, 1, 1, 0), 3, 2)
    tasks1_copy = copy.deepcopy(tasks1)   
    csp1 = scheduler_csp_model(tasks1, datetime(2016, 1, 1), old1)
            
    bt1 = BT(csp1[0])
    bt1.bt_search(prop_BT)

    final1 = apply_sol(old1, bt1.csp)
    

    print('\n\n\n\n')
    print('Testing Results:')
    print('\n')
    print('Initial Schedule:')
    print(old1)
    print('\n')
    print('Tasks:')
    print(tasks1)
    print('\n')
    print('Final Schedule:')
    print(final1)
    print('\n')
    check_const(tasks1_copy, old1_copy, final1, datetime(2016, 1, 1))
    

    
#USING FC
    print('constraint_satisfaction_testing 2 (FC)Starts. ')
    print('\n\n\n\n')
    print('Building CSP and Search:')
    old2 = compose_initial_schedule(7, 4)

    old2_copy = copy.deepcopy(old2)
    [tasks2, duration2] = compose_tasks_for_deadline_testing(old2, datetime(2016, 1, 1, 0), 3, 2)
    tasks2_copy = copy.deepcopy(tasks2)   
    csp2 = scheduler_csp_model(tasks2, datetime(2016, 1, 1), old2)
            
    bt2 = BT(csp2[0])
    bt2.bt_search(prop_FC)

    final2 = apply_sol(old2, bt2.csp)
    

    print('\n\n\n\n')
    print('Testing Results:')
    print('\n')
    print('Initial Schedule:')
    print(old2)
    print('\n')
    print('Tasks:')
    print(tasks2)
    print('\n')
    print('Final Schedule:')
    print(final2)
    print('\n')
    check_const(tasks2_copy, old2_copy, final2, datetime(2016, 1, 1))


#USING GAC
    print('constraint_satisfaction_testing 3 (GAC)Starts. ')
    print('\n\n\n\n')
    print('Building CSP and Search:')
    old3 = compose_initial_schedule(8, 6)

    old3_copy = copy.deepcopy(old3)
    [tasks3, duration3] = compose_tasks_for_deadline_testing(old3, datetime(2016, 1, 1, 0), 3, 2)
    tasks3_copy = copy.deepcopy(tasks3)   
    csp3 = scheduler_csp_model(tasks3, datetime(2016, 1, 1), old3)
            
    bt3 = BT(csp3[0])
    bt3.bt_search(prop_GAC)

    final3 = apply_sol(old3, bt3.csp)
    

    print('\n\n\n\n')
    print('Testing Results:')
    print('\n')
    print('Initial Schedule:')
    print(old3)
    print('\n')
    print('Tasks:')
    print(tasks3)
    print('\n')
    print('Final Schedule:')
    print(final3)
    print('\n')
    check_const(tasks3_copy, old3_copy, final3, datetime(2016, 1, 1))

    

# Checking invalid inputs
    # simply feeding in more tasks than available empty slots. 
    print('constraint_satisfaction_testing 3 (GAC)Starts. ')
    print('\n\n\n\n')
    print('Building CSP and Search:')
    old4 = compose_initial_schedule(4, 4)

    old4_copy = copy.deepcopy(old4)
    [tasks4, duration4] = compose_tasks_for_deadline_testing(old4, datetime(2016, 1, 1, 0), 1, 1, invalid = 1)
    tasks4_copy = copy.deepcopy(tasks4)   
    csp4 = scheduler_csp_model(tasks4, datetime(2016, 1, 1), old4)
            
    bt4 = BT(csp4[0])
    bt4.bt_search(prop_GAC)

    final4 = apply_sol(old4, bt4.csp)
    

    print('\n\n\n\n')
    print('Testing Results:')
    print('\n')
    print('Initial Schedule:')
    print(old3)
    print('\n')
    print('Tasks:')
    print(tasks3)
    print('\n')
    print('Final Schedule:')
    print(final3)
    


def get_time_consumed(tasks, final):
    #goal: return number of hours allocated to tasks
    total_hrs = 0
    for day in final:
            for hour in day:
                if(not(hour)):
                    continue
                for t in hour:
                    found = False
                    for x in tasks:
                        if ( t == x.name):
                            total_hrs = total_hrs + 1
                            found = True
                            break
                    if(found):
                        break
                        
    return total_hrs



def solution_optimization_testing():
    '''
    compose_tasks_for_deadline_testing(schedule, startdate, multiplicity = 1, timespan = 1, opt = -1):
    '''
    print('optimization_testing 1    (BT)   Starts. ')
    print('\n\n\n\n')
    print('Building CSP and Search:')
    old1 = compose_initial_schedule(8, 6)

    old1_copy = copy.deepcopy(old1)
    [tasks1, duration] = compose_tasks_for_deadline_testing(old1, datetime(2016, 1, 1, 0), 3, 2, 3)
    tasks1_copy = copy.deepcopy(tasks1)   
    csp1 = scheduler_csp_model(tasks1, datetime(2016, 1, 1), old1)
            
    bt1 = BT(csp1[0])
    bt1.bt_search(prop_BT)

    final1 = apply_sol(old1, bt1.csp)
    

    print('\n\n\n\n')
    print('Testing Results:')
    print('\n')
    print('Initial Schedule:')
    print(old1)
    print('\n')
    print('Tasks:')
    print(tasks1)
    print('\n')
    print('Final Schedule:')
    print(final1)
    print('\n')
    check_const(tasks1_copy, old1_copy, final1, datetime(2016, 1, 1))
    

    print('This is the duration I estimated: ' + str(duration))
    print('This is the actual duration: ' + str(get_time_consumed(tasks1_copy, final1)))

    if(get_time_consumed(tasks1_copy, final1) > duration):
        print('WHAT? Result is slower than how I would have done it? FAIL!')
    else:
        print('Estimated > Actual: PASS!')






    print('optimization_testing 2    (FC)   Starts. ')
    print('\n\n\n\n')
    print('Building CSP and Search:')
    old2 = compose_initial_schedule(4, 6)

    old2_copy = copy.deepcopy(old2)
    [tasks2, duration2] = compose_tasks_for_deadline_testing(old2, datetime(2016, 1, 1, 0), 3, 2, 3)
    tasks2_copy = copy.deepcopy(tasks2)   
    csp2 = scheduler_csp_model(tasks2, datetime(2016, 1, 1), old2)
            
    bt2 = BT(csp2[0])
    bt2.bt_search(prop_FC)

    final2 = apply_sol(old2, bt2.csp)
    

    print('\n\n\n\n')
    print('Testing Results:')
    print('\n')
    print('Initial Schedule:')
    print(old2)
    print('\n')
    print('Tasks:')
    print(tasks2)
    print('\n')
    print('Final Schedule:')
    print(final2)
    print('\n')
    check_const(tasks2_copy, old2_copy, final2, datetime(2016, 1, 1))
    

    print('This is the duration I estimated: ' + str(duration2))
    print('This is the actual duration: ' + str(get_time_consumed(tasks2_copy, final2)))

    if(get_time_consumed(tasks2_copy, final2) > duration2):
        print('WHAT? Result is slower than how I would have done it? FAIL!')
    else:
        print('Estimated > Actual: PASS!')




    print('optimization_testing 2    (GAC)   Starts. ')
    print('\n\n\n\n')
    print('Building CSP and Search:')
    old3 = compose_initial_schedule(5, 5)

    old3_copy = copy.deepcopy(old3)
    [tasks3, duration3] = compose_tasks_for_deadline_testing(old3, datetime(2016, 1, 1, 0), 3, 2, 3)
    tasks3_copy = copy.deepcopy(tasks3)   
    csp3 = scheduler_csp_model(tasks3, datetime(2016, 1, 1), old3)
            
    bt3 = BT(csp3[0])
    bt3.bt_search(prop_FC)

    final3 = apply_sol(old3, bt3.csp)
    

    print('\n\n\n\n')
    print('Testing Results:')
    print('\n')
    print('Initial Schedule:')
    print(old3)
    print('\n')
    print('Tasks:')
    print(tasks3)
    print('\n')
    print('Final Schedule:')
    print(final3)
    print('\n')
    check_const(tasks3_copy, old3_copy, final3, datetime(2016, 1, 1))
    

    print('This is the duration I estimated: ' + str(duration3))
    print('This is the actual duration: ' + str(get_time_consumed(tasks3_copy, final3)))

    if(get_time_consumed(tasks3_copy, final3) > duration3):
        print('WHAT? Result is slower than how I would have done it? FAIL!')
    else:
        print('Estimated > Actual: PASS!')



        



        
    
if __name__ == '__main__':
    
    constraint_satisfaction_testing()
    solution_optimization_testing()
   
    
