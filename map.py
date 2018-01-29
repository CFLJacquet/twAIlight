from collections import defaultdict

class Map(object):

    
    def __init__(self, size):
        self.content = defaultdict(tuple) # Exemple : {(0, 0): (4, 'W')} ,ie en 0,0 il y a 4 Werewolves.
        self.size = size
    