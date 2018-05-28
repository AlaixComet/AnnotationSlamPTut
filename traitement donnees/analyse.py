# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 19:16:56 2018

@author: Corentin
"""
import numpy as np
import scipy
from scipy import stats
from data import Annotation, Annotateur, Campagne, Theme
from graphviz import Digraph
import pandas
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.metrics import cohen_kappa_score
import itertools



def distance(mat1, mat2):
    mat1 = mat1.sum(0) #on fait abstraction du type de relation pour l'instant
    mat2 = mat2.sum(0)
    
    #On fait un grand vecteur
    mat1 = mat1.as_matrix().reshape(-1)
    mat2 = mat2.as_matrix().reshape(-1)
    
    return scipy.spatial.distance.hamming(mat1,mat2)

        
def matriceSansType(matrice3d):
    """
    Aplatit la matrice 3d de relations d'une anotation en une matrice 2d où on ne tient plus compte du type des relations mais seulement des unités qu'elles relient.
    Cette matrice 2d est encapsulée dans une matrice 3d (avec une seule couche en profondeur) pour la compatibilité avec d'autres fonctions.
    matrice3d : pandas.Panel
    return : pandas.Panel
    """
    matrice = matrice3d.sum(0).as_matrix()
    matrice = np.expand_dims(matrice, 0) #On rajoute une dimension en première position
    return pandas.Panel(matrice, [0], matrice3d.major_axis, matrice3d.minor_axis)

def matriceAvecCategories(matrice3d, categories):
    """
    Transforme la matrice 3d des relations en une matrice 3d par catégorie
    matrice3d : pandas.Panel
    categories : dict String : list de String
    return : pandas.Panel
    """
    matrices = list()
    nomsCateg = list()
    for nom, rels in categories.items():
        nomsCateg.append(nom)
        matrice = matrice3d[rels[0]].as_matrix()
        for typeRel in rels[1:]:
            matrice = matrice + matrice3d[typeRel].as_matrix()
        matrices.append(matrice)
    matrice = np.stack(matrices, axis=0)
    return pandas.Panel(matrice, nomsCateg, matrice3d.major_axis, matrice3d.minor_axis)


def ruptureDeLaFrontiereDroite(annotation):
    """
    parcours postfixe
    """
    pass
    #TODO

def draw_global_tree(campagne, nomTexte, regroupement="aucun", seuilAffichage=0.05, montrerThemes=True):
    """
    campagne : Campagne
    nomTexte : String
    type : String dans ['aucun', 'catégorie', 'emplacement']
    """
    categories = categories = {"Narration":["Narration"], "Elaborations":["Elaboration descriptive", "Elaboration evaluative", "Elaboration prescriptive", "Contre-élaboration", "Réponse"], "Méta": ["Conduite","Phatique", "Méta-question"], "Question":["Question"]}
    dot = Digraph(name=nomTexte, format="svg", node_attr={'shape':'box','style':'filled'})
    
    annotations = campagne.getAnnotations(nomTexte)
    texte = campagne.textes[nomTexte]

    units_names = [u.name for u in texte.unites]

    for u in texte.unites:
        if u.name[0] == "A":
            dot.node(u.name, u.name + " : " + u.txt, fillcolor='wheat')
        elif u.name[0] == "B":
            dot.node(u.name, u.name + " : " + u.txt, fillcolor='skyblue')
        else:
            dot.node(u.name, u.name + " : " + u.txt) 


    matrices = [a.matrice() for a in annotations]

    if regroupement == "emplacement":
        matrices = [matriceSansType(m) for m in matrices]
    elif regroupement == "catégorie":
        matrices = [matriceAvecCategories(m, categories) for m in matrices]

    matriceTotale = matrices[0].copy()
    for mat in matrices[1:]:
        matriceTotale = matriceTotale.add(mat)

    nbAnnotations = len(annotations)
    dot.attr(label='<<font point-size="20">'+nomTexte+'</font><br/><font point-size="16">'+str(nbAnnotations) + " annotations <br/> seuil = "+str(seuilAffichage)+"</font>>")
    dot.attr(labeljust="left")
    dot.attr(labelloc="top")

    nbMax = np.amax(matriceTotale.as_matrix())

    i = 0
    for rel in matriceTotale.items:
        i += 1
        for dest in units_names:
            for origine in units_names:
                val = matriceTotale[rel, origine, dest]
                if val/nbAnnotations > seuilAffichage:
                    label = ""
                    color = "2"
                    if regroupement != "emplacement":
                        label += rel + "\n"
                        color = str(i)
                    label += str(val)
                    poids = (val / nbMax) * 10
                    dot.edge(dest, origine, label=label, penwidth=str(poids), color=color, colorscheme="paired11", arrowsize="0.5", dir="back") #dir back car no fait pas un arbre à proprement parler
    
    if montrerThemes:
        dot.attr(forcelabels="true")
        nbThemes = dict()
        for u in texte.unites:
            nbThemes[u.name] = 0
        for a in annotations:
            for t in a.themes:
                nbThemes[t.unite.name] += 1
        
        for u, n in nbThemes.items():
            if(n > 0):
                dot.node(u, xlabel='<<B><I><font color="red">'+str(n)+"</font></I></B>>")
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

def annotationValide(annotation):
    mat = annotation.matrice().as_matrix()
    mat = mat.sum(0) #On ne tient pas compte des types de relation
    # On vérifie que toutes les flèches sont bien vers le haut, c'est-à-dire que la matrice est triangulaire inférieure
    flechesHaut = np.allclose(mat, np.tril(mat))
    #On vérifie maintenant qu'il y a exactement une relation qui part de chaque unité (sauf début)
    sommeLignes = mat.sum(1)
    zeroDebut = sommeLignes[0] == 0
    unPartoutAilleurs = np.all(sommeLignes[1:]==1)

    return flechesHaut and zeroDebut and unPartoutAilleurs

def supprimerMauvaisesAnnotations(campagne):
    annotationsSupprimees = list()
    for nomAnnot, annotateur in campagne.annotateurs.items():
        for texte in campagne.textes:
            if texte in annotateur.annotations:
                annot = annotateur.annotations[texte]
                if not annotationValide(annot):
                    del annotateur.annotations[texte]
                    annotationsSupprimees.append((nomAnnot, texte))
    return annotationsSupprimees


def calculEntropie(campagne, nomTexte, critere):
    """
    annotaion : Annotation
    critere : String : "emplacement", "type", "emplacement-type"
    """
    annotations = campagne.getAnnotations(nomTexte)
    units = [u.name for u in campagne.textes[nomTexte].unites]
    nomsCol = list()
    index = 0
    if critere == "emplacement":
        index = 0
        nomsCol = units
    elif critere == "type":
        index = 2
        nomsCol = campagne.typesRelations
    elif critere == "emplacement-type":
        index = 4
        for u in units:
            for r in campagne.typesRelations.keys():
                nomsCol.append(u + "-" + r)
    zeros = np.zeros((len(units)-1, len(nomsCol)))
    df = pandas.DataFrame(zeros, units[1:], nomsCol, dtype="int")
    for a in annotations:
        tab = a.representationEtiquettes()[index]
        for i, dest in enumerate(tab):
            df.iloc[i][dest] += 1
    
    entropie = pandas.Series(np.zeros(len(units)-1), units[1:])
    for u in df.index:
        p = df.loc[u] / df.loc[u].sum()
        entropie[u] = stats.entropy(p, base=2)
    return entropie

"""
Not used anymore
"""
# def createCondensedDistanceMatrix(camp, texteName, distanceLevel):
#     """
#     distanceLevel int qui peut être 0, 1 ou 2
#     0 : unité d'arrivée
#     1 : relation à l'unité
#     2 : unité ET relation
#     """
#     matrix = None
#     annotations = camp.getAnnotations(texteName)
#     for i in annotations :
#         kappasforI = []        
#         for j in annotations :
#             if i != j :
#                 kappasforI.append(1 - calculKappa(i,j)[distanceLevel])
#         if isinstance(matrix,type(None)) :
#             matrix = np.array(kappasforI)
#         else :
#             matrix = np.vstack([matrix, kappasforI])
        
