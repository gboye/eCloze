# -*- coding: utf8 -*-

import re, warnings
import random as rd

choixMultiples=["MC","MCV","MCH","MCS"]
choixSimples=["SA","SAC","SACV"]
maxChoix=10
penalite="0.3333333"

debug=False

def makeChamps(chaine,champs):
    chunks=re.findall(r"(#[^#]+#|[^#]*)",chaine)
    result=""
    for chunk in chunks:
        sChamp=re.match("#(\d+)#",chunk)
        if sChamp:
            nChamp=int(sChamp.group(1))-1
            result+=champs[nChamp].decode("utf8")
        elif "#N#" in chunk:
            nAlea="%04d"%rd.randint(1,10000)
            result+=chunk.replace("#N#",nAlea)
        else:
            result+=chunk
    return result


class XMLSeries:
    '''
    Conteneur pour une série d'exercices d'une même catégorie
    '''
    def __init__(self,category):
        self.category=category
        self.exercices=[]
        self.questiontext=set()
        self.content=[]

    def addExercice(self,exercice):
        if not exercice.forme in self.content:
            self.content.append(exercice.forme)
            self.exercices.append(exercice)

    def getSeries(self):
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

class XMLSubCategory:
    '''
    balise de sous-catégorie
    '''
    def __init__(self,category):
        self.category=category

        categoryStructure=[u'<question type="category">',
                            u'<category>',
                                u'<text>',
                                    self.category,
                                u'</text>',
                            u'</category>',
                        u'</question>'
                        ]
        self.forme=u"\n".join(categoryStructure)



class Essay:
    '''
    Conteneur pour un exercice Essay

    on fournit le titre et le corps de la question à insérer tout prêts
    '''
    def __init__(self,titre,consigne,responsefieldlines=20):
        self.titre=titre
        self.consigne=consigne
        exerciceStructure=[
            u'<question type="essay">',
                u'<name><text>%s</text></name>'%titre,
                u'<questiontext><text><![CDATA[%s]]></text></questiontext>'%consigne,
                u'<generalfeedback><text>Bien reçu.</text></generalfeedback>',
                u'<responseformat>editor</responseformat>',
                u'<responserequired>1</responserequired>',
                u'<responsefieldlines>%s</responsefieldlines>'%responsefieldlines,
                u'</question>'
                ]
        self.forme=u"\n".join(exerciceStructure)


class DragDropImage:
    '''
    Conteneur pour un exercice DragDrog

    on fournit le titre et le corps de la question à insérer tout prêts
    '''
    def __init__(self,titre,consigne,image,pieces,penalty="0.3333333",shuffle=1,drag="text"):
        self.titre=titre
        self.consigne=consigne
        self.image=image
        self.pieces=pieces
        if penalty=="0.3333333": penalty=penalite
        exerciceStructure=[
            u'<question type="ddimageortext">',
                u'<name><text>%s</text></name>'%titre,
                u'<questiontext><text><![CDATA[%s]]></text></questiontext>'%consigne,
                u'<generalfeedback><text>Bien reçu.</text></generalfeedback>',
                u'<shuffleanswers>%d</shuffleanswers>'%shuffle,
                u'<penalty>%s</penalty>'%penalty,
                u'<file name="%s" encoding="base64">%s</file>'%(titre,image)
                ]
        dragPieces=[]
        dropPieces=[]
        if drag=="text":
            for num,piece in enumerate(pieces):
                dragPiece=[
                    '<drag>',
                        '<no>%d</no>'%(num+1),
                        '<text>%s</text>'%piece["drag"],
                        '<draggroup>1</draggroup>',
                    '</drag>'
                    ]
                dragPieces.extend(dragPiece)
                dropPiece=[
                    '<drop>',
                        '<text></text>',
                        '<no>%d</no>'%(num+1),
                        '<choice>%d</choice>'%(num+1),
                        '<xleft>%s</xleft>'%piece["drop"][0],
                        '<ytop>%s</ytop>'%piece["drop"][1],
                    '</drop>'
                    ]
                dropPieces.extend(dropPiece)
        elif drag=="image":
            for num,piece in enumerate(pieces):
                dragPiece=[
                    '<drag>',
                        '<no>%d</no>'%(num+1),
                        '<text></text>',
                        '<file name="%s" encoding="base64">%s</file>'%(titre+'-%02d'%num,piece[0]),
                        '<draggroup>1</draggroup>',
                    '</drag>'
                    ]
                dragPieces.extend(dragPiece)
                dropPiece=[
                    '<drop>',
                        '<text></text>',
                        '<no>%d</no>'%(num+1),
                        '<choice>%d</choice>'%(num+1),
                        '<xleft>%s</xleft>'%piece[1][0],
                        '<ytop>%s</ytop>'%piece[1][1],
                    '</drop>'
                    ]
                dropPieces.extend(dropPiece)
        else:
            print u"type de drag non traité", drag
        exerciceStructure.extend(dragPieces)
        exerciceStructure.extend(dropPieces)
        exerciceStructure.append(u'</question>')
        self.forme=u"\n".join(exerciceStructure)

