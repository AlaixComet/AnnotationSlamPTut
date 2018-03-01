from data_analyse import *
import sys
from bs4 import BeautifulSoup
from data_analyse import to_xml, annotateur, data
from collections import Counter, OrderedDict
import re
import operator
import glob

class Unit:
    """
    Unit Class
        label : String name of the Unit
        start : String start position of the selected Unit
        end : String end position of the selected Unit
        theme : String theme of the Unit

    has tostring method
    """
    def __init__(self, label, start, end, theme):
        self.label = label
        self.start = start
        self.end = end
        self.theme = theme

    def setTheme(self, theme):
        self.theme = theme

    def tostring(self):
        return("    label:"+str(self.label)+" start:"+str(self.start)+"  end:"+str(self.end)+"   theme: "+str(self.theme))

class Theme:
    """
    Theme Class
        label : String name of the Theme
        pos : ?? postion of the Theme

    has tostring method
    """
    def __init__(self, label, pos):
        self.label = label
        self.pos = pos



    def tostring(self):
        return("     label:"+str(self.label)+"  pos:"+str(self.pos))


class Relation:
    """
    Relation Class
        type : String type of the Relation {Narration, Phatique, ...}
        start : String start of the Relation
        end : String end of the Relation
    """
    def __init__(self, label, start, end):
        self.type = label
        self.start = start
        self.end = end