#     return matrix

"""
Clustering
"""
def createVectorList(camp, textName, critere):
    """
    distanceLevel int qui peut être 0, 1 ou 2
    0 : unité d'arrivée
    1 : relation à l'unité
    2 : unité ET relation
    """
    annotations = camp.getAnnotations(textName)
    vectors = [calculDistanceKappa(annotations[i], annotations[j],critere) for (i,j) in itertools.combinations(range(len(annotations)), 2)]
    return vectors

def clusteringParTexte(camp, textname, critere) :
    """
    for a given text, uses distance vectors to create clusters of annotations with average algortihm
    args :  camp Campagne
            textname String
            critere int btwn 0 and 2 (our level of annotation comparing)
    """
    vectors = createVectorList(camp,textname, critere)
    cluster = linkage(vectors, 'average')
    fig = plt.figure(figsize=(10, 6))
    dn = dendrogram(cluster, labels = camp.getAnnotateurNamesForTexte(textname))
    plt.show()


def calculDistanceKappa(annotation1, annotation2, critere):
    """
    http://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html
    https://stackoverflow.com/questions/43676905/how-to-calculate-cohens-kappa-coefficient-that-measures-inter-rater-agreement?rq=1&utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    on calcule des kappa à partir de chaque représentations sous forme de liste de deux annotations d'un même texte, et on renvoi en fonction du critère choisi
    args :  2 Annotations
            critere : int entre 0 et 4 (notre "profondeur" de comparaison entre annotateurs)
    returns : list of 'critere' float, result of cohen_kappa_score
    """
    listA1 = annotation1.representationEtiquettes()
    listA2 = annotation2.representationEtiquettes()
    ListKappa = []
    for i in range(0,len(listA1)):
        ListKappa.append(cohen_kappa_score(listA1[i],listA2[i]))
    return 1 - ListKappa[critere]


