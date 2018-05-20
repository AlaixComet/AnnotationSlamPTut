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

from sklearn.metrics import cohen_kappa_score
def calculKappa(annotation1, annotation2):
    """
    http://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html
    https://stackoverflow.com/questions/43676905/how-to-calculate-cohens-kappa-coefficient-that-measures-inter-rater-agreement?rq=1&utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    on calcule 3 kappa à partir des 3 représentations sous forme de liste de deux annotations d'un même texte
    args : 2 Annotations
    returns : list of 3 float, result of 3 cohen_kappa_score
    """
    listA1 = annotation1.getArrayRepresentationForKappa()
    listA2 = annotation2.getArrayRepresentationForKappa()
    ListKappa = []
    for i in range(0,len(listA1)):
        ListKappa.append(cohen_kappa_score(listA1[i],listA2[i]))
    return ListKappa
