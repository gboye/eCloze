# -*- coding: utf8 -*-

import re
import random, math

choixMultiples=["MC","MCV","MCH"]
choixSimples=["SA","SAC","SACV"]
choixNumeriques=["NM","NMS"]+["NM%d"%i for i in range(4)]
maxChoix=10
penalite="0.3333333"
erreur=0

debug=False

def makeChamps(chaine,champs):
    chunks=re.findall(r"(#[^#]+#|[^#]*)",chaine)
    result=""
    if debug: print chunks
    for chunk in chunks:
        sChamp=re.match("#(\d+)(;\d+)?#",chunk)
        if sChamp:
            nChamp=int(sChamp.group(1))-1
            if sChamp.group(2):
                coef=sChamp.group(2)
            else:
                coef=""
            result+=champs[nChamp].decode("utf8")+coef
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
          result+=exercice.forme
        return result

class Exercice:
  '''
  Conteneur pour un ensemble de réponses pour un exercice
  Indépendant du format de sortie (Cloze ou autre)
  '''
  def __init__(self,boucle,conclusion,titre=""):
    self.boucle=boucle
    self.conclusion=conclusion
    self.titre=titre



class ClozeSerie:
    '''
    Conteneur pour les éléments d'une série d'exercices Cloze

    L'initialisation demande la structure des boucles et de la conclusion
    La structure est une liste de TXT,SA,SAC,MC,MCV,MCH
    modif pour ajouter NM
    '''
    def __init__(self,sBoucle,sConclusion):
        self.sBoucle=sBoucle
        self.sConclusion=sConclusion
        self.reponsesBoucles={}
        self.reponsesConclusions={}
        self.exercices=[]

    def addExercice(self,exercice):
        '''
        Stocker les ensembles de réponses et les possibilités pour chaque position
        '''
        self.exercices.append(exercice)
        boucle=exercice.boucle
        conclusion=exercice.conclusion
        for reponses in boucle:
          for nStructure,structure in enumerate(self.sBoucle):
            if structure in choixMultiples:
                if not nStructure in self.reponsesBoucles:
                    self.reponsesBoucles[nStructure]=set()
                if "~=" in reponses[nStructure]:
                    for elementReponse in reponses[nStructure].split("~="):
                        self.reponsesBoucles[nStructure].add(elementReponse)
                else:
                    self.reponsesBoucles[nStructure].add(reponses[nStructure])
        for nStructure,structure in enumerate(self.sConclusion):
          if structure in choixMultiples and nStructure in range(len(conclusion)):
            if not nStructure in self.reponsesConclusions:
                self.reponsesConclusions[nStructure]=set()
            self.reponsesConclusions[nStructure].add(conclusion[nStructure])

    def getChoix(self,index,bonneReponse,section="boucle"):
#     print index,bonneReponse,section
      if section=="boucle":
        choixPossibles=self.reponsesBoucles[index].copy()
      elif section=="conclusion":
        choixPossibles=self.reponsesConclusions[index].copy()
      '''
      Si la bonne réponse correspond à plusieurs choix (séparés par "~="), il faut éliminer chacun des bons choix
      des mauvaises réponses possibles
      '''
      if "~=" in bonneReponse:
        for elementReponse in bonneReponse.split("~="):
            choixPossibles.remove(elementReponse)
      elif bonneReponse in choixPossibles:
        choixPossibles.remove(bonneReponse)
      else:
        print "Problème avec la réponse %s" % bonneReponse
      nChoix=min(maxChoix,len(choixPossibles))
      choix=random.sample(choixPossibles,nChoix)
      return bonneReponse+"~"+"~".join(choix)

    def makeSerie(self,consigne):
      result=[]
      for nExercice,exercice in enumerate(self.exercices):
        for nElement,element in enumerate(exercice.boucle):
          if debug: print nElement,element
          for nChamp, champ in enumerate(element):
            if debug: print nChamp, champ
            if nChamp < len(self.sBoucle):
              if self.sBoucle[nChamp] in choixMultiples:
                self.exercices[nExercice].boucle[nElement][nChamp]="{%d:%s:=%s}"%(1,self.sBoucle[nChamp],self.getChoix(nChamp,element[nChamp]))
              elif self.sBoucle[nChamp] in choixSimples:
                choixSimple=self.sBoucle[nChamp]
                if self.sBoucle[nChamp]=="SACV":
