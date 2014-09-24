# -*- coding: utf8 -*-

import re

choixMultiples=["MC","MCV","MCH"]
choixSimples=["SA","SAC"]

def makeChamps(chaine,champs):
#    print chaine, donnees
#    champs=donnees.split(";")
    chunks=re.findall(r"(#[^#]+#|[^#]*)",chaine)
    result=""
    for chunk in chunks:
        sChamp=re.match("#(\d+)#",chunk)
        if sChamp:
#            print sChamp.group(),donnees,champs
            nChamp=int(sChamp.group(1))-1
            result+=champs[nChamp]
        else:
            result+=chunk
    return result

class XMLClozes:
    '''
    Conteneur pour une série d'exercices d'une même catégorie
    '''
    def __init__(self,category):
        self.category=category
        self.exercices=[]
    
    def addExercice(self,exercice):
        self.exercices.append(exercice)
    
    def getClozes(self):
        def makeExerciceStructure(exercice):
            exerciceStructure=[ 
                u'<question type="cloze">',
                    u'<name><text>%s</text></name>'%exercice.titre,
                    u'<questiontext><text><![CDATA[%s]]></text></questiontext>'%"\n".join(exercice.enonce),
                    u'<generalfeedback><text>Bien reçu.</text></generalfeedback>',
                    u'<shuffleanswers>1</shuffleanswers>',
                u'</question>'
                ]
            return u"\n".join(exerciceStructure)
                
        categoryStructure=[u'<question type="category">',
                            u'<category>',
                                u'<text>',
                                    self.category,
                                u'</text>',
                            u'</category>',
                        u'</question>'
                        ]
        result=u"\n".join(categoryStructure)
        for exercice in self.exercices:
          result+=makeExerciceStructure(exercice)
        return result

class ClozeSerie:
    '''
    Conteneur pour les éléments d'une série d'exercices Cloze
    
    L'initialisation demande la structure des boucles et de la conclusion 
    La structure est une liste de TXT,SA,SAC,MC,MCV,MCH
    '''
    def __init__(self,sBoucle,sConclusion):
        self.sBoucle=sBoucle
        self.sConclusion=sConclusion
        self.reponsesBoucles={}
        self.reponsesConclusions={}
        self.exercices=[]
        self.mcBoucles=[]
        self.mcConclusions=[]
        for index, element in enumerate(sBoucle):
            if element in choixMultiples:
                self.mcBoucles.append(index)
        for index, element in enumerate(sConclusion):
            if element in choixMultiples:
                self.mcConclusions.append(index)
        
    
    def addExercice(self,exercice):
        '''
        Stocker les ensembles de réponses et les possibilités pour chaque position
        '''
        self.exercices.append(exercice)
        boucle=exercice[0]
        conclusion=exercice[1]
        print boucle,conclusion
        for reponses in boucle:
            for index in self.mcBoucles:
                if not index in self.reponsesBoucles:
                    self.reponsesBoucles[index]=set()
                self.reponsesBoucles[index].add(reponses[index])
        for index in self.mcConclusions:
            if not index in self.reponsesConclusions:
                self.reponsesConclusions[index]=set()
            self.reponsesConclusions[index].add(conclusion[index])
        
    def makeSerie(self):
        for ligne in consigne.getConsigne(*element):
            self.exercice.append(ligne)
            
    

class ClozeExercice:
    '''
    Conteneur pour un exercice Cloze
    
    on fournit le titre et les éléments à insérer tout prêts
    
    boucles contient les éléments Cloze préparés pour l'insertion
    conclusion également
    '''
    def __init__(self,titre):
        self.titre=titre
        self.elements=[]
        self.exercice=[]
        self.enonce=""
    
    def addElement(self,boucles,conclusion,consigne):
        self.elements.append((boucles,conclusion))
        for ligne in consigne.getConsigne(boucles,conclusion):
            self.exercice.append(ligne)

class ClozeConsigne:
    '''
    Conteneur pour la consigne d'un exercice Cloze
    
    globalWrap donne un cadre pour l'ensemble de l'exercice qui apparaît tout
        en haut et tout en bas
    boucleWrap donne un cadre pour les boucles qui apparaît au début et 
        à la fin de chaque boucle
    conclusion donne une question sur l'ensemble avec un cadre
    
    consignes donne le contenu de la question des boucles
    
    dans consignes comme dans conclusion, les arguments sont repérés par #num#
    '''
    def __init__(self,consignes,**kwargs):
        self.boucle=consignes

        if "globalWrap" in kwargs:
            self.headerGlobal=kwargs["globalWrap"][0]
            self.trailerGlobal=kwargs["globalWrap"][1]
            self.globalWrap=True
        else:
            self.headerGlobal=[]
            self.trailerGlobal=[]
            self.globalWrap=False
            
        if "boucleWrap" in kwargs:
            self.headerBoucle=kwargs["boucleWrap"][0]
            self.trailerBoucle=kwargs["boucleWrap"][1]
            self.boucleWrap=True
        else:
            self.headerBoucle=[]
            self.trailerBoucle=[]
            self.boucleWrap=False
            
        if "conclusion" in kwargs:
            self.headerConclusion=kwargs["conclusion"][0]
            self.conclusion=kwargs["conclusion"][1]
            self.trailerConclusion=kwargs["conclusion"][2]
            self.conclusionWrap=True
        else:
            self.conclusion=[]
            self.headerConclusion=[]
            self.trailerConclusion=[]
            self.conclusionWrap=False
    
    def getConsigne(self,lignes,conclusion=""):
        result=[]
        if self.globalWrap:
            result.append(self.headerGlobal)
        if not isinstance(lignes,list):
            lignes=[lignes]
        for ligne in lignes:
            if self.boucleWrap:
                result.append(self.headerBoucle)
            for element in self.boucle:
                result.append(makeChamps(element,ligne))
            if self.boucleWrap:
                result.append(self.trailerBoucle)
        if conclusion!="" and self.conclusionWrap:
            result.append(self.headerConclusion)
            for element in self.conclusion:
                result.append(makeChamps(element,conclusion))
            result.append(self.trailerConclusion)
        if self.globalWrap:
            result.append(self.trailerGlobal)
        return result



class MoodleXML:
    def __init__(self):
        self.header=[u'<?xml version="1.0" encoding="UTF-8"?>',u'<quiz>']
        self.trailer=[u'</quiz>']
        self.quizzes=[]
    def addQuiz(self,quiz):
        self.quizzes.append(quiz)
    def addQuizzes(self,quizzes):
        for quiz in quizzes:
            self.addQuiz(quiz)
    def getXML(self):
        result=u"\n".join(self.header)+u"\n"+u"\n".join(self.quizzes)+u"\n"+u"\n".join(self.trailer)
        return result
