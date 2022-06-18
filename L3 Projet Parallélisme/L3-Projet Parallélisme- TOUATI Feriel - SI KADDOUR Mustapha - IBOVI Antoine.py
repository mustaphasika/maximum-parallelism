#Année universitaire: 2021/2022

#Projet Système d'exploitation : parallélisation de tâches

# Membres du groupe de travail:

#    NOM Prénom           : N°étudiant :  Spécialitée

#    TOUATI Feriel        : 20205426   : L3 ASR 
#    SI KADDOUR Mustapha  : 20205521   : L3 ASR
#    IBOVI Antoine        : 20184359   : L3 MIAGE FI

import threading
import time 
from time import sleep
import matplotlib.pyplot as plt
import networkx as nx
from graphviz import Digraph

#---------------------------------------------------------------Class Task-----------------------------------------------------------------------------------------------------

class Task:
    name = ""
    reads = []
    writes = []
    run = None
    done = None


#---------------------------------------------------------------Class TaskSystem----------------------------------------------------------------------------------------------

class TaskSystem:
    listtask = []
    precedences = {}

#-------------------------------------------------------TaskSystem Methods-----------------------------------------------------------------------------------------------------
    
    def __init__(self, tasks, dependances):
        self.listtask = tasks
        self.precedences = dependances

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def getDependancies(self, nomTask): # This function enable the extraction of a task's dependencies
        #We verify if the Task is the precedences list of the task system
        if nomTask in self.precedences:
            #we return the tasks list of dependencies corresponding to the key NomTask (precedencesformat={NomTask: [list of dependencies]})
            return self.precedences[nomTask] 
        else:
            return "la tache n'existe pas"
    
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def Run(self): # this function is used to run all taks system using parallelism

        tasknoorder = [] # to stock  tasks that still don't have an order of excution
        taskexcuted = [] # to stock tasks whose execution is laucnhed
        tasktobexcuted = [] # to stock tasks whose execution is done
        threads = [] # to stock all threads which are launched

        if self.verification(): # If the task System is valide we start the running procedure

            for task in self.listtask: # this loop is used to go through all the system's tasks to extract tasks with no dependencies
                # verify if the task doesn't have dependencies and add them to the list of tasks ready to be executed (tasktobexcuted)
                if self.getDependancies(task.name) == []: tasktobexcuted.append(task)

            
            for task in self.listtask: #this loop stock task that are still not ready to be executed in (tasknoorder)
                # we go through all tasks in the system and we keep only the ones who are not ready to be executed 
                if task not in tasktobexcuted:
                    tasknoorder.append(task)

            while tasknoorder: # this loop is used to run tasks who are possible to run at the same time using threads (parallelism) as long as there's at least one
                            # task is not exectuted(tasknoorder is not empty)

                for task in tasktobexcuted:  #this loop is used to launch all tasks ready to be exectuted with threads to launch them at the same time
                    
                    t = threading.Thread(target=task.run) #define a thread t for each task
                    t.start() #run the thread
                    threads.append(t) #stock the thread in the threads list
                    taskexcuted.append(task) #put the task in the list of tasks who are already launched
                    if task in tasknoorder: tasknoorder.remove(task) #remove the task that is excuted from tasknoorder if it is in that list

                #Once the loop is done with executing tasks which were ready to be executed we empty the list tasktobeexecuted
                tasktobexcuted = []
                
                #this loop while is used to wait for the threads to finish their execution (wait till all threads are no longer alive) to ge through the rest of the code
                while len(list(filter(lambda x: not x.is_alive(), threads))) != len(threads): pass 
                
                for t in tasknoorder : #this loop is used to extract tasks from task who are still not excuted and their dependencies has all alrady been executed
                    
                    # verify if all the dependencies of the task t are in the list of the executed tasks(tasksexecuted)
                    #if it is the cas we add it to tasks to be executed
                    if all(elem in list(map(lambda x: x.name, taskexcuted)) for elem in self.getDependancies(t.name)): 
                        tasktobexcuted.append(t)


