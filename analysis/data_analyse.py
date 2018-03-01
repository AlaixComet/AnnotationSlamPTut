from lxml import etree
import os
import sys
from collections import Counter
import matplotlib.pyplot as plt
import subprocess
import pandas


def annotateur(f):
    """returns string annotateur name from file name following the nomenclature "annotateur_typetext" """
    # print('ici'+os.path.basename(f).split('_'))
    return os.path.basename(f).split('_')[0]


def data(f):
    """ returns Dataframe from data_retours.csv for the annotator of the selected file """
    d = pandas.DataFrame.from_csv('data_retours.csv', index_col=1)
    return d.loc[annotateur(f)]


def type_texte(f):
    """returns string text name from file name following the nomenclature "annotateur_typetext" """
    return os.path.basename(f).split('_')[1]


def print_themes(xml):
    """
    input : xml parser
    prints theme list
    """
    for theme in xml.xpath('/annotations/flag/characterisation/comment'):
        print("  ->"+theme.text)


def theme_list(xml):
    """
    input : xml parser
    output : theme list
    """
    t = []
    for theme in xml.xpath('/annotations/flag/characterisation/comment'):
        t.append(theme)
    return t


def nb_themes(xml):
    """
    input : xml parser
    prints number of themes
    """
    nbtheme = 0
    for theme in xml.xpath('/annotations/flag/characterisation/comment'):
        nbtheme = nbtheme+1
    print("  "+str(nbtheme))


def to_xml(f):
    ''' takes a filename and creates the associated xml parser '''
    tree = etree.parse(f)
    return tree


def relations_print(xml):
    '''returns a list of every relations'''
    for rel in xml.xpath('/annotations/relation/characterisation/type'):
        print(rel.text)


def relations_list(xml):
    '''returns a list of relations'''
    li = []
    for rel in xml.xpath('/annotations/relation/characterisation/type'):
        li.append(rel.text)
    return li


def nb_rel(xml):
    """
    input : xml parser
    output : int len of the relation list in the xml file
    """
    li = relations_list(xml)
    return len(li)


def count_rel(xml):
    """
    input : xml parser
    output : relation list counter
    """
    li = relations_list(xml)
    c = Counter(li)
    return c


def plot_relations(xml):
    """
    input : xml parser
    output : a mathlab pie (onsenfou)
    """
    counts = count_rel(xml)
    a = plt.pie([float(v) for v in counts.values()],
                labels=[k for k in counts], autopct=None)
    return a


def create_dot(dirr, filee):
    """
    tous les chemins de fichiers sont en dur, TODO changer tt ça
    sinon ça a l'air de créer les fameux .dot à partir du script "/script_gen_arbre.sh"
    """
    launch = "/script_gen_arbre.sh"

    # change directory to find script
    os.chdir('/home/laurine/Documents/PROJETTUT2017')
    path = os.getcwd()
    launch = path+launch

    strr = "/home/laurine/Documents/PROJETTUT2017/check.sh B06_bruno B06_flo"
    print("le checkkkkkk")
    res1 = subprocess.check_call([strr], shell=True, stderr=subprocess.STDOUT)
    for r in res1:
        print(r)

    cmd = launch+" "+dirr+" "+filee
    print(cmd)

    res = subprocess.check_call([cmd], shell=True, stderr=subprocess.STDOUT)
    for r in res:
        print(r)
    print("[ERREUR] : cannot launch this java command")


if __name__ == '__main__':
    args = sys.argv[1:]
    print("\n\n\n\n")
    print("### Themes dans "+sys.argv[1]+" ###")
    while args != []:
        f = args.pop()
        xml = to_xml(f)
        print_themes(xml)
