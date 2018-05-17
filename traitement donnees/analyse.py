# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 19:16:56 2018

@author: Corentin
"""
import numpy as np
import scipy
from data import Annotation, Annotateur, Campagne, Theme
from graphviz import Digraph


def distance(mat1, mat2):
    mat1 = mat1.sum(0) #on fait abstraction du type de relation pour l'instant
    mat2 = mat2.sum(0)
    
    #On fait un grand vecteur
    mat1 = mat1.as_matrix().reshape(-1)
    mat2 = mat2.as_matrix().reshape(-1)
    
    return scipy.spatial.distance.hamming(mat1,mat2)

        
def matriceSansType(matrice3d):
    """
    Aplatit la matrice 3d de relations d'une anotation en une matrice 2d où on ne tient plus compte du type des relations mais seulement des unités qu'elles relient
    matrice3d : pandas.Panel
    return : pandas.Dataframe
    """
    return matrice3d.sum(0)

def matriceAvecCategories(matrice3d, categories):
    """
    Transforme la matrice 3d des relations en une liste de matrices 2d par catégorie
    matrice3d : pandas.Panel
    categories : list 2d de strings : [["Question","Méta-question"],["Elaboration descriptive"]]...
    return : list de pandas.Dataframe
    """
    res = list()
    for categ in categories:
        matrice = matrice3d[categ[0]].copy()
        for typeRel in categ[1:]:
            matrice = matrice.add(matrice3d[typeRel])
        res.append(matrice)
    return res


def detectionChangementTheme(annotation = Annotation):
    """
    args    : Annotation
    return  : list d'Unit
    """
    unitList = annotation.texte.unites
    previousT = Theme("null",1)
    unitsThemeChanges = list()
    for key, t in enumerate(annotation.themes) :
        if previousT.label != t.label :
            annotation.themes[key] = t.linkToUnit(unitList)
            unitsThemeChanges.append(annotation.themes[key].unite)
        previousT = t
    return(unitsThemeChanges)

def ruptureDeLaFrontiereDroite(annotation):
    """
    parcours postfixe
    """
    #TODO

def draw_global_tree(campagne, text, minOccurrences=1):
    """

    """
    dot = Digraph(name=text.nom, format="png")
    units_names = list()
    matrice = sommeMatrices(campagne,text)
    annotationList = campagne.getAnnotationListFromText(text)
    nbAnnotations = len(annotationList)
    for u in text.unites:
        dot.node(u.name, u.name + " : " + u.txt)
        units_names.append(u.name)
    i = 0
    for rel in list(campagne.typesRelations.keys()):
        i += 1
        for dest in units_names:
            for origine in units_names:
                val = matrice[rel][dest][origine]
                if val >= minOccurrences:
                    label = rel+"\n"+str(val)
                    poids = (val / nbAnnotations) * 10
                    dot.edge(dest, origine, label=label, penwidth=str(poids), color=str(i), colorscheme="paired11", dir="back") #dir back car no fait pas un arbre à proprement parler
    
    return dot

def save(matrice, nom, nbAnnotations, minOccurrences=1):
    """

    """
    dot = Digraph(name=nom, format="png")
    units_names = list()
    for u in units_list:
        dot.node(u.name, u.name + " : " + u.txt)
        units_names.append(u.name)
    i = 0
    for rel in types_relations:
        i += 1
        for dest in units_names:
            for origine in units_names:
                val = matrice[rel][dest][origine]
                if val >= minOccurrences:
                    label = rel+"\n"+str(val)
                    poids = (val / nbAnnotations) * 10
                    dot.edge(dest, origine, label=label, penwidth=str(poids), color=str(i), colorscheme="paired11", dir="back") #dir back car no fait pas un arbre à proprement parler
    
    return dot

def calculKappa():
    """

    """
    #TODO