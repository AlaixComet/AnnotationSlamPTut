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

    def getAnnotations(self, nomTexte):
        annotations = list()
        for annotateur in self.annotateurs.values():
            if nomTexte in annotateur.annotations:
                annotations.append(annotateur.annotations[nomTexte])
        return annotations

    def getAnnotateurNamesForTexte(self, nomTexte) :
        annotNames = list()
        annotations = self.getAnnotations(nomTexte)
        for a in annotations:
            annotNames.append(a.annotateur.id)
        return annotNames

    def getAnnotateursForTextes(self, textlist) :
        """
        args : list of string textname
        result : list of Annotateur which passed the given textes
        """
        aList = self.annotateurs.copy()
        for t in textlist :
            for i,a in enumerate(aList) :
                if t not in a.annotations.keys() :
                    aList.pop(i)
        return aList


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
        return self.name + " : " + self.txt
    
    def __repr__(self):
        return self.name
    
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
        unite : Unit auquel est attaché le thème
    """
    def __init__(self, label, debut, texte):
        self.label = label
        self.debut = debut
        self.unite = None
        self.__linkToUnit(texte.unites)
    
    def __linkToUnit(self,unitList):
        """
        links the theme to the corresponding unit
        """
        for u in unitList[1:] :
            # Par défaut on dit que le thème est rattaché à la première unité (sauf début)
            if self.unite == None :
                self.unite = u
            #puis on cherche quelle est la vraie unité (éventuellement la première aussi !)
            if u.fin >= self.debut : 
                self.unite = u
                break
        return self

    def __repr__(self):
        return self.label


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
        self.themes = sorted(themes, key=lambda x:x.debut)
        self.__nettoyerThemes()
        self.relations = relations

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.annotateur.id == other.annotateur.id and self.texte.nom == other.texte.nom
        else:
            return False

    def matrice(self):
        """
        Retourne la liste des relation sous forme de pandas.Panel (matrice 3D) 
        binaire. La première dimension correspond au type de relation, la deuxième
        à l'origine de la relation et la troisième à sa destination.
        """
        tab = np.zeros((len(self.annotateur.campagne.typesRelations.keys()), len(self.texte.unites), len(self.texte.unites)),  dtype="int")
        nomsUnites = [u.name for u in self.texte.unites]
        #Les Panels c'est des matrices 3D. L'avantage c'est qu'on peut nommer les colonnes ! 
        panel = pandas.Panel(tab, self.annotateur.campagne.typesRelations.keys(), nomsUnites, nomsUnites) 
        for rel in self.relations[:]: #on parcourt une copie de la liste pour pouvoir supprimer les relations en trop dans la vrai
            if rel.type is not None and rel.dest.name is not None and rel.origine.name is not None:
                if panel.loc[rel.type, rel.origine.name, rel.dest.name] == 1: #S'il y a 2 relations identiques on en supprime une
                    self.relations.remove(rel)
                else:
                    panel.loc[rel.type, rel.origine.name, rel.dest.name] = 1
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
        
        # On fait des paires (Noeud, typeRelation)
        noeudsFilsHoriz = [(self.__makeTree(f[0]), f[1]) for f in filsHoriz]
        noeudsFilsVert = [(self.__makeTree(f[0]), f[1]) for f in filsVert]

        # On trie les fils par ordre d'apparence des unités dans le texte
        noeudsFilsHoriz.sort(key= lambda x : self.texte.unites.index(x[0].racine))
        noeudsFilsVert.sort(key= lambda x : self.texte.unites.index(x[0].racine))
        
        return Arbre(debut, noeudsFilsHoriz, noeudsFilsVert)
    
    def dessinerArbre(self, montrerThemes=False):
        """
        Permet de dessiner l'arbre d'annotations d'une personne, à l'aide de Graphviz. 
        L'objet retourné est un Digraph Graphviz. Il peut être enregistré comme suit :
        dot = annot.dessinerArbre()
        dot.format = 'png' # si on veut changer le format d'enregistrement
        dot.render()

        montrerThemes: boolean qui indique si on doit afficher les boîtes thématiques ou pas
        return: graphviz.Digraph
        """
        nom = self.texte.nom+'_-_'+self.annotateur.id
        dot = Digraph(name=nom, node_attr={'shape':'box','style':'filled'})
        dot.attr(newrank="true") # pour que ça affiche les clusters au bon endroit

        dot.node("zero", style="invis") # Le noeud d'origine du dessin
        # Ajout des unités
        for u in self.texte.unites:
            if u.name[0] == "A":
                dot.node(u.name, u.name + " : " + u.txt, fillcolor='wheat')
            elif u.name[0] == "B":
                dot.node(u.name, u.name + " : " + u.txt, fillcolor='skyblue')
            else:
                dot.node(u.name, u.name + " : " + u.txt)       

        # Ajout des relations
        typesRel = self.annotateur.campagne.typesRelations
        debut = self.texte.unites[0].name
        dot.edge("zero", debut, label="", style="invis") #On relie le début à l'origine
        for rel in self.relations:
            if typesRel[rel.type] == "horizontale":
                ## On n'utilise au final pas les sous-graphes car ils ne permettent pas d'afficher aussi les thèmes (on ne peut pas faire des clusters et sous-graphes qui se chevauchent)
                # with dot.subgraph() as sub:
                #     sub.attr(rank="same")
                #     sub.node(rel.dest.name)
                #     sub.node(rel.origine.name)
                #     sub.edge(rel.dest.name, rel.origine.name, label=rel.type, dir="none")
                

                ## A la place on va relier les membres d'une relation horizontale au noeud situé au-dessus, de manière invisible
                # Pour ça il faut donc chercher le parent qui est situé au dessus : ce n'est pas forcément le parent immédiat car on peut avoir un enchainement de relations horizontales
                relParent = rel.type
                noeudParent = rel.dest.name
                while typesRel[relParent] == "horizontale" and noeudParent != debut: #on cherche jusqu'à arriver à une relation verticale, ou au début
                    mat = self.matrice()[:,noeudParent,:] # matrice (destination, typeRel) binaire présentant toutes les relations qui partent du parent
                    ligne = ""
                    colonne = ""
                    where = np.argwhere(mat.as_matrix()) # On cherche l'index de la case où il y a un 1, c'est à dire celle qui correspond à la relation qui part de cette unité
                    if(len(where)>0): # Si on a bien trouvé une case (normalement il n'y en a qu'une)
                        ligne, colonne = where[0] 
                        # On transforme cet index numérique en le nom de l'unité et le type de relation
                        noeudParent = mat.index[ligne]
                        relParent = mat.columns[colonne]
                    else: # Sinon c'est qu'on est arrivé au début (il n'a pas de parent) ou que l'annotateur a oublié de relier cette unité
                        noeudParent = debut
                #Si on est arrivé au début il faut se raccrocher à l'origine invisible comme parent vertical
                if noeudParent == debut:
                    noeudParent = "zero"
                #On ajoute ensuite une relation verticale invisible vers le noeud au-dessus, afin de contraindre notre noeud dans la hiérarchie du graphe : il doit forcément être placé sous noeudParent
                dot.edge(noeudParent, rel.origine.name, style="invis", weight="1") # On met un poids de 1 (faible) car cette relation n'est pas importante et peut-être penchée. Les vraies relations verticales en revanche auront un poids plus élevées pour être dessinées le plus verticalement possible
                # On dessine enfin la relation horizontale. constraint=false permet d'indiquer que cette relation n'intervient pas dans la hiérarchie du graphe : les deux noeuds doivent être dessinés au même niveau.
                dot.edge(rel.dest.name, rel.origine.name, label=rel.type, dir="none", constraint="false")
            else:
                dot.edge(rel.dest.name, rel.origine.name, label=rel.type, dir="none", weight="2") # On met un poids de 2 pour que cette relation soit prioritaire sur les relations invisibles : elle doit être dessinée le plus verticalement possible.


        # Ajout des thèmes
        if montrerThemes:
            colorsThemes = dict()
            i = 0
            colors=["violetred", "olivedrab", "red", "burlywood4", "blue", "peru", "seagreen4", "mediumorchid", "royalblue", "darkorange"]
            for theme, unites in self.getThemesUnitsList():
                if theme not in colorsThemes:
                    colorsThemes[theme] = colors[i]
                with dot.subgraph(name="cluster_"+str(i)) as c:
                    c.attr(label="<<B>"+theme+"</B>>")
                    c.attr(color=colorsThemes[theme])
                    c.attr(fontcolor=str(colorsThemes[theme]))
                    for u in unites:
                        c.node(u.name)
                i += 1 

        return dot

    def __nettoyerThemes(self):
        """
        Nettoie la liste des thèmes en faisant en sorte de n'en garder qu'un seul par unité et de fusionner les thèmes qui se suivent mais portent le même label.
        """
        themesPropres = list()
        if(len(self.themes) > 0):
            #On ajoute le premier thème s'il n'est pas nul
            previousT = self.themes[0]
            if(previousT.label.strip() != ""):
                themesPropres.append(previousT)
            #Puis on parcourt tous les autres en n'ajoutant que ceux qui sont différents du précédent à chaque fois
            for t in self.themes[1:]:
                if previousT.label != t.label and previousT.unite != t.unite and t.label.strip() != "":
                    themesPropres.append(t)
                previousT = t
        self.themes = themesPropres


    def getThemeByUnit(self, unite):
        """
        """
        for t in self.themes :
            if t.unite == unite :
                return t
    
    def getThemesUnitsList(self):
        """
        Retourne la liste de tous les thèmes de l'annotation avec les unités correspondantes
        return: list de tuples (labelTheme, list d'Units)
        """
        unitsThemeChanges = [t.unite for t in self.themes]
        themesUnits = [(t.label, [t.unite]) for t in self.themes]
        i = -1
        for u in self.texte.unites:
            if u in unitsThemeChanges:
                i += 1
            elif i >= 0:
                themesUnits[i][1].append(u)
        return(themesUnits)

    def representationEtiquettes(self):
        """
        return List of 3 list of string
        chaque case correspond à une unité de départ. Attention, la première case correspond à la première unité après début. on y stocke. 
        1 : string de l'unité d'arrivée
        2 : la catégorie de relation
        3 : la relation
        4 : unité d'arrivée-catégorie de relation
        5 : unité d'arrivée-relation
        """
        array1,array2,array3,array4,array5 = ([],[],[],[],[])
        categories = {
            "Narration" : ["Narration"],
            "Elaborations" : ["Elaboration descriptive","Elaboration evaluative","Elaboration prescriptive","Contre-élaboration","Réponse"],
            "Méta" : ["Conduite", "Phatique", "Méta-question"],                        
            "Question" : ["Question"],
            }
        for u in self.texte.unites :
            for r in self.relations :
                if r.origine == u :
                    c =""
                    for cat,rels in categories.items() :
                        if r.type in rels :
                            c = cat
                    array1.append(r.dest.name)
                    array2.append(c)
                    array3.append(r.type)
                    array4.append(r.dest.name+"-"+c)
                    array5.append(r.dest.name+"-"+r.type)
        return [array1,array2,array3,array4,array5]


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

    def parcoursPrefixe(self):
        parcourus = [self.racine]
        for v in self.filsVert:
            parcourus.extend(v[0].parcoursPrefixe())
        for h in self.filsHoriz:
            parcourus.extend(h[0].parcoursPrefixe())
        return parcourus

    def __str__(self):
        return repr(self.racine) + " " + repr(self.filsVert) + " " + repr(self.filsHoriz)
    
    __repr__ = __str__