class Data:
    """
    Data Class
        filename        = String name of the file, taken as an input in Data constructor
        txt             = readable file lines of filename
        xml             = xml version of txt file with BeautifulSoup
        rels            = List of String relations from xml file "relations"
        nbrels          = Int len(rels)
        relations_count = dictionnary of different relations in rels
        relations_freq  = dictionnary with {relation Label : Float frequency} for each different relation
        units           = List of Unit Objects
        themes          = List of Theme Objects
        units           = List of Unit Objects
        nb_diff_themes  = int nb different themes
        theme_count     = dictionnary of different themes in rels
        theme_freq      = dictionnary with {relation Label : Float frequency} for each different relation
        after_data      = //TODO use of data_analyse.py with panda
    """
    def __init__(self, ffile):
        self.filename = ffile
        self.txt = self.totxt()
        self.xml = self.toxml()
        self.rels = self.rels_list()
        self.nbrels = len(self.rels)
        self.relations_count = self.count_rel()
        self.relations_freq = self.freq_rel()
        self.units = self.unit_list()
        self.themes = self.theme_list()
        self.units = self.assoc_unit_theme(self.units, self.themes)
        self.nb_diff_themes = self.diff_themes()
        self.theme_count = self.count_theme() 
        self.theme_freq = self.freq_theme()
        self.after_data = data(ffile)


    def totxt(self):
        with open(self.filename) as txt:
            return txt.read()

    def toxml(self):
        xml = BeautifulSoup(self.txt, 'lxml')
        return xml

    def rels_list(self):
        return [x.type.text for x in self.xml.findAll('relation')]

    def count_rel(self):
        return dict(Counter(self.rels))

    def freq_rel(self):
        count = self.count_rel()
        size = len(self.rels)
        ret = {}
        for key, value in count.items():
            ret[key] = (float(value)*100.0)/float(size)
        return ret

    def count_theme(self):
        """
        count the number of occurences of each theme
        """
        themes = [u.theme for u in self.units]
        return dict(Counter(themes))

    def freq_theme(self):
        """
        count the frequence of apparition of each thme
        """
        count = self.count_theme()
        size = len(self.units)
        ret = {}
        for key, value in count.items():
            ret[key] = (float(value)*100.0/float(size))
        return OrderedDict(sorted(ret.items(), key=operator.itemgetter(1)))

    def unit_list(self):
        units = self.xml.findAll('unit')
        ret = []
        for u in units:
            if u.author.text[:7] == "vsteyer":
                start = u.start.singleposition['index']
                end = u.end.singleposition['index']
                unit = Unit(None, start, end, None)
                ret.append(unit)
        return ret

    def unit_dict(self, themes):
        """
        cree un dictionnaires clé : pos, value : theme
        input : themes List of Strings
        output : dictionnay {position : label}
        """
        dic = {}
        for t in themes:
            dic[t.pos] = t.label

        return dic

    def assoc_unit_theme(self, units, themes):
        """
        associe à chaque unité son thème 
        output : list of Units
        """
        themes_dic = self.unit_dict(themes)
        ret = []
        for key, value in themes_dic.items():
            for u in units:
                if key <= u.end:
                    label = u.label
                    start = u.start
                    end = u.end
                    newu = Unit(label, start, end, value)
                    ret.append(newu)
        return(ret)

    def tout_reliee(self):
        """
        Je crois qu'à un moment elles appellent ça pour définir le nb de relation prédéfini
        en fonction du nom du fichier parcouru

        pas d'output, pas d'input, juste une lecture console et une initialisation de nbrels
        """
        nb_unit = {'pro': 23.0,
                    'nord': 13.0,
                    'flo': 14.0,
                    'bas': 8.0}

        if "bas" in os.path.basename(self.filename):
            return nb_unit['bas']-1 == self.nbrels
        if "nord" in os.path.basename(self.filename):
            return nb_unit['nord']-1 == self.nbrels
        if "pro" in os.path.basename(self.filename):
            return nb_unit['pro']-1 == self.nbrels
        if "flo" in os.path.basename(self.filename):
            return nb_unit['flo']-1 == self.nbrels


    def theme_list(self):
        """
        generates a List of Theme Object from xml file
        """
        themes = self.xml.findAll('flag')
        ret = []
        for t in themes:
            label = t.comment.text.replace(',', '')
            start = t.singleposition['index']
            theme = Theme(label, start)
            ret.append(theme)
        return ret

    def diff_themes(self):
        """
        output : Float frequency of each different themes
        """
        count = dict(Counter(self.themes))
        if len(count) != 0:
            return ((len(count)*100.0)/len(self.units))
        else:
            return (len(count))

    def retour_arriere(self):
        """
        ??? Elle s'en servent dans leurs tests
        Je crois que ça montre si on retrouve un theme dejà utilisé, donc un retour arrière
        dans la conversation
        output : Int le nombre de retours arrière. 
        """
        ret = 0
        li = []
        for t in self.themes:
            if t.label not in li:
                li.append(t.label)
            elif t.label != li[-1]:
                ret += 1
        return ret

    def create_line(self):
        """
        ouah je comprends paaaaas
        Elles créent une énorme string, sorte de résumé avec leurs données venues de Data.
        """
        # nom du fichier
        string = ""
        string += os.path.basename(self.filename)
        string += ","

        # nombre de themes différents
        string += str(self.nb_diff_themes)
        string += ","

        # ajout de la frequence d'apparition des relations
        relations = ['Méta-question', 'Phatique',
                        'Elaboration evaluative', 'Contre-élaboration',
                        'Narration', 'Elaboration descriptive',
                        'Conduite', 'Elaboration evaluative',
                        'Question', 'Réponse',
                        'Elaboration prescriptive']
        for rel in relations:
            if rel in self.relations_freq.keys():
                string += str(self.relations_freq[rel])
                string += ","
            else:
                string += '0'
                string += ","

        # 0 theme
        if len(list(self.theme_freq)) == 0:
            string += "None,None,None,None,None,None,"

        # 1 seul theme
        if len(list(self.theme_freq)) == 1:
            for items in list(self.theme_freq)[:3]:
                string += items
                string += ","
                string += str(self.theme_freq[items])
                string += ","
            string += "None,None,None,None,"

        # 2 themes
        if len(list(self.theme_freq)) == 2:
            for items in list(self.theme_freq)[:3]:
                string += items
                string += ","
                string += str(self.theme_freq[items])
                string += ","
            string += "None,None,"


        # 3 themes les + fréquents ainsi que leur fréquence
        if len(self.theme_freq) >= 3:
            for items in list(self.theme_freq)[:3]:
                string += items
                string += ","
                string += str(self.theme_freq[items])
                string += ","

        # age annotateur
        string += self.after_data['age']
        string += ","
        # comprehension de la mission
        string += re.sub(r'\(.*\)', '', self.after_data['comp_mission']).replace(' ','')
        string += ","
        # comprehension de la plate forme
        string += re.sub(r'\(.*\)', '', self.after_data['comp_glozz']).replace(' ','')
        string += ","
        # avis sur la duree
        string += re.sub(r'\(.*\)', '', self.after_data['duree']).replace(' ','')
        string += "\n"
        return string



