# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 19:16:56 2018

@author: Corentin
"""
import numpy as np
import scipy
from data import Annotation, Annotateur, Campagne, Theme

def distance(mat1, mat2):
    mat1 = mat1.sum(0) #on fait abstraction du type de relation pour l'instant
    mat2 = mat2.sum(0)
    
    #On fait un grand vecteur
    mat1 = mat1.as_matrix().reshape(-1)
    mat2 = mat2.as_matrix().reshape(-1)
    
    return scipy.spatial.distance.hamming(mat1,mat2)

        
def sommeMatricesCampagne(campagne, l = []):
    """

    """
    #TODO

def detectionChangementTheme(annotation):
    """
    arg     : Annotation 
    return  : list d'Unit
    """
    #TODO

def ruptureDeLaFrontiereDroite(annotation):
    """
    parcours postfixe
    """
    #TODO

def dessinerGraphThemes():
    """

    """
    #TODO

def calculKappa():
    """

    """
    #TODO