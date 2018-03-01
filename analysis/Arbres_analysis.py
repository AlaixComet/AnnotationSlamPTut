import glob
import re
from Arbres import *
from copy import copy
import os


def dict_unit(txt):
    """
    input  : txt String name of the file to read
    output : Dictionnary {int from 0 to nb line : String txtLine}
    """
    dic = {}
    i = 0
    with open(txt) as txt:
        lines = txt.readlines()
        for line in lines:
            line = line.replace('\n', '')
            line = re.sub(r'\w\d* *: ', '', line)
            dic[i] = line
            i += 1
    return dic

# a chaque unite on associe son id debut pour le parcours prefix

def assoc_id(txt):
    """
    je sais pas ce qu'ils ouvrent avec
    """
    nodes = {}
    with open(txt) as txt:
        txt = txt.read()
        # recuperation des lignes noeuds
        iter_labels = re.finditer(r'\w\d\[label = "\d*.*"', txt)
        for label in iter_labels:
            node = re.search(r'\w\d', label.group(0)).group(0)
            idd = re.findall(r'.*"(\d*)_.*', label.group(0))
            nodes[node] = idd
    return nodes

def read_dot(txt):
    """
    surement pour lire les fichier .dot qu'on a pas du coup
    Mais la regex ressemble à la structure "txt" de Glozz
    Retroune une liste de strings de la forme (\w\d -> \w\d) soit (unit -> unit)
    """
    #unused variable dic /!\
    dic = {}
    rels = []

    # pour savoir si début est present, si oui on veut l'ignorer
    ignoreDeb = False

    # dans notre cas nord et provoc ont l'unité début
    if "pro" in txt or "nord" in txt:
        ignoreDeb = True

    with open(txt) as txt:
        lines = txt.readlines()
        for line in lines:
                if re.match(r'.*\w\d -> \w\d.*', line):
                    rel = re.findall(r'(\w\d -> \w\d)', line)[0]
                    # print(rel)

                    if ignoreDeb and rel[:2] == "A0":
                        None
                    else:
                        rels.append(rel)
    return rels


def to_tree(li, rels):
    """
    creation of a "tree" from empty list and relation list
    to check
    why isn't imported Arbre Object used ??
    TODO check and use Arbre ??
    """
    data = rels.pop(0)
    # dbug: print("\n"+str(data))
    (pere, fils) = (data[:2], data[-2:])
    d = (pere, fils) # psq flemme

    # on verifie si le pere n'est pas un fils plus tard, si oui on ajoute
    # en fin de liste pr respecter l'ordre
    if pere in [f[-2:] for f in rels]:
        # print("fils plus tard")
        rels.append(data)

    # sinon on lance l'algo de creation de la structure
    else:
        # print("\n"+str(d))
        if exists(pere, li) or li==[]:
            check_and_add(d, li)
        else:
            # cas
            # print('sous arbre')
            old = copy(li)
            del(li[:])

            li.append(old)
            li.append([pere, fils])

        # print(li)


def exists(k, l):
    """
    False if l is not a list (tree list of sons)
    True if k in l (direct son node)
    Recursivly checks for each sublist of l (each son nodes)
    """
    if not isinstance(l, list):
        return False
    if k in l:
        return True
    return any(map(lambda sublist: exists(k, sublist), l))



# pf est un tuple pere fils
def check_and_add(pf, li):
    """
    tous les return sont Null
    Sinon ça m'a l'air de prendre un tuple pere fils et de l'ajouter à une liste
    """
    # cas 1 er tour
    if li == []:
        li.append(pf[0])
        li.append(pf[1])

        return

    if pf[1] in li:
        return

    # cas ou il est dans la liste de base
    inlist = False
    nested = False
    # if search(pf[0], li):
    #    print("inlist true")
    #    inlist = True
    if pf[0] in li:
        inlist = True

    # cas ou l'element est imbriqué dans une sous liste
    elif exists(pf[0], li):
        nested = True

    # verif et ajout recursif
    for index, elem in enumerate(li):
        # la racine n'est pas en tête de liste donc il faut créer un sous arbre
        if pf[0] == elem and li[0] != elem:
            li[index] = [pf[0], pf[1]]
            return

        # la racine est en tête de liste donc on ajoute en tant que fils
        if pf[0] == elem and li[0] == elem:
            li.append(pf[1])
            return

        if isinstance(elem, list) and not inlist:
            # lelem courant est une list, go recursion
            # if nested: # si l'élément est bien qqpart dans la liste
            check_and_add(pf, elem)
            return

def sous_arbre(rels):
    """
    recherche si l'arbre est composé de plusieur sous arbres ??
    Si oui il y a rupture.
    input : rels a list wich is in fact a tree
    ouptut : Boolean
    """
    li = []
    nbarbre = 1 # 1 arbre de base
    # print(rels)
    while rels != []:
        rel = rels.pop(0)
        (pere, fils) = (rel[:2], rel[-2:])
        if li == []:
            li.append(pere)
            li.append(fils)
        else:
            # on verifie si le pere n'est pas un fils plus tard, si oui on ajoute
            # en fin de liste pr respecter l'ordre
            if pere in [f[-2:] for f in rels]:
                # print("fils plus tard")
                rels.append(rel)
            elif pere in li or fils in li:
                li.append(fils)
            else:
                nbarbre += 1
    # print(nbarbre)
    if nbarbre != 1:
        return True
    else:
        return False




def run():
    """
    reads the dot files and check if for each of them there is sub trees.
    writes the results in file "sous_arbre.csv"
    """
    dic = {}
    # directory where your dots files are hidden ;)
    #mdr non
    cur_dir = 'textes_emilie_laurine/decote_arbres_reference/arbres_nouv/'
    # to get dot files
    dot = '*.dot'
    all_files = glob.glob(cur_dir + dot)
    # bon = 0
    # nbfiles = 0
    with open("sous_arbre.csv","w") as wf:
        wf.write('file, sousarbre')
        for f in all_files:
        #     nbfiles += 1
    #     ids = assoc_id(f)
    #     li = []
            rels = read_dot(f)
            if sous_arbre(rels):
                wf.write(str(os.path.basename(f))+",OUI\n")
            else:
                wf.write(str(os.path.basename(f))+",NON\n")

    #      while rels != []:
    #         # print(d)
    #         to_tree(li, rels)
    #     print(li)
    #     if isinstance(li[0], list):
    #         print("mal formé")
    #         bon += 1
    #
    #
    # print("nombre de fichier : " + str(nbfiles))
    # print("nombre de fichier mal formés: " + str(bon))



    # prefixe_out = a.prefixe()
    # prefixe_out_ids = [ids[x] for x in prefixe_out]
    # print(prefixe_out_ids)
    # a.view()




run()
