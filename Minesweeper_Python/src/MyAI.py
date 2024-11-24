# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

# python3 Main.pyc -f ../../WorldGenerator/Problems/
# python3 Main.pyc -d -f ../../WorldGenerator/Problems/Beginner_world_125.txt
# python3 Main.pyc -d -f ../../WorldGenerator/Problems/Intermediate_world_355.txt
# python3 Main.pyc -d -f ../../WorldGenerator/Problems/Expert_world_3.txt
from AI import AI
from Action import Action
import random

p = False

def check_print(*args, **kwargs):
    if p:
        print(*args, **kwargs)


class MyAI( AI ):
    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        self.__rowDimension = rowDimension
        self.__colDimension = colDimension
        self.__totalTiles = rowDimension * colDimension
        self.__valueX = startX
        self.__valueY = startY
        self.__totalMines = totalMines
        self.__toVisit = set()
        self.__checked = set()
        self.__mines = set()
        self.__minesDict = dict()
        self.__flag = set()
        self.__danger = set()

    def getAction(self, number: int):
        unvisited_tiles = [
                (x, y) for x in range(self.__colDimension) for y in range(self.__rowDimension)
                if (x, y) not in self.__checked and (x, y) not in self.__mines
            ]
        
        if len(self.__checked) + len(self.__mines) == self.__totalTiles:
            #leave when the number of checked and the number of mines are equal to total number of tiles
            return Action(AI.Action.LEAVE)
        
        if len(self.__flag) == self.__totalMines:
            #found all flag -> the rest are safe
            for t in unvisited_tiles:
                self.__toVisit.add(t)
            
        self.__checked.add((self.__valueX, self.__valueY))

        if number > 0:
            self.__minesDict[(self.__valueX, self.__valueY)] = number
        
        check_print("toVisit: ", self.__toVisit)

        self.getNewSafeCoordinate()
        check_print("Mines: ", self.__mines)

        # add code here

        safe = self.checkSafe(self.__valueX, self.__valueY, number) #add safe coord to toVisit when it's 0)

        for new_x, new_y in safe:
            if (new_x, new_y) not in self.__checked and (new_x, new_y) not in self.__mines:
                self.__toVisit.add((new_x, new_y))

        if (len(self.__flag) != len(self.__mines)) and not self.__toVisit:
            # continue flagging if there are still flags
            diff = self.__mines.difference(self.__flag)
            if diff:
                flag_x, flag_y = diff.pop()
                self.__flag.add((flag_x, flag_y))
                #check_print(self.__flag)
                return Action(AI.Action.FLAG, flag_x, flag_y)

        if self.__toVisit:
            self.__valueX, self.__valueY = self.__toVisit.pop() #get the new coordinates from toVisit for the next action
        else:
            check_print("RANDOM TIME")
            if unvisited_tiles:
                self.__valueX, self.__valueY = random.choice(unvisited_tiles)
        return Action(AI.Action.UNCOVER, self.__valueX, self.__valueY)
   
    def getNeighbors(self, x, y):
        neighbors = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i != 0 or j != 0:
                    new_x, new_y = x + i, y + j
                    if 0 <= new_x < self.__colDimension and 0 <= new_y < self.__rowDimension:
                        neighbors.append((new_x, new_y))
        return neighbors

    def checkMines(self, x, y, number):
        neighbors = self.getNeighbors(x, y)
        filtered = []
        for n in neighbors:
            if n not in self.__checked:
                filtered.append(n)
        if len(filtered) == number:
            for new_x, new_y in filtered:
                self.__mines.add((new_x, new_y))
            return filtered
        return []

    def checkSafe(self, x, y, number):
        neighbors = self.getNeighbors(x, y)
        #return the coordinates of the mines
        mines = [n for n in neighbors if n in self.__mines]
        if len(mines) == number:
            # the rest will be safe
            safe = []
            for n in neighbors:
                if n not in mines and n not in self.__checked and n not in self.__toVisit:
                    safe.append(n)
            return safe
        return []

    def getNewSafeCoordinate(self):
        safe = []
        for (x, y), value in self.__minesDict.items():
            self.checkMines(x, y, value)
            safes = self.checkSafe(x, y, value)
            if safes:
                safe.extend(safes)

        for new_x, new_y in safe:
            if (new_x, new_y) not in self.__checked and (new_x, new_y) not in self.__mines:
                self.__toVisit.add((new_x, new_y))

    def checkSurrounding(self):
        pass


