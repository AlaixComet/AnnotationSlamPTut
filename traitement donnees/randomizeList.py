from random import randint

"""
file used to generate random list of texts
"""

def randommizeList(l):
    """
    with a list l return randomized list l2
    """
    l2 = []
    if len(l) == 0 :
        raise Exception("list can't be empty")
    while(len(l)>0) :
        if len(l) == 1 :
            l2.append(l.pop())
            return l2
        else :
            l2.append(l.pop(randint(0,len(l)-1)))

def chooseOneFromList(l) :
    """
    with a list l return a random value
    """
    if len(l) == 0 :
        raise Exception("list can't be empty","list len = "+str(len(l)),l)
    return l.pop(randint(0,len(l)-1))
    

temoin = ["volley","concours"]
text1 = ["nord","florence"]
text2 = ["sauveur","provocation"]

with open("Liste_Textes_Passation.txt",'w',encoding="utf-8") as csvFile :
    csvFile.write("Id Annotateur,Texte 1,Texte 2,Texte 3\n")
    for i in range(0,150):
        l = []
        l.append(chooseOneFromList(temoin.copy()))
        l.append(chooseOneFromList(text1.copy()))
        l.append(chooseOneFromList(text2.copy()))
        finalL = randommizeList(l.copy())
        csvFile.write(","+str(finalL[0])+","+str(finalL[1])+","+str(finalL[2])+"\n")
