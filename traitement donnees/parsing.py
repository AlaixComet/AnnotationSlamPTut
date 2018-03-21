# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 15:27:15 2018

@author: Corentin
"""
import glob
from os import path
from bs4 import BeautifulSoup
from unit import Unit
from relation import Relation
import numpy as np
import pandas

"""============================================================================
Lecture des fichiers
============================================================================"""
#Pour l'instant il faut saisir le chemin à la main (oui c'est dégueu)
#Je considère que dans le dossier Bac_a_sable il y a un fichier texte.ac, un fichier unites.aa et ensuite les sous-dossiers avec les fichiers .aa des gens

directory = path.dirname(path.realpath(__file__))
textsNames = ["Bac_a_sable","Florence","Provocation"]
directories = [directory+"\\textes\\"+t for t in textsNames]

directory = directories[0]

ac_file = path.join(directory, "texte.ac")
aa_file = path.join(directory, "unites.aa")

f = open(aa_file, "r", encoding="utf_8")
unites = f.read()
f.close()

f = open(ac_file, "r", encoding="utf_8")
text = f.read()
f.close()

soup = BeautifulSoup(unites, "lxml")


"""============================================================================
On récupère la liste des unités depuis le fichier aa des unités
============================================================================"""
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
            print(u)
            units_list.append(u)

#Vu que pour l'instant dans leurs fichiers c'est le cirque on est obligés de passer par la position des unités dans le texte, 
#Mais si on arrive à faire comme on veut on pourra directement y accéder par leur id (ou nom)
units_list = sorted(units_list, key=lambda x:x.debut)



"""============================================================================
On récupère les annotations de chaque gens
============================================================================"""
annotations = {}

files = glob.glob(path.join(directory, "*\*.aa")) #liste de tous les fichiers .aa
for file in files:
    print(path.basename(file))
    f = open(file, "r", encoding="utf-8")
    annotation = f.read()
    f.close()
    
    soup = BeautifulSoup(annotation, "lxml") 
    
    rel_list = list()
    
    #Comme leurs données ne correspondent pas on récupère toutes les unités du texte et on les trie pour retrouver à quelle unité elle correspond
    #Si on fait comme on veut cette étape ne sera pas nécessaire car on aura directement l'id de l'unité (la même pour tous les fichiers)
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
    equivalence_unites = {}
    i = 0
    for u in units_nulles:
        equivalence_unites[u[1]] = units_list[i]
        i+=1
    
    
    #On peut enfin récupérer les relations à proprement parler
    relations = soup.findAll("relation")
    for relation in relations:
        extremites = relation.findAll("term")
        rel = Relation(relation["id"], equivalence_unites[extremites[0]["id"]], equivalence_unites[extremites[1]["id"]], relation.type.string)
        rel_list.append(rel)
    name = path.basename(file).split(".")[0]
    annotations[name] = rel_list
    
    

"""
J'ai commencé à essayer de transformer les listes de relations en matrices 3D :
    - 1ère dimension : type de relation (Conduite, Question etc)
    - 2ème dimension : unité dont part la relation (nom court (A1, B1_1 etc))
    - 3ème dimension : unité où arrive la relation

S'il y a une Narration entre B2 et B1 par exemple je mets un 1 dans la case correspondante.

Après l'idée ce serait par exemple de faire la somme des matrices de tous les gens pour voir s'il y a des endroits où tout le monde a coché pareil ou pas.
Dans cette matrice somme, on peut aussi la ramener à une matrice 2D en faisant la somme selon la première dimension, pour avoir le nombre de relations enrte A1 et A2 indépendamment de leur type
J'ai pas d'autres idées pour l'instant
"""   

annotations_panels = list()
    
types_relations = ["Conduite", "Contre-élaboration", "Elaboration descriptive", "Elaboration evaluative", "Elaboration prescriptive", "Méta-question", "Narration", "Phatique", "Question", "Réponse", "Réponse phatique"]

for a in annotations.values():
    tab = np.zeros((len(types_relations), len(units_list), len(units_list)),  dtype="int")
    units_names = [u.name for u in units_list]
    #Les Panels c'est des matrices 3D. L'avantage c'est qu'on peut nommer les colonnes ! 
    panel = pandas.Panel(tab, types_relations, units_names, units_names) 
    for rel in a:
        if rel.type is not None and rel.dest.name is not None and rel.origine.name is not None:
            panel[rel.type][rel.dest.name][rel.origine.name] = 1
    annotations_panels.append(panel)
    
print(annotations_panels[0]["Narration"])

total = annotations_panels[1].copy()

for pan in annotations_panels[1:]:
    total = total.add(pan)

print(total.sum(0)) #on affiche le total toutes relations confondues


#On explore ceux qui ont beaucoup de croix
#total.major_xs("A1").loc["Début"] #Le détail des relations de A1 vers Début

#total.major_xs("A2").loc[["A1","B1"]].transpose()



from graphviz import Digraph
def draw_global_tree(matrice, nom, nbAnnotations, minOccurrences=1):
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
                    dot.edge(dest, origine, label=label, penwidth=str(poids), color=str(i), colorscheme="paired11", dir="back")
    return dot

#draw_global_tree(total, "test", 27, 4)