#                    print element[nChamp], element[nChamp].upper()
                    if element[nChamp]==element[nChamp].upper():
                        choixSimple="SAC"
                    else:
                        choixSimple="SA"
                self.exercices[nExercice].boucle[nElement][nChamp]="{%d:%s:=%s}"%(1,choixSimple,element[nChamp])
              elif self.sBoucle[nChamp] in choixNumeriques:
                choixNumerique=self.sBoucle[nChamp]
                numElement=element[nChamp]
#                print choixNumerique,numElement
                m=re.match(ur"NM([S0123])",choixNumerique)
                if m:
                  choixNumSpec=m.group(1)
                  if choixNumSpec=="S":
                    sErreur=10**math.floor(math.log(float(element[nChamp]))+math.log(erreur)-1)
                  else:
                    sErreur=10**(-int(choixNumSpec))
                else:
                  sErreur=erreur
                self.exercices[nExercice].boucle[nElement][nChamp]="{%d:%s:=%s:%f}"%(1,"NM",element[nChamp],sErreur)
            else:
              if debug: print "Champ vide",nChamp
        for nElement, element in enumerate(exercice.conclusion):
          conclusionCoefs=consigne.conclusionCoefs
          if self.sConclusion[nElement] in choixMultiples:
            self.exercices[nExercice].conclusion[nElement]="{%d:%s:=%s}"%(conclusionCoefs[nElement],self.sConclusion[nElement],self.getChoix(nElement,element,"conclusion"))
          elif self.sConclusion[nElement] in choixSimples:
            self.exercices[nExercice].conclusion[nElement]="{%d:%s:=%s}"%(conclusionCoefs[nElement],self.sConclusion[nElement],element)
          elif self.sConclusion[nElement] in choixNumeriques:
            self.exercices[nExercice].conclusion[nElement]="{%d:%s:=%s:%f}"%(conclusionCoefs[nElement],"NM",element,erreur)
        exerciceCloze=[]
        for element in consigne.getConsigne(exercice):
          if element!="":
            newElement=element
            changeCoef=re.findall(ur"{(\d+):(.*?)};(\d+)",element)
            for triplet in changeCoef:
                if debug: print triplet
                coefOrig,rep,coef=triplet
                newElement=newElement.replace(ur"{%s:%s};%s"%(coefOrig,rep,coef),ur"{%s:%s}"%(coef,rep))
            exerciceCloze.append(newElement)
        exerciceSerie=ClozeExercice(exercice.titre,"<br>\n".join(exerciceCloze))
        result.append(exerciceSerie)
      return result


class ClozeExercice:
    '''
    Conteneur pour un exercice Cloze

    on fournit le titre et le corps de la question à insérer tout prêts
    '''
    def __init__(self,titre,corps,penalty="0.3333333",shuffle=1):
        self.titre=titre
        self.corps=corps
        if penalty=="0.3333333": penalty=penalite
        exerciceStructure=[
            u'<question type="cloze">',
                u'<name><text>%s</text></name>'%self.titre,
                u'<questiontext><text><![CDATA[%s]]></text></questiontext>'%self.corps,
                u'<generalfeedback><text>Bien reçu.</text></generalfeedback>',
                u'<shuffleanswers>%d</shuffleanswers>'%shuffle,
                u'<penalty>%s</penalty>'%penalty,
            u'</question>'
            ]
        self.forme=u"\n".join(exerciceStructure)


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

    def getConsigne(self,exercice):
        result=[]
        lignes=exercice.boucle
        conclusion=exercice.conclusion
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
        if conclusion and self.conclusionWrap:
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
