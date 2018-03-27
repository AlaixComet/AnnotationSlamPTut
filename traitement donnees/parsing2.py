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
from data import Unit, Texte


projectDirectory = path.dirname(path.realpath(__file__))
textsNames = ["Bac_a_sable","Florence","Provocation"]
directories = [projectDirectory+"\\textes\\"+t for t in textsNames]

camp = Campagne()

for directory in directories:

#### Parsing des unités
    
    ac_file = path.join(directory, "texte.ac")
    aa_file = path.join(directory, "unites.aa")
    
    f = open(aa_file, "r", encoding="utf_8")
    unites = f.read()
    f.close()
    
    f = open(ac_file, "r", encoding="utf_8")
    text = f.read()
    f.close()
    
    soup = BeautifulSoup(unites, "lxml")
    
    units_list = list()

    units = soup.findAll("unit")
    for unit in units:
        if unit['id'][:12] != 'TXT_IMPORTER': #Je sais pas à quoi les TXT_IMPORTER correspondent mais elles sont là et servent à rien
            debut = int(unit.start.singleposition['index'])
            fin = int(unit.end.singleposition['index'])
            nom = unit.find("feature", {"name":"Nom"}) #J'ai refait un fichier .aa comme j'ai expliqué donc dedans j'ai direct le nom des tours de parole !
            if nom != None:
                nom = nom.string
            if fin > debut:
                u = Unit(unit['id'], debut, fin, text[debut:fin], nom)
                units_list.append(u)

    units_list = sorted(units_list, key=lambda x:x.debut)
    nom = path.basename(directory)
    t = Texte(nom, text, units_list)
    camp.textes[nom] = t

##### Parsing des annotations
    
    