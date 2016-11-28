# Import libraries
import random

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector
from agents import TreeCell, FireFighter

class ForestFire(Model):
    '''
    Simple Forest Fire model.
    '''
    def __init__(self, height, width, density, wind, ff_count, ff_vision, movement=True):
        '''
        Create a new forest fire model.
        
        Args:
            height, width: The size of the grid to model
            density: What fraction of grid cells have a tree in them.
            wind: Wind speed in MPH
            ff_count: # of firefighters 
        '''
        # Initialize model parameters
        self.height = height
        self.width = width
        self.density = density
        self.wind = wind
        self.ff_count = ff_count
        self.movement = movement
        self.ff_vision = ff_vision
        # Set up model objects
        self.schedule = RandomActivation(self)
        self.grid = Grid(height, width, torus=False)
        self.dc = DataCollector({"Fine": lambda m: self.count_type(m, "Fine"),
                                "On Fire": lambda m: self.count_type(m, "On Fire"),
                                "Burned Out": lambda m: self.count_type(m, "Burned Out")})
        self.running = True
        
        # Place a tree in each cell with Prob = density
        unique_id = 0
        for (contents, x, y) in self.grid.coord_iter():
            if random.random() < self.density:
                ## Create a tree
                new_tree = TreeCell(self, (x, y))
                # Set all trees in the first column on fire.
                if x == 0:
                    new_tree.condition = "On Fire"
                self.grid[x][y] = new_tree
                self.schedule.add(new_tree)
        # Place a firefighter in each cell with Prob = density
        y = random.randint(0, ff_count)
        for x in range(0,ff_count):
            # Add a firefighter
            new_ff = FireFighter(self, (x, y))
            # Place firefighter in grid cell
            self.grid.place_agent(new_ff, (x,y))
        
    def step(self):
        '''
        Advance the model by one step.
        '''
        self.schedule.step()
        self.dc.collect(self)
        # Halt if no more fire
        if self.count_type(self, "On Fire") == 0:
            self.running = False
    
    @staticmethod
    def count_type(model, tree_condition):
        '''
        Helper method to count trees in a given condition in a given model.
        '''
        count = 0
        for tree in model.schedule.agents:
            if tree.condition == tree_condition:
                count += 1
        return count