# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 22:12:27 2018

@author: Corentin
"""

class Relation():
    def __init__(self, id_rel, debut, fin, type_rel):
        self.id = id_rel
        self.origine = debut #Unit
        self.dest = fin #Unit
        self.type = type_rel #"Narration" etc.
        
    def __str__(self):
        return self.id + " = " + self.origine.name + " --" + self.type + "--> "+self.dest.name
    
    __repr__ = __str__