def clusteringMultipleTextes(critere, camp, temoin = "", rupture1 = "", rupture2 = ""):
    """
    crée un cluster à partir des textes d'un annotateur
    """
    textList = ["Bac_a_sable",temoin,rupture1,rupture2]
    textList = list(filter(lambda a: a != "", textList))
    annotateurList = camp.getAnnotateursForTextes(textList)
    """
    ici : créer un vecteur avec les distances cummulées entre mêmes annotateurs sur plusieurs textes différents
    deux possiblités :
            createVector plusieurs fois et additionner les distances donc Calculer le Kappa de chaque texte et les additionner
            createVector une fois avec un gros Kappa sur toutes les annotations mises à la suite
    """
    """
    P1 : addition des vecteurs
    """
    vectors = []    
    print("Textes annotés :")
    print(textList)
    for textename in textList:
        vectors = createCumuledVectorList(annotateurList,textename, critere, vectors)
    cluster = linkage(vectors, 'average')
    fig = plt.figure(figsize=(10, 6))
    annonames = []
    for a in annotateurList :
        annonames.append(a.id)
    dn = dendrogram(cluster, labels = annonames)
    plt.show()
    
    """
    P2
    """
    #pertinent ?
    
    
def createCumuledVectorList(annotateurList,textename, critere, vector):
    """

    """
    v = [calculDistanceKappa(annotateurList[i].annotations[textename], annotateurList[j].annotations[textename],critere) for (i,j) in itertools.combinations(range(len(annotateurList)), 2)]
    if len(vector) == 0 : 
        return v
    else :
        for i in range(len(v)) :
            vector[i] = vector[i] + v[i]
    return vector

"""
Rupture discursive
"""
def rupturesFrontiereDroite(annotation):
    """
    Retourne la liste des unités qui sont reliées en brisant la règle de la frontière droite.
    Si tout un sous-arbre est rattaché à gauche d'une ancienne unité, toutes les unités du sous-arbre sont retournées. Plus tard, il pourrait être intéressant de chercher à "réparer" la conversation à la manière du psychologue qui conduit les interviews, et ne retourner que la racine de ce sous-arbre, afin de chercher s'il y a d'autres ruptures à l'intérieur.
    """
    arbre = annotation.arbre()
    ordreParcours = arbre.parcoursPrefixe()
    unites = annotation.texte.unites
    ruptures = list()

    for i in range(len(unites)):
        if unites[i] != ordreParcours[i] and unites[i].debut < ordreParcours[i].debut:
            ruptures.append(ordreParcours[i])

    return ruptures
