# -*- coding: utf8 -*-

import re
    
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
        self.boucles={}
        self.conclusions={}
    
    def addExercice(self,exercice):
        self.exercices.append(exercice)
        for element in exercice.elements:
          boucles=element[0]
          conclusion=element[1]
          for boucle in boucles:
            for index, valeur in enumerate(boucle):
              if not index in self.boucles:
                self.boucles[index]=set()
              self.boucles[index].add(valeur)
          for index, valeur in enumerate(conclusion):  
            if not index in self.conclusions:
              self.conclusions[index]=set()
            self.conclusions[index].add(valeur)
    
    def getClozes(self):
        def makeExerciceStructure(exercice):
            exerciceStructure=[ 
                u'<question type="cloze">',
                    u'<name><text>%s</text></name>'%exercice.titre,
                    u'<questiontext><text><![CDATA[%s]]></text></questiontext>'%"\n".join(exercice.exercice),
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

class ClozeExercice:
    '''
    Conteneur pour les éléments d'un exercice Cloze
    '''
    def __init__(self,titre):
        self.titre=titre
        self.elements=[]
        self.exercice=[]
    
    def addElement(self,element,consigne):
        self.elements.append(element)
        for ligne in consigne.getConsigne(*element):
            self.exercice.append(ligne)

class ClozeConsigne:
    '''
    Conteneur pour la consigne d'un exercice Cloze
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
