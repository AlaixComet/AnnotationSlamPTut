from parsing2 import parsing
from os import path

AnnotationDirectory = "Campagne 2018"
projectDirectory = path.dirname(path.realpath(__file__))
projectDirectory = path.join(path.split(projectDirectory)[0])
textsNames = ["Bac_a_sable","Florence","Provocation", "Nord", "Concours", "Sauveur", "Volley"]
textDirectories = [path.join(projectDirectory,AnnotationDirectory,t) for t in textsNames]

camp = parsing(textDirectories)

typesRel = {"Narration":"horizontale", "Réponse":"horizontale", "Elaboration descriptive":"verticale", "Elaboration evaluative":"verticale", "Elaboration prescriptive":"verticale", "Conduite":"verticale","Phatique":"verticale","Contre-élaboration":"verticale","Méta-question":"verticale","Question":"verticale"}
camp.typesRelations = typesRel

for t in textsNames:
    annotations = camp.getAnnotations(t)
    dossierThemes = path.join(projectDirectory,"arbres",t, "themes")
    dossierRelations = path.join(projectDirectory,"arbres",t, "relations")
    for a in annotations:
        print(t, a.annotateur.id)
        gThemes = a.dessinerArbre(montrerThemes=True)
        gThemes.format = 'png'
        gThemes.render(directory=dossierThemes)

        gRelations = a.dessinerArbre(montrerThemes=False)
        gRelations.format = 'png'
        gRelations.render(directory=dossierRelations)