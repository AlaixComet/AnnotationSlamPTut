# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 16:38:16 2018

@author: Corentin
"""

class Unit():
    def __init__(self, id_unit, debut, fin, txt, name=""):
        self.id = id_unit
        self.debut = debut #indice du début
        self.fin = fin #indice de la fin
        self.txt = txt
        self.name = name
        
    def __str__(self):
        return self.name
    
    __repr__ = __str__