class DragDropText:
    '''
    Conteneur pour un exercice DragDrog

    on fournit le titre et le corps de la question à insérer tout prêts
    '''
    def __init__(self,titre,corps,pieces,penalty="0.3333333",shuffle=1,drag="text"):
        self.titre=titre
        self.contenu=(corps,pieces)
        if penalty=="0.3333333": penalty=penalite
        exerciceStructure=[
            u'<question type="ddwtos">',
                u'<name><text>%s</text></name>'%titre,
                u'<questiontext format="html">',
                    u'<text><![CDATA[%s]]></text>'%corps,
                u'</questiontext>',
                u'<generalfeedback><text>Bien reçu.</text></generalfeedback>',
                u'<shuffleanswers>%d</shuffleanswers>'%shuffle,
                u'<penalty>%s</penalty>'%penalty,
                ]
        dragPieces=[]
        for num,piece in enumerate(pieces):
            if drag=="text":
                dragPiece=[
                    '<dragbox>',
                        '<text>%s</text>'%piece,
                        '<group>1</group>',
                    '</dragbox>'
                    ]
            elif drag=="image":
                dragPiece=[
                    '<dragbox>',
                        '<text></text>',
                        '<file name="%s" encoding="base64">%s</file>'%(titre+'-%02d'%num,piece),
                        '<group>1</group>',
                    '</dragbox>'
                    ]
            dragPieces.extend(dragPiece)
        exerciceStructure.extend(dragPieces)
        exerciceStructure.append(u'</question>')
        self.forme=u"\n".join(exerciceStructure)


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
    La structure est une liste de TXT,SA,SAC,MC,MCV,MCH,MCS
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
      choix=rd.sample(choixPossibles,nChoix)
      return bonneReponse+"~"+"~".join(choix)

    def makeSerie(self,consigne):
      result=[]
      uniques=[]
      for nExercice,exercice in enumerate(self.exercices):
        for nElement,element in enumerate(exercice.boucle):
#          print nElement,element
          for nChamp, champ in enumerate(element):
#            print nChamp, champ
            if nChamp < len(self.sBoucle):
              if self.sBoucle[nChamp] in choixMultiples:
                self.exercices[nExercice].boucle[nElement][nChamp]="{1:%s:=%s}"%(self.sBoucle[nChamp],self.getChoix(nChamp,element[nChamp]))
              elif self.sBoucle[nChamp] in choixSimples:
                choixSimple=self.sBoucle[nChamp]
                if self.sBoucle[nChamp]=="SACV":
