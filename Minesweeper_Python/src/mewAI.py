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

from AI import AI
from Action import Action
from collections import defaultdict
import random

test = False

def makeBoard(rows, cols):
	'''
	Makes a list of list of size rows x cols to represent board.
	'''
	board = list()
	for i in range(rows):
		board.append([9]*cols)
	return board
	
def checkWin_old(potential_bombs):
	'''
	Checks for any potential bombs
	'''
	count = defaultdict(int)
	nums = len(potential_bombs)
	# freq = [[] for i in range(nums)]

	for i in potential_bombs:
		count[i] += 1 
		if count[i] > 4:
			print('bomb definitely!')
			return i
	
	res = sorted(count.items(), reverse=True, key=lambda x: x[1])		
	return res[0]
	# res = sorted(count.items(), reverse=True, key=lambda x: x[1])
	# return [c[0] for c in res[:k]]

class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		self.__board = makeBoard(rowDimension, colDimension) # 0 = no info
		self.__rowDimension = rowDimension
		self.__colDimension = colDimension
		self.__moveCount = 0
		self.__mines = totalMines
		self.__startX = startX
		self.__startY = startY
		self.__bombCoords = set() # list of bombs found
		self.__frontier = [] # frontier aka safe nodes to explore next
		self.__potentialBomb = [] # where potential bombs are placed aka unsafe list
		self.__visited = [] # where safe, uncovered nodes are placed
		self.__border = [] # where safe, non-zero tiles are placed
		self.__bombsToFlag = [] # bombs found, time to flag
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

		
	def getAction(self, number: int) -> "Action Object":
		'''
		Gets input from game (number) and returns action to do on board.
		
		number: # of neighboring bombs OR -1 if flag/unflag
		'''
		
		self.__board[self.__startY][self.__startX] = number
		self.__visited.append((self.__startX, self.__startY))
		
		if self.__bombsToFlag: # prioritize check wins
			self.__mines -= 1
			self.__startX, self.__startY = self.__bombsToFlag.pop()
			self.__bombCoords.add((self.__startX, self.__startY))
			return Action(AI.Action.FLAG, self.__startX, self.__startY) # flag bomb
		
		if self.__mines == 0:
			for y in range(self.__rowDimension):
				for x in range(self.__colDimension):
					if self.__board[y][x] == 9: # if not bomb and not checked, check 'em all
						self.__startX, self.__startY = x, y
						return Action(AI.Action.UNCOVER, self.__startX, self.__startY)
			return Action(AI.Action.LEAVE)
		
		# now we know if self X and Y are safe!
		neighbors, unknown, bombsFound = self.countNeighbors(self.__startX, self.__startY)
		
		if number: # number = 1
			# add (X, Y) neighbors to unsafe list
			self.__border.append((self.__startX, self.__startY))
			self.__potentialBomb.extend(neighbors)
			self.__border = list(set(self.__border))
			self.__potentialBomb = list(set(self.__potentialBomb))
		else: # number = 0
			# add neighbors to frontier
			self.__frontier.extend(neighbors)
			self.__frontier = list(set(self.__frontier))
			
		
		
		if test:
			print('frontier2 :', self.__frontier)
			
		while self.__frontier:
			self.__startX, self.__startY = self.__frontier.pop() # get a safe coord
			return Action(AI.Action.UNCOVER, self.__startX, self.__startY)
		
		if not self.__frontier: # if no more safe tiles to uncover, check for 
			self.findBombs()
			
			if self.__frontier or self.__bombsToFlag: # if some tiles added to safe/bombs list
				return self.getAction(number)
			elif self.__rowDimension > 10:
				self.findHardBombs()
						self.__startX = random.randrange(self.__colDimension)
			self.__startY = random.randrange(self.__rowDimension)
			
			for i in range(20):
				if (self.__startX, self.__startY) not in (self.__potentialBomb, self.__visited):
					return Action(AI.Action.UNCOVER, self.__startX, self.__startY) # if not in potential, run
				else:
					self.__startX = random.randrange(self.__colDimension) # if in pot unsafe, randomize
					self.__startY = random.randrange(self.__rowDimension)
					
		return Action(AI.Action.LEAVE)
		
		
	def validCoord(self, X, Y):
		'''
		Checks if X and Y are valid coordinates within board.
		'''
		return (X < self.__colDimension and X > -1) and (Y < self.__rowDimension and Y > -1)
		
		
	def countNeighbors(self, x, y):
		'''
		Returns unknown neighboring tiles, their count, and number of bombs found in vicinity.
		'''
		neighbors = list()
		unknown = 0
		bombsFound = 0
		
		for i in range(3):
			for j in range(3):
				coord = (x-1+i, y-1+j)
				if (i != 1 or j != 1) and self.validCoord(coord[0], coord[1]):
					if (coord not in self.__frontier) and (coord not in self.__visited):
						unknown += 1	
						neighbors.append(coord)
					elif self.__board[coord[1]][coord[0]] == -1:
						bombsFound += 1
		
		return (neighbors, unknown, bombsFound)

	
	def findBombs(self): # need to find way to update neighbors :(((
		'''
		Checks number of bombs and unknown tiles arond border to determine flag/uncover moves.
		'''
		remove = set()

		for tile in self.__border:
			neighbors, unknown, bombsFound = self.countNeighbors(tile[0], tile[1])
			if test:
				print(f"COUNT NEIGHBORS of {tile} with {self.__board[tile[1]][tile[0]]}: {neighbors}, {unknown}, {bombsFound}")

			if unknown == 0 or self.__board[tile[1]][tile[0]] == -1:
				remove.add(tile) # no neighbors to uncover
			elif unknown == (self.__board[tile[1]][tile[0]] - bombsFound):
				# flagall cos all neighbors bombs
				self.__bombsToFlag.extend(neighbors)
				self.__bombsToFlag = list(set(self.__bombsToFlag))
				remove.add(tile)
			elif bombsFound == self.__board[tile[1]][tile[0]]:
				# uncoverall cos all bombs found, all unknown neighbors safe
				self.__frontier.extend(neighbors)
				remove.add(tile)
				
		for coord in remove:
			self.__border.remove(coord) # update border
	
	def findHardBombs(self):
		for tile in self.__border:
			pass