class Datas:
    def __init__(self, files):
        """ init de la class, attributs:
        list of Data objects
        list of themes
        counter of themes per files """
        self.datas = self.init_datas(files)

    def init_datas(self, files):
        datas = []
        for f in files:
            print(f)
            d = Data(f)
            datas.append(d)  # list of data objects
        return datas

    def prepare_lines(self):
        init_str = "filename,nb themesdiff,nb meta,nb phatique,nb elab,\
                    nb contreelab,nb narr,nb Elaboration descriptive,\
                    nb Conduite,nb Elaboration evaluative,nb Question,\
                    nbRéponse,nb Elaboration prescriptive, Theme1, FreqT1,\
                    Theme2,FreqT2,Theme3,FreqT3,age,comprehension mission,\
                    comprehension glozz, avis duree\n"
        # premiere ligne du csv, definition des colones
        lines = [init_str]
        for d in self.datas:
            lines.append(d.create_line())
        return lines



if __name__ == "__main__":
    files = glob.glob('A*/*.aa')
    files += glob.glob('B*/*.aa')
    d = Datas(files)
    l = d.prepare_lines()

    #suite de print tests

    # with open("retours_arriere.csv", "w") as f:
    #     f.write('file, retour\n')
    #     for data in d.datas:
    #         line = str(os.path.basename(data.filename))+","+str(data.retour_arriere())
    #         print(line)
    #         f.write(line+'\n')

    # with open("unitees_reliees.csv", "w") as f:
    #     f.write('file, reliee\n')
    #     for data in d.datas:
    #         if data.tout_reliee:
    #             line = str(os.path.basename(data.filename))+",TRUE"
    #         else:
    #             line = str(os.path.basename(data.filename))+",FALSE"
    #         f.write(line+"\n")

    # with open('output.csv', 'a') as the_file:
    #     for line in l:
    #         the_file.write(line)
    # filename = sys.argv[1]
    # print(filename)
    # d = Data(filename)
    # print(d.retour_arriere())
    #
    # print("RELATIONS")
    # print(d.rels)
    #
    # print("\n"+"UNIT")
    #
    #
    #
    # print("\n THEME")
    # themes = d.theme_list()
    # print([t.tostring() for t in themes])
    #
    # print("\n ASSOC UNIT THEME")
    #
    # # units = d.assoc_unit_theme(units, themes)
    # print([u.tostring() for u in d .units])
    #
    # print("\n DIFF THEMES")
    # print(d.nb_diff_themes)
    #
    # print("\n AFTER DATA")
    # print(re.sub(r'\(.*\)', '', d.after_data['comp_mission']))
    #
    # print("\n RELATIONS DISTINCT")
    # relations = d.relations_count.keys()
    # print(relations)
    #
    # print("\n theme count")
    # print(d.theme_count)
    #
    #
    # print("\n theme freq")
    # print(d.theme_freq)
    #
    # print("\n TEST STRING")
    # print("filename, nb themesdiff, nb meta, nb phtatique, nb elab, nb contreelab, nb narr, nb Elaboration descriptive, nb Conduite, nb Elaboration evaluative,  nb Question,nbRéponse, nb Elaboration prescriptive")
    # print(d.create_line())
    #
    # print("\n PAS RELIEE")
    # print(d.tout_reliee())