#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   
    def draw(self): # this function is used to draw the paralell execution

        Graphe = Digraph(comment="Graphe d'exécution en parallèle", strict=True) # intialisation of  our graph
        taskwithnodep=[] # list to stock tasks with no dependencies
        taskwithdep=[] # list to stock tasks with dependencies
        if self.verification():

            for task in self.listtask:# this loop is used to go through all the system's tasks to extract tasks with no dependencies
                # verify if the task doesn't have dependencies and add them to the list of taskswithnodep
                if self.getDependancies(task.name) == []: taskwithnodep.append(task)

            for task in self.listtask: #this loop stock task having at least one dependency
                # we go through all tasks in the system and we keep only the ones who are not in taskwithdep
                if task not in taskwithnodep :
                    taskwithdep.append(task)

            for task in taskwithnodep: #this loop aims to draw all nodes of independent task  
                Graphe.node(task.name)

            drawn= taskwithnodep # stock drawn taks witout dependencies in drawn list
            
            while taskwithdep:#this loop is used to draw tasks who are are still not drawn as long as there's at least one
                            # task in taskwithdep (each time we draw one of it we romove it from teh list and move it to drawn list)

                todraw=taskwithdep # put the list taskwithdep in to draw

                for task in todraw: # for each task we check if its dependencies are drawn to draw it  
                    if all(elem in list(map(lambda x: x.name, drawn)) for elem in self.getDependancies(task.name)) :
                        for elem2 in self.getDependancies(task.name): # during this loop we check for each element (Task type) of the task 's dependencies 
                                                                    # if it's linked to another element so that we don't add useless eddges  
                            if len(self.getDependancies(task.name)) > 1: 
                                for elem3 in list(filter(lambda x : x != elem2 ,self.getDependancies(task.name)))  :
                                    if elem2 in self.getDependancies(elem3): pass # if the dependencies of the task are linked we don't create an edge 
                                    else:                                         #else we link them  
                                        Graphe.node(task.name)
                                        Graphe.edge(elem2, task.name)
                                        drawn.append(task)
                                        if task in taskwithdep: taskwithdep.remove(task)
                            else :
                                Graphe.node(task.name)
                                Graphe.edge(elem2, task.name)
                                drawn.append(task)
                                if task in taskwithdep: taskwithdep.remove(task)

                todraw=[]

            Graphe.format = 'png'
            Graphe.render('my_graph', view=True)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def verification(self):
        taskdup = set()
        verif = True
        for task in self.listtask: #  We check if there are duplicated tasks 
            if self.listtask.count(task) > 1:
                 taskdup.add(task)
                 verif = False
        for t in taskdup: print(t.name, ' Task is duplicated')

        for key in [*self.precedences]: # we check if our dictionnary contains inexisted tasks 
            if key not in list(map(lambda x: x.name, self.listtask)): 
                print('la tache ' + key + " n'exite pas (dans le dictionnaire)")
                verif = False

            for task in self.getDependancies(key): # we check for each task if its dependencies contain inexisted tasks 
                if task not in list(map(lambda x: x.name, self.listtask)): 
                    print("la taches " + task + " n'exite pas (dans la liste de précédence de " + key + " )")
                    verif = False

        listt = self.listtask
        for task1 in listt: # we check if there are tasks that depend of each other 
            for task2 in list(filter(lambda task: task != task1, listt)):
                if task1.name in self.getDependancies(task2.name) and task2.name in self.getDependancies(task1.name):
                    print("les deux taches " + task1.name + " " + task2.name + " l'une depend de l'autre")
                    listt.remove(task1)
                    verif = False
        return verif
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def interference(self, a, b): #conditons de Bernstein
            if not intersection(a.writes, b.reads) == [] or not intersection(a.reads, b.writes) == [] or not intersection(
                    a.writes, b.writes) == [] :
                return 'true'

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def intersection(list1, list2):
        list3 = [value for value in list1 if value in list2]
        return list3

#--------------------------------------------------------------------------------------MAIN Test------------------------------------------------------------------------------------------------------------

def runT1():
    global X
    X = 1
    print('this is task 1 : '+ str(X))
    sleep(5)

def runT2():
    global Y
    Y = 2
    print('this is task 2 : '+ str(Y))
    sleep(1)


def runT3():
    global X, Y, Z
    Z = X + Y
    print('this is task 3 : '+ str(Z))
    sleep(3)


def runT4():
    global X, Y, Z
    Z = X - Y 
    print('this is task 4 : '+ str(Z))
    sleep(3)


def runT5():
    print('this is task 5 ')
    sleep(6)


t1 = Task()
t1.name = "T1"
t1.writes = ["X"]
t1.run = runT1

t2 = Task()
t2.name = "T2"
t2.writes = ["Y"]
t2.run = runT2
t3 = Task()

t3.name = "T3"
t3.reads = ["X", "Y"]
t3.writes = ["Z"]
t3.run = runT3

t4 = Task()
t4.name = "T4"
t4.writes = ["X", "Y"]
t4.reads = ["Z"]
t4.run = runT4

t5 = Task()
t5.name = "T5"
t5.run = runT5



list1 = TaskSystem([t1, t2, t3, t4, t5],
                   {'T1': [], 'T2': ["T1"], 'T3': ["T1", "T2"], 'T4': ["T1", "T2"], 'T5': []})
                   

list2 = TaskSystem([t1, t1, t3, t4, t5], {'T1': [], 'T2': ["T1"], 'T3': ["T1", "T5"], 'T4': ["T1", "T2", "T3"], 'T5': []})

#---------------------------------------------------------------Test exécution séquentielle-------------------------------------------------------------------

'''start= time.perf_counter()
runT1()
runT5()
runT2()
runT3()
runT4()
finish= time.perf_counter()
print(f'Finished in {round(finish-start, 2)} seconds(s)')
start= time.perf_counter()
list1.Run()
finish= time.perf_counter()
print(f'Finished in {round(finish-start, 2)} seconds(s)')'''

#-----------------------------------------------------------------Test exécution avec parallélisation-------------------------------------------------------------

start= time.perf_counter()
list1.Run()
finish= time.perf_counter()
print(f'Finished in {round(finish-start, 2)} seconds(s)')
list1.draw()

#--------------------------------------------------------------------Test Erreur de validation---------------------------------------------------------------------

#list2.Run()
#list2.draw()
