# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 11:19:05 2018

@author: Corentin
"""
import numpy as np
import pandas
from graphviz import Digraph


class Campagne():
    """
    Contient toutes les informations nécesaires pour la campagne d'annotation.
        textes : dict qui à chaque nom de texte associe le Texte correspondant
        typesRelations : dict qui à chaque nom de relation associe son type (verticale ou horizontale)
        annotateurs : dict qui à chaque id associe un annotateur
        infosAnnotateurs : pandas.DataFrame le tableau csv des ages, CSP etc
    """
    def __init__(self):
        self.textes = dict()
        self.typesRelations = dict()
        self.annotateurs = dict()
        self.infosAnnotateurs = None
    

class Texte():
    """
    Représente un texte proposé à l'annotation
        nom : String le nom du texte
        texte : String le contenu du texte (comme formaté dans le fichier .ac)
        unites : list des unites du texte (dans l'ordre du texte)
    """
    def __init__(self, nom, texte, unites):
        self.nom = nom
        self.texte = texte
        self.unites = unites
        

class Annotateur():
    """
    Représente un participant à la campagne et ses annotations
        id : String l'id de l'annotateur
        annotations : dict qui à chaque nom de texte associe les annotations
        campagne : Campagne référence vers la campagne où participe l'annotateur
    """
    def __init__(self, id, campagne):
        self.id = id
        self.annotations = dict()
        self.campagne = campagne
    
    def getInfos(self):
        """
        Retourne la ligne du DataFrame correspondant aux données de l'annotateur
        """
        return self.campagne.infosAnnotateurs[self.id]
    
    
class Unit():
    """
    Représente une unité d'un texte
        id : String identifiant Glozz de l'unité
        debut : int indice de début
        fin : int indice de fin
        txt : String contenu de l'unité
        name : nom court de l'unité (de la forme A1, B2_1, B2_2 etc.)
    """
    def __init__(self, id_unit, debut, fin, txt, name):
        self.id = id_unit
        self.debut = debut
        self.fin = fin
        self.txt = txt
        self.name = name
        
    def __str__(self):
        return self.name 
    
    __repr__ = __str__
    
    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.id == other.id
        else:
            return False


class Relation():
    """
    Représente une relation entre deux unités d'un texte
        id : String identifiant Glozz de la relation
        origine : Unit unité dont part la relation (celle du bas donc)
        dest : Unit unité où arrive la relation (plus haut dans le texte donc)
        type : String type de relation {Narration, Phatique, ...}
    """
    def __init__(self, id_rel, debut, fin, type_rel):
        self.id = id_rel
        self.origine = debut #Unit
        self.dest = fin #Unit
        self.type = type_rel #"Narration" etc.
        
    def __str__(self):
        return self.id + " = " + self.origine.name + " --" + self.type + "--> "+self.dest.name
    __repr__ = __str__


class Theme():
    """
    Thème associé à une partie d'un texte
        label : String nom du thème
        debut : int indice du début du thème
    """
    def __init__(self, label, debut):
        self.label = label
        self.debut = debut


class Annotation():
    """
    Annotation d'un texte par un annotateur (expert ou non)
        annotateur : Annotateur ayant produit cette annotation
        campagne : Campagne
        texte : Texte texte sur lequel porte l'annotation
        themes : list de Theme
        relations : list de Relation
    """
    def __init__(self, annotateur, campagne, texte, themes, relations):
        self.annotateur = annotateur
        self.texte = texte
        self.themes = themes
        self.relations = relations
    
    def matrice(self):
        """
        Retourne la liste des relation sous forme de pandas.Panel (matrice 3D) 
        binaire. La première dimension correspond au type de relation, la deuxième
        à l'origine de la relation et la troisième à sa destination.
        """
        tab = np.zeros((len(self.annotateur.campagne.typesRelations), len(self.texte.unites), len(self.texte.unites)),  dtype="int")
        nomsUnites = [u.name for u in self.texte.unites]
        #Les Panels c'est des matrices 3D. L'avantage c'est qu'on peut nommer les colonnes ! 
        panel = pandas.Panel(tab, self.annotateur.campagne.typesRelations.keys(), nomsUnites, nomsUnites) 
        for rel in self.relations:
            if rel.type is not None and rel.dest.name is not None and rel.origine.name is not None:
                panel.loc[rel.type, rel.dest.name, rel.origine.name] = 1
        return panel
    
    def arbre(self):
        """
        Retourne l'Arbre correspondant à la structure des relations.
        """
        debut = self.texte.unites[0]
        return self.__makeTree(debut)
    
    def __makeTree(self, debut):
        """
        Fonction récursive pour construire l'arbre à partir d'une unité de départ
            debut : Unit
        """
        filsHoriz = list() #liste d'Units
        filsVert = list() # liste d'Units
        for r in self.relations:
            if r.dest == debut:
                if self.annotateur.campagne.typesRelations[r.type] == "horizontale":
                    filsHoriz.append((r.origine, r.type))
                else:
                    filsVert.append((r.origine, r.type))
        
        #On fait des paires (Noeud, typeRelation)
        noeudsFilsHoriz = [(self.__makeTree(f[0]), f[1]) for f in filsHoriz]
        noeudsFilsVert = [(self.__makeTree(f[0]), f[1]) for f in filsVert]
        
        return Arbre(debut, noeudsFilsHoriz, noeudsFilsVert)
    
    def dessinerArbre(self):
        dot = Digraph()
        units_names = list()
        for u in self.texte.unites:
            dot.node(u.name, u.name + " : " + u.txt)
            units_names.append(u.name)
        typesRel = self.annotateur.campagne.typesRelations
        for rel in self.relations:
            if typesRel[rel.type] == "horizontale":
                with dot.subgraph() as sub:
                    sub.attr(rank="same")
                    sub.node(rel.dest.name)
                    sub.node(rel.origine.name)
                    sub.edge(rel.dest.name, rel.origine.name, label=rel.type, dir="none")
            else:
                dot.edge(rel.dest.name, rel.origine.name, label=rel.type, dir="none")


class Arbre():
    """
    L'arbre des relations d'une annotation.
        racine : Unit l'unité au sommet de l'arbre
        filsHoriz : list de paires (Arbre fils, String typeRelation)
        filsVert : list de paires (Arbre fils, String typeRelation)
    Je ne sais pas si c'est utile de séparer les 2 comme ça ou pas.
    """
    def __init__(self, racine, filsHoriz, filsVert):
        self.racine = racine
        self.filsHoriz = filsHoriz
        self.filsVert = filsVert
