# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 19:02:46 2018

@author: Corentin
"""

import glob
from os import path
from bs4 import BeautifulSoup
import numpy as np
import pandas
from data import Unit, Texte, Campagne, Annotateur, Relation, Annotation, Theme
from analyse import *

def parsing(directories, id_unites_constants = False, experts=False):
    camp = Campagne()
    annotateurs = dict()

    for directory in directories:

    #### Parsing des unités
        
        ac_file = path.join(directory, "texte.ac")
        aa_file = path.join(directory, "unites.aa")
        
        with open(aa_file, "r", encoding="utf_8") as f :
            unites = f.read()
        
        with  open(ac_file, "r", encoding="utf_8") as f :
            text = f.read()
        
        soup = BeautifulSoup(unites, "html.parser")
        
        units_list = list()

        units = soup.findAll("unit")
        for unit in units:
            if unit['id'][:12] != 'TXT_IMPORTER': #Je sais pas à quoi les TXT_IMPORTER correspondent mais elles sont là et servent à rien
                debut = int(unit.start.singleposition['index'])
                fin = int(unit.end.singleposition['index'])
                nom = unit.find("feature", {"name":"Nom"}) #Pour chaque unité on a ajouté une feature "Nom" qu'on remplit avec le nom de l'unité (A1, B2_1, etc) donc on peut les récupérer directement
                if nom != None:
                    nom = nom.string
                if fin > debut:
                    u = Unit(unit['id'], debut, fin, text[debut:fin], nom)
                    units_list.append(u)

        units_list = sorted(units_list, key=lambda x:x.debut)
        nom_texte = path.basename(directory)
        t = Texte(nom_texte, text, units_list)
        camp.textes[nom_texte] = t

        id2units = dict()
        for u in units_list:
            id2units[u.id] = u
        
    ##### Parsing des annotations
        fichiers_annotations = glob.glob(path.join(directory, "Annotations/*.aa"))
        for f_annot in fichiers_annotations:
            nom_annotateur = path.basename(f_annot).rstrip(".aa")
            if  nom_annotateur != "expert" or experts:
                if not nom_annotateur in annotateurs:
                    annotateurs[nom_annotateur] = Annotateur(nom_annotateur, camp)
                
                f = open(f_annot, 'r', encoding="utf-8")
                annotation = f.read()
                f.close()
                soup = BeautifulSoup(annotation, "html.parser")

                if not id_unites_constants:
                    units_nulles = list()
                    units = soup.findAll("unit")
                    for unit in units:
                        if unit['id'][:12] != 'TXT_IMPORTER':
                            debut = int(unit.start.singleposition['index'])
                            fin = int(unit.end.singleposition['index'])
                            if fin > debut:
                                units_nulles.append((debut, unit['id']))

                    units_nulles = sorted(units_nulles, key=lambda x:x[0])
                    #Dans ce dict, on fait correspondre les ids (tous différents selon les fichiers) des unités aux Units qu'on a créé précédemment
                    id2units = dict()
                    i = 0
                    for u in units_nulles:
                        id2units[u[1]] = units_list[i]
                        i+=1
                
                #On peut enfin récupérer les relations à proprement parler
                rel_list = list()
                relations = soup.findAll("relation")
                for relation in relations:
                    extremites = relation.findAll("term")
                    rel = Relation(relation["id"], id2units[extremites[0]["id"]], id2units[extremites[1]["id"]], relation.type.string)
                    rel_list.append(rel)
                # name = path.basename(f_annot).split(".")[0]
                # annotateurs[nom_annotateur].annotations[nom_texte] = rel_list


                ### Récupération des thèmes
                themes_list = list()
                themes = soup.findAll("flag")
                previousLabel = ""
                for theme in themes:
                    position = int(theme.positioning.singleposition["index"])
                    label = theme.characterisation.comment.string
                    th = Theme(label, position, t)
                    if label != previousLabel : themes_list.append(th)
                    previousLabel = label
                annot = Annotation(annotateurs[nom_annotateur], camp, t, themes_list, rel_list)

                annotateurs[nom_annotateur].annotations[nom_texte] = annot
    
    camp.annotateurs = annotateurs
    return camp