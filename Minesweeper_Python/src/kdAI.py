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

import random
from AI import AI
from Action import Action

from collections import deque


class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		

		self.__rowDimension = rowDimension
		self.__colDimension = colDimension
		self.__totalMines = totalMines
		self.coveredtotal = rowDimension * colDimension

		self.remainingFlags = self.__totalMines

		self.x = startX
		self.y = startY
		

		self.safe_tiles = deque() #list of COVERED tiles that are safe to UNCOVER
	
		self.adjcovered = set() #list of SURROUNDING covered tiles
		self.covered = set()
		self.uncovered = set() 


		self.flagged = set()
		self.mine = set()
		self.uncoverFlag = deque()
		self.needFlag = deque()

		self.revealed_numbers = dict()
		self.risk_dict = dict()
		
		if rowDimension >= colDimension:
			for x in range(rowDimension):
				for y in range(colDimension):
					self.risk_dict[(x, y)] = 0
					self.covered.add((x,y))
		else:
			for y in range(colDimension):
				for x in range(rowDimension):
					self.risk_dict[(x, y)] = 0
					self.covered.add((x,y))


	
	def getAction(self, number: int) -> "Action Object":
		if (number == 0):
			self.safetilesZero()
		if (number > -1):
			self.revealed_numbers[(self.x, self.y)] = number
		
		self.updateAdj(number)
		self.checkUncovered(list(self.uncovered))
		self.checkFlags()
		
		
		if self.needFlag and self.remainingFlags > 0:
			#print('flag')
			flag_tile = self.flagTile()
			return Action(AI.Action.FLAG, *flag_tile)
		elif self.uncoverFlag:
			#print('unflag')
			unflag_tile = self.unflagTile()
			if unflag_tile is not None:
				return Action(AI.Action.UNFLAG, *unflag_tile)
		elif self.safe_tiles:
			#print('safe tiles...')
			return Action(AI.Action.UNCOVER, *self.uncoverTile())
		else:
			if self.remainingFlags == 0 and self.coveredtotal == self.__totalMines:
				return Action(AI.Action.LEAVE)

			#print('newarea or random')
			random_tile = self.chooseRandom()
			new_area_tile = self.exploreNewArea()

			random_tile_risk = self.risk_dict.get(random_tile, float('inf'))
			new_area_tile_risk = self.risk_dict.get(new_area_tile, float('inf'))
			# if new_area_tile_risk == 0:
			# 	new_area_tile_risk += 1

			random_tile_score = random_tile_risk + self.calculateTileScore(random_tile)
			new_area_tile_score = new_area_tile_risk + self.calculateTileScore(new_area_tile)

			# Choose the tile with the lower risk
			if random_tile_score <= new_area_tile_score:
				#print('random')
				return Action(AI.Action.UNCOVER, *self.uncoverTile(*random_tile))
			else:
				#print('new')
				return Action(AI.Action.UNCOVER, *self.uncoverTile(*new_area_tile))
				

	"""Grid Checkers"""
	def calculateTileScore(self, tile):
		x, y = tile
		adjacent_uncovered = len([t for t in self.getAdj(x, y) if t in self.uncovered])
		adjacent_flags = len([t for t in self.getAdj(x, y) if t in self.flagged])
		
		# Example scoring function: higher score for tiles near uncovered or flagged tiles
		return adjacent_uncovered * 0.5 + adjacent_flags * 0.5
	
	def safetilesZero(self):
		for coord in self.getAdj():
				if (coord not in self.uncovered and coord not in self.safe_tiles):
					self.safe_tiles.appendleft(coord)
	def checkFlags(self):
		for flag in self.flagged:
			# Check all adjacent uncovered tiles of the flagged tile
			adj_tiles = self.getAdj(*flag)
			adj_uncovered = [t for t in adj_tiles if t in self.uncovered]
			for tile in adj_uncovered:
				number = self.revealed_numbers.get(tile)
				if number is not None:
					adj_tiles_of_tile = self.getAdj(*tile)
					flagged_adj = [t for t in self.flagged if t in adj_tiles_of_tile]
	
					# Mark tiles as needing unflagging if there are too many flags around a tile
					if len(flagged_adj) > number:
						self.uncoverFlag.extend([f for f in flagged_adj if f 
							   not in self.uncoverFlag and f in adj_tiles_of_tile])
	def unflagTile(self, x = None, y = None):
		self.uncoverFlag = set(self.uncoverFlag)
		if x is None or y is None: 
			if not self.uncoverFlag:
				return None
			self.uncoverFlag = deque(self.uncoverFlag)
			x, y = self.uncoverFlag.popleft()
		if (x, y) not in self.flagged:
			return None
		self.flagged.remove((x, y))
		self.remainingFlags += 1
		self.x, self.y = x, y
		return x, y

	def flagTile(self, x = None, y = None):
		if x is None or y is None: 
			if not self.needFlag:
				return None
			x, y = self.needFlag.popleft()
		if (x, y) in self.flagged:
			return None
		self.flagged.add((x, y))
		self.remainingFlags -= 1
		self.x, self.y = x, y
		return x, y

	def addFlag(self, flagList):
		for coord in flagList:
			self.needFlag.append(coord)

	def checkUncovered(self, tileList):
		for tile in tileList:
			if tile in self.uncovered:
				if self.revealed_numbers[tile] != 0:
					self.checkAdj(*tile)
	
	def checkAdj(self, x=None, y=None): #Checks the adjacent number to see if a flag can be placed
		if x is None or y is None: x,y = self.x, self.y

		adj = self.getAdj(x,y)
		current_num = self.revealed_numbers.get((x, y), 0)
		adj_flags = [t for t in adj if t in self.flagged]
		adj_covered = [t for t in adj if t in self.adjcovered]
		adj_uncovered = [t for t in adj if t in self.uncovered]
		adj_noflags = [t for t in adj if t not in self.flagged and t in adj_covered]

		# Flag tiles if they are certain mines based on the revealed number
		
		# Only add tiles to `needFlag` if certain they are mines
		if (len(adj_covered) + len(adj_flags) == current_num or \
	  			len(adj_noflags) + len(adj_flags) == current_num) and current_num > 0:
			for tile in adj_covered:
				if tile not in self.flagged and tile not in self.needFlag and tile not in self.safe_tiles:
					self.needFlag.append(tile)
		if current_num == len(adj_flags) and current_num > 0:
			if len(adj_covered) == len(adj_flags) or \
			len(adj_covered) == len(adj_flags) + len(adj_noflags): #+ len(adj_uncovered):
				
				for tile in adj_covered:
					if tile not in self.flagged and tile not in self.needFlag and tile not in self.safe_tiles:
						self.safe_tiles.append(tile)

	def manhattanDistance(self, tile1, tile2):
    # Calculate the Manhattan distance between two tiles
		return abs(tile1[0] - tile2[0]) + abs(tile1[1] - tile2[1])

	def exploreNewArea(self):
		unvisited_tiles = [tile for tile in self.covered if tile not in self.uncovered and tile not in self.flagged]
		min_risk_tiles = [tile for tile in unvisited_tiles if self.risk_dict[tile] == 0]
		if min_risk_tiles:
			return random.choice(min_risk_tiles)
		return random.choice(unvisited_tiles)
	
	def chooseRandom(self): #Choose the minimum from the SURROUNDING area
		covered_keys = [key for key in self.adjcovered if key not in self.flagged]
		min_value = min((self.risk_dict[key] for key in covered_keys), default=None)
		min_keys = [key for key in covered_keys if self.risk_dict[key] == min_value]
		x, y = random.choice(min_keys)
		return x, y	
	
	def uncoverTile(self, x = None, y = None):
		if x is None and y is None:
			x, y = self.safe_tiles.popleft()
		self.uncovered.add((x, y))
		self.adjcovered.discard((x, y))
		self.covered.discard((x,y))
		self.coveredtotal -= 1


		self.x, self.y = x, y
		return x, y
	
	"""Grid Getters """
	def getAdj(self, x= None, y=None):
		if x is None or y is None: x,y = self.x, self.y
		adj = [self.getUpper(x,y), self.getLower(x,y), self.getULD(x,y), self.getURD(x,y),
		 self.getL(x,y),self.getR(x,y), self.getLLD(x,y), self.getLRD(x,y)]
		
		valid_adj = [coord for coord in adj if self.checkCoords(*coord)]
		return valid_adj

	def addRisk(self, number, x, y):
		if (x, y) in self.risk_dict:
			self.risk_dict[(x, y)] = max(0, self.risk_dict[(x, y)] + number)

	def checkCoords(self, x, y):
		if (x < 0) or (y < 0):
			return False
		elif x > self.__rowDimension - 1:
			return False
		elif y > self.__colDimension - 1:
			return False
		else:
			return True

	def computeRisk(self, number, x, y):
		if self.checkCoords(x, y) == True:
			self.addRisk(number, x, y)
	
	def updateAdj(self, number,  x=None, y=None):
		if x is None or y is None: x,y = self.x, self.y
		for adjTile in self.getAdj(x, y):
			if adjTile in self.flagged:
				continue
			self.computeRisk(number, *adjTile)
			if adjTile not in self.uncovered:
				self.adjcovered.add(adjTile)
	"""COORDINATE HELPERS"""
	def getUpper(self, x=None, y=None):
		if x is None or y is None: x,y = self.x, self.y
		return (x, y + 1)
	def getLower(self,x=None, y=None):
		if x is None or y is None: x,y = self.x, self.y
		return (x, y - 1)
	def getULD(self,x=None, y=None):
		if x is None or y is None: x,y = self.x, self.y
		return (x - 1, y + 1)
	def getURD(self,x=None, y=None):
		if x is None or y is None: x,y = self.x, self.y
		return (x + 1, y + 1)
	def getL(self,x=None, y=None):
		if x is None or y is None: x,y = self.x, self.y
		return (x - 1, y)
	def getR(self,x=None, y=None):
		if x is None or y is None: x,y = self.x, self.y
		return (x + 1, y)
	def getLLD(self,x=None, y=None):
		if x is None or y is None: x,y = self.x, self.y
		return (x - 1, y - 1)
	def getLRD(self,x=None, y=None):
		if x is None or y is None: x,y = self.x, self.y
		return (x + 1, y - 1)