#                    print element[nChamp], element[nChamp].upper()
                    if element[nChamp]==element[nChamp].upper():
                        choixSimple="SAC"
                    else:
                        choixSimple="SA"
                self.exercices[nExercice].boucle[nElement][nChamp]="{1:%s:=%s}"%(choixSimple,element[nChamp])
            else:
              if debug: print "Champ vide",nChamp
        for nElement, element in enumerate(exercice.conclusion):
          if self.sConclusion[nElement] in choixMultiples:
            self.exercices[nExercice].conclusion[nElement]="{1:%s:=%s}"%(self.sConclusion[nElement],self.getChoix(nElement,element,"conclusion"))
          elif self.sConclusion[nElement] in choixSimples:
            self.exercices[nExercice].conclusion[nElement]="{1:%s:=%s}"%(self.sConclusion[nElement],element)
        exerciceCloze=[]
        for element in consigne.getConsigne(exercice):
          if element!="":
            exerciceCloze.append(element)
        corps="<br>\n".join(exerciceCloze)
        exerciceSerie=ClozeExercice(exercice.titre,corps)
        if corps in uniques :
            print nExercice,
        else:
            result.append(exerciceSerie)
            uniques.append(corps)
      return result


class RegExExercice:
    '''
    Conteneur pour un exercice RegEx

    on fournit le titre, le corps et les réponses de la question à insérer tout prêts
    '''
    def __init__(self,titre,consigne,reponses,
                 penalty="0.2000000",usehint="0",usecase="1",alternates="0",nbHints=None):
        self.titre=titre
        self.consigne="<br>".join(consigne)
        self.reponses=reponses
        regexReponses=[]
        if len(reponses)!=1:
            warnings.warn("\nPlusieurs réponses dans le RegEx\nElles seront toutes considérées correctes.")
        for reponse in reponses:
            if isinstance(reponse, basestring):
                regexReponse=[
                u'<answer fraction="100">',
                    u'<text>%s</text>'%reponse,
                u'</answer>'
                ]
            elif isinstance(reponse,(list,tuple)):
                if len(reponse)>=2:
                    if len(reponse)<3:
                        reponse.append("")
                    regexReponse=[
                        u'<answer fraction="%s">'%reponse[0],
                            u'<text>%s</text>'%reponse[1],
                            u'<feedback format="html">',
                                u'<text><![CDATA[%s]]></text>'%reponse[2],
                            u'</feedback>',
                        u'</answer>'
                    ]
            else:
                warnings.warn("\nRéponses incompréhensibles.")
            regexReponses.extend(regexReponse)

        exerciceStructure=[
            u'<question type="regexp">',
                u'<name><text>%s</text></name>'%self.titre,
                u'<questiontext><text><![CDATA[%s]]></text></questiontext>'%self.consigne,
                u'<generalfeedback><text>Bien reçu.</text></generalfeedback>',
                u'<studentshowalternate>%s</studentshowalternate>'%alternates,
                u'<usehint>%s</usehint>'%usehint,
                u'<usecase>%s</usecase>'%usecase,
                u'<penalty>%s</penalty>'%penalty,
                u"\n".join(regexReponses),
            u'</question>'
            ]
        if nbHints:
            for hintNum in range(nbHints):
                hintText='<hint format="html"><text><![CDATA[<p>Il vous reste %d essais<br></p>]]></text></hint>'%(nbHints-hintNum)
                exerciceStructure.insert(-1,hintText)
        self.forme=u"\n".join(exerciceStructure)



class ClozeExercice:
    '''
    Conteneur pour un exercice Cloze

    on fournit le titre et le corps de la question à insérer tout prêts
    '''
    def __init__(self,titre,corps,penalty="0.3333333",shuffle=1,nbHints=None):
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
        if nbHints:
            for hintNum in range(nbHints):
                hintText='<hint format="html"><text><![CDATA[<p>Il vous reste %d essais<br></p>]]></text></hint>'%(nbHints-hintNum)
                exerciceStructure.insert(-1,hintText)
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
