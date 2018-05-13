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
from data import Unit, Texte, Campagne, Annotateur

AnnotationDirectory = "Campagne 2018"
projectDirectory = path.dirname(path.realpath(__file__))
projectDirectory = path.join(path.split(projectDirectory)[0])
textsNames = ["Bac_a_sable","Florence","Provocation"]
textDirectories = [path.join(projectDirectory,AnnotationDirectory,t) for t in textsNames]


def parsing(directories, id_unites_constants = False):
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
        
        soup = BeautifulSoup(unites, "lxml")
        
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

    ##### Parsing des annotations
        fichiers_annotations = glob.glob(path.join(directory, "Annotations\*.aa"))
        for f_annot in fichiers_annotations:
            nom_annotateur = path.basename(f_annot).rstrip(".aa")
            if not nom_annotateur in annotateurs:
                annotateurs[nom_annotateur] = Annotateur(nom_annotateur, camp)
            
            with open(f_annot, 'r', encoding="utf-8") as f :
                annotation = f.read()

            soup = BeautifulSoup(annotation, "lxml")

            #if not id_unites_constants:
                
            

parsing(textDirectories)