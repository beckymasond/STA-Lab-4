import random
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector

class TreeCell(Agent):
    '''
    A tree cell.
    
    Attributes:
        x, y: Grid coordinates
        condition: Can be "Fine", "On Fire", or "Burned Out"
        unique_id: (x,y) tuple. 
    
    unique_id isn't strictly necessary here, but it's good practice to give one to each
    agent anyway.
    '''
    def __init__(self, model, pos):
        '''
        Create a new tree.
        Args:
            pos: The tree's coordinates on the grid. Used as the unique_id
        '''
        super().__init__(pos, model)
        self.breed = 'Tree'
        self.pos = pos
        self.unique_id = pos
        self.condition = "Fine"
        
    def step(self):
        '''
        If the tree is on fire, spread it to fine trees nearby.
        If wind speed is under 13, only immediate neighbors with a common edge catch fire.
        If wind speed is 13-31, all neighbors in Moore's neighborhood catch fire.
        If wind speed is 32 or greater, all Moore's neighbors within a radius of 2 squares catch fire.
        '''
        if self.condition == "On Fire":
            if 13 <= self.model.wind < 32: 
                neighbors = self.model.grid.get_neighbors(self.pos, moore=True)
            elif self.model.wind >= 32:
                neighbors = self.model.grid.get_neighbors(self.pos, radius=2, moore=True)
            else:
                neighbors = self.model.grid.get_neighbors(self.pos, moore=False)
            for neighbor in neighbors:
                try:
                    if neighbor.condition == "Fine":
                        neighbor.condition = "On Fire"
                except:
                    pass
            self.condition = "Burned Out"

class FireFighter(Agent):
    '''
    A firefighter agent that puts out trees on fire.

    Attributes:
        x, y: Grid coordinates
    '''
    def __init__(self, model, pos):
        '''
        Create a firefighter.
        '''
        super().__init__(pos, model)
        self.breed = 'firefighter'
        self.pos = pos
        
    def step(self):
        '''
        If neighbor is a tree On Fire, change it to Fine.
        Ignore all other neighbors.
        ''' 
        self.update_neighbors()
        active_neighbors = []
        for agent in self.neighbors:
            if agent.breed == 'Tree' and \
                    agent.condition == 'On Fire':
                active_neighbors.append(agent)
        if active_neighbors:
            protected = active_neighbors
            protected.condition = "Fine"
        if self.model.movement:
            new_pos = random.choice(self.neighbors)
            self.model.grid.move_agent(self, new_pos)

    def update_neighbors(self):
        """
        Look around and see who my neighbors are.
        """
        self.neighborhood = self.model.grid.get_neighborhood(self.pos,
                                                        moore=True, radius=1)
        self.neighbors = self.model.grid.get_cell_list_contents(self.neighborhood)
        self.empty_neighbors = [c for c in self.neighborhood if
                                self.model.grid.is_cell_empty(c)]