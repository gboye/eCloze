# -*- coding: UTF-8 -*-

#########################IMPORTS############################################
import re
import sys, codecs, optparse, glob, os
import string
import random
#########################CONSTANTS##########################################
xml_head_deb = [
    u'<?xml version="1.0" encoding="UTF-8"?>',
    u'<quiz>',
    u'',
    u'<question type="category">',
    u'<category>',
    u'<text>'
    ]
    

xml_head_fin = [   
    u'</text>',
    u'</category>',
    u'</question>'
        ]

trailer = [
    u'</quiz>'
        ]

entete_question = []
trailer_exercice =[]


#########################VARIABLES##########################################
xml_lignes=[]
categorie = u'test/clozexml'
header=[]
entete=[]
debug=0
debug_now=1
lines=[]
nb_champs=0
nb_champs_ex=0
indices=[]
indices_cloze=[]
indices_cloze_ex=[]
nb_indices=0
nb_indices_cloze=0
nb_indices_cloze_ex=0
liste=0
aleatoire=0
champ=[]
champ_ex=[]
###ql=range(0,20)
###reponse=range(0,20)
titre=u""
titre_ex=u""
questions=[]
trailer_question=[]
choix=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
general_feedback=u'Bien reçu.'
shuffle_answers=0
max_choices=32

#########################FUNCTIONS##########################################
def stderrprint(chaine):
        sys.stderr.write(chaine+u"\n")

def init_liste(n):
    liste=[]
    for i in range(n):
        liste.append(u'')
    return liste

def add_entete():
    for ligne in header:
        xml_lignes.append(ligne)
        
def add_sortie():
    for ligne in trailer:
        xml_lignes.append(ligne)

def add_debut_question(question):
    xml_lignes.append(u'<!-- question: %s  -->' % unicode(question))
    xml_lignes.append(u'<question type="cloze">')
    xml_lignes.append(u'<name><text>%s</text>' % (make_line(nom_question)))
    xml_lignes.append(u'</name>')
    xml_lignes.append(u'<questiontext>')
    xml_lignes.append(u'<text><![CDATA[')
    for l in entete_question:
        xml_lignes.append(make_line(l)+u'<br>')
    for l in trailer_question:
        xml_lignes.append(make_line(l)+u'<br>')
    xml_lignes.append(u'<br>')

def add_fin_question():
    xml_lignes.append(u'%s<br><br>]]></text>' % make_line(u" ".join(trailer_exercice)))
    xml_lignes.append(u'</questiontext>')
    xml_lignes.append(u'<generalfeedback>')
    xml_lignes.append(u'<text>%s</text>' % general_feedback)
    xml_lignes.append(u'</generalfeedback>')
    xml_lignes.append(u'<shuffleanswers>%s</shuffleanswers>' % unicode(shuffle_answers))
    xml_lignes.append(u'</question>')

def make_line(ligne):
    global indices
    result=ligne
    result=result.replace(u"#T#",titre_ex)
    if titre.startswith(u"RND,"):
        result=result.replace(u"#0#",titre)
    else:
        result=result.replace(u"#0#",titre)
    for i in range(0,nb_champs):
        result=result.replace(u"#"+unicode(i+1)+u"#",champ[i])
        if debug: print i, champ[i], result
    for i in range(0,nb_champs_ex):
        result=result.replace(u"#EX"+unicode(i+1)+u"#",champ_ex[i])
        if debug: print i, champ_ex[i], result
    if debug: print nb_lignes, nb_champs, i, result
    return result

def escape(chaine):
    chaine=chaine.replace(u'}',u'\\}')
    chaine=chaine.replace(u'#',u'\\#')
    chaine=chaine.replace(u'/',u'\\/')
    if u"=" in chaine and u"~=" not in chaine:
        chaine=chaine.replace(u'=',u'\\=')
    return chaine

def make_champ(texte,index):
    texte=escape(texte)
    if cloze[index] in [u"SA", u"SAC"]:
        champ[index]=u"{1:"+cloze[index]+u":="+texte+u"}"
    elif cloze[index] in [u"TXT"]:
        champ[index]= texte
    elif cloze[index] in [u"MC",u"MCH",u"MCV"]:
        if u"~" in texte:
            tamp=score_individuel(texte)
        else:
            tamp={texte:u"="}
        choixi=choix[index][:]
        ########################################################
        #
        # PROBLEME AVEC ECAMPUS : LES MC SONT LIMITES EN NOMBRE DE CHOIX Y COMPRIS LES BONNES REPONSES
        #     
        #
        ########################################################
        if len(choixi)>max_choices:
            nbonnes=len(tamp)
            choixi=[choixi[k] for k in sorted(random.sample(xrange(len(choixi)), max_choices-nbonnes)) if choixi[k] not in tamp]
            for k in tamp: choixi.append(k)
        liste_choix=choixi
        liste_choix.sort()
        result=u""
        for rep in liste_choix:
            if debug: print u"REP",rep
#            if rep==texte : result=result+"~="+rep
            if rep in tamp : result=result+u"~"+tamp[rep]+rep
            else:
                result=result+u"~"+rep
        result=result[1:]
        champ[index]=u"{1:"+cloze[index]+u":"+result+u"}"
    else:
        champ[index]=u"************************"

def add_champ(question):
    tampon=(question.strip()).split(u';')
    if debug: print tampon
    for i in range(liste,len(cloze)):
        if debug: print tampon[i], i, cloze[i]
        if i<len(tampon): make_champ(tampon[i],i)
        else: champ[i]=u""

def add_question(question):
    global indices
    tampon=(question.strip()).split(u';')
    if cloze[0] in [u"LST",u"RND"]:
        if cloze[0] in [u"RND"]:
            if nb_indices_cloze==0 and tampon[0].isdigit():
                nb_indices=int(tampon[0])
            elif tampon[0].startswith(u"RND,"):
                nb_indices=int(tampon[0].split(u',')[1])
            elif nb_indices==0 :
                nb_indices=3
            if debug: print u"nb_indices :",nb_indices
            indices=random.sample(xrange(len(cloze)), nb_indices)
        elif cloze[0] in [u"LST"]:
            liste_champs=tampon[0].split(u',')
            if nb_indices_cloze>0 and not liste_champs[0] in (u"RND",u"LST"):
                if debug: print u"liste_champs :", liste_champs, nb_indices_cloze, indices_cloze,
                indices=indices_cloze[:]
            elif liste_champs[0]==u"RND":
                indices=random.sample(xrange(1,len(cloze)), int(liste_champs[1]))
                if debug: print u"indices :", indices
            elif liste_champs[0]==u"LST":
                indices=[int(k) for k in range(1,len(liste_champs))]
#                nb_indices=len(liste_champs)-1
            else:    
                indices=[int(k) for k in liste_champs]
            nb_indices=len(indices)
            if debug: print u"cloze0 :", cloze[0], nb_indices, indices
        for i in range(1,len(cloze)):
            if i in indices:
                cloze[i]=u"TXT"
            else:
                cloze[i]=u"SAC"
    if debug: stderrprint(u"%s et %s" %(len(tampon), nb_indices))
    add_champ(question)
    if debug: print tampon
    for i in range(0,nb_lignes):
        xml_lignes.append(make_line(questions[i])+u"<br>")

def scores_multiples(scores):
    if debug: print u"SCORES", scores
    tamp=scores.split(u'~')
    result=[]
    for texte in tamp:
        if texte[0]==u"=":
            result.append(texte[1:])
            if debug: print result, texte[1:]
        elif texte[0]==u"%":
            debut=texte.find(u'%',1)
            result.append(texte[debut:])
            if debug: print result, texte[debut:]
        else:
            result.append(texte)
            if debug: print result, texte
    return result

def score_individuel(scores):
    if debug: print u"SCORES", scores
    tamp=scores.split(u'~')
    result={}
    for texte in tamp:
        if texte[0]==u"=":
            result[texte[1:]]=u"="
            if debug: print u"=", result, texte[1:]
        elif texte[0]==u"%":
            debut=texte.find(u'%',1)
            result[texte[debut:]]=texte[0:debut]
            if debug: print u"%", result, texte[debut:]
        else:
            result[texte]=u"="
            if debug: print u"DIRECT", result, texte
    return result

def add_choix(ligne):
    tampon=(ligne.strip()).split(u';')
    if debug: print tampon,len(tampon),len(cloze)
    for i in range(liste,len(cloze)):
        if debug: print i, tampon[i], cloze[i], choix[i]
        tamp=[]
        t=u""
        if cloze[i] in [u"MC",u"MCH",u"MCV"]:
            if u"~" in tampon[i]:
                if debug: print u"~"
                tamp.extend(scores_multiples(tampon[i]))
            else:
                tamp.append(tampon[i])
            for texte in tamp:
                texte=escape(texte)
                if texte not in choix[i]: choix[i].append(texte)
                if debug: print cloze[i], tampon[i], texte, choix[i]

def supprime_debut(ligne,entete):
    longueur=len(entete)
    result=ligne[longueur:]
    return result

def parser_ligne(line):
    result=[]
    extract=re.findall(ur"[^;]*<[^>]+>[^;]*;|[^;]*;", line)
    for element in extract:
        result.append(element.strip(u";"))
    return result

def choisir_fichier(default=u"."):
    for file in glob.glob(default):
        print file
    return raw_input(u"Fichier exercice : ")

################
#
# LECTURE DU FICHIER DE DONNEES
#
# PHRASES
# AMORCE;SYNTAGME;FONCTION;MOTS
# AMORCE;SYNTAGME;FONCTION;MOTS
# AMORCE;SYNTAGME;FONCTION;MOTS
#
# PHRASES
# AMORCE;SYNTAGME;FONCTION;MOTS
# AMORCE;SYNTAGME;FONCTION;MOTS
# ...
#
#                LES LIGNES QUI COMMENCENT PAR # SONT IGNOREES
#
################
parser=optparse.OptionParser()
parser.add_option("-f", "--file", dest="outfile", action="store_true", help="write to FILE")
parser.add_option("-c", "--choose", dest="choose", action="store_true", help="choose an exercice file")


(options, args) = parser.parse_args()

if options.choose:
    if len(args) !=0:
        print u'No argument with CHOOSE'
        sys.exit()
    else:
        ex_file_name=choisir_fichier(u"*.txt")
else:     
    if len(args) != 1:
        print u'Please provide an exercise file'
        sys.exit()
    ex_file_name=args[0]

try:
        ex_file=codecs.open(ex_file_name,"r","utf-8") 
except IOError:
        print u'I could not open the question file', args[0]
        sys.exit()


if options.outfile:
    if ex_file_name.endswith(u".txt"):
        xml_file_name=ex_file_name[:-4]+u".xml"
    else:
        xml_file_name=ex_file_name+u".xml"
    try:
            xml_file=codecs.open(xml_file_name,"w","utf-8") 
    except IOError:
            print u'I could not open the tree file', options.outfile
            sys.exit()


fichier=ex_file.readlines()
ex_file.close()

##################################
#
#    PREPARER LES CHAMPS, LES QUESTIONS, LES REPONSES
#
##################################
champ=init_liste(20)
cloze=[]
cloze_ex=[]

for line in fichier:
    tampon=line.strip().strip(u";")+u";"
    if tampon.startswith(u"#"):
        if debug: print tampon
#        mots=tampon.split(';')
        mots=parser_ligne(tampon)
        if mots[0]==u"#CAT":
            if debug: print u"#CAT"
            nom_question=mots[1]
            categorie=mots[2]
            header.append(categorie)
        elif mots[0] in [u"#ENTETE",u"#HEAD",u"#DEBUT"]:
            entete_question.append(supprime_debut(tampon,mots[0]+u";").strip(u";"))
        elif mots[0] in [u"#QUEUE",u"#TRAILER",u"#FIN"]:
            trailer_exercice.append(supprime_debut(tampon,mots[0]+u";").strip(u";"))
        elif mots[0]==u"#QUESTION":
            questions.append(supprime_debut(tampon,u"#QUESTION;").strip(u";"))
#        elif mots[0]=="#INDICES":
#            nb_indices=int(mots[1])
#            if debug: print "INDICES", nb_indices, mots, len(mots)
        elif mots[0]==u"#CLOZE":
            nb_champs=len(mots)-1
            cloze=range(0,nb_champs)
            if debug: print u"CLOZE", nb_champs, mots, len(mots)
            for i in range(1,len(mots)):
                if mots[i].startswith(u"RND"):
                    aleatoire=1
                    sous_champs=mots[i].split(u',')
                    cloze[i-1]=sous_champs[0]
                    if len(sous_champs)==2:
                        nb_indices=int(sous_champs[1])
                    if debug: print u"RND", cloze[i-1], nb_indices
                elif mots[i].startswith(u"LST"):
                    liste=1
                    sous_champs=mots[i].split(u',')
                    if debug: print u"sous_champs :", sous_champs
                    if len(sous_champs)>1:
                        nb_indices_cloze=len(sous_champs)-1
                        indices_cloze=[int(k) for k in sous_champs[1:nb_indices_cloze+1]]
                    cloze[i-1]=sous_champs[0]
                    if debug: print u"LST", cloze[i-1], nb_indices_cloze, indices_cloze
                else:
                    cloze[i-1]=mots[i]
        elif mots[0]==u"#CLOZE_EX":
            nb_champs_ex=len(mots)-1
            cloze_ex=range(0,nb_champs_ex)
            if debug: print u"CLOZE_EX", nb_champs_ex, mots, len(mots)
            for i in range(1,len(mots)):
                if mots[i].startswith(u"RND"):
                    aleatoire=1
                    sous_champs=mots[i].split(u',')
                    cloze_ex[i-1]=sous_champs[0]
                    if len(sous_champs)==2:
                        nb_indices=int(sous_champs[1])
                    if debug: print u"RND", cloze_ex[i-1], nb_indices
                elif mots[i].startswith(u"LST"):
                    liste=1
                    sous_champs=mots[i].split(u',')
                    if debug: print u"sous_champs :", sous_champs
                    if len(sous_champs)>1:
                        nb_indices_cloze_ex=len(sous_champs)-1
                        indices_cloze_ex=[int(k) for k in sous_champs[1:nb_indices_cloze_ex+1]]
                    cloze_ex[i-1]=sous_champs[0]
                    if debug: print u"LST", cloze_ex[i-1], nb_indices_cloze_ex, indices_cloze_ex
                else:
                    cloze_ex[i-1]=mots[i]
    else:
        add_choix(line)

nb_lignes=len(questions)

if debug:
    for i in choix:
        stderrprint (unicode(len(i)))
        print u"NUM", choix.index(i)
        for j in i:
            print u"\t"+j
    for question in questions: print question
    print champ
    print cloze

##################################
#
#    PREPARER L'ENTETE XML ET L'IMPRIMER
#
##################################

header=xml_head_deb
header.append(categorie)
header.extend(xml_head_fin)
add_entete()

##################################
#
#    LIRE LE FICHIER QUESTIONS
#        LES BALISES #EX MARQUENT LE DEBUT D'UNE QUESTION CLOZE COMPOSEE DE QUESTIONS UNITAIRES
#        CHAQUE LIGNE NORMALE EST UNE INSTANCE DE QUESTION UNITAIRE
#
##################################

question=0
debut_question=0
for line in fichier:
    tampon=line.strip().strip(u";")+u";"
    if tampon.startswith(u"#"):
        if debug: print tampon
#        mots=tampon.split(';')
        mots=parser_ligne(tampon)
        if mots[0]==u"#EX":
            if debug: print u"#EX"
            champ_ex=init_liste(20)
            if len(mots)>1:
                titre_ex=mots[1]
                for i in range(1,len(mots)):
                    champ_ex[i-1]=mots[i]
            if question>0: add_fin_question()
            question=question+1
            debut_question=1
            trailer_question=[]
            titre=u""
        elif mots[0]==u"#TITRE":
            if debug: print u"#TITRE"
            titre_ex=supprime_debut(tampon,u"#TITRE;").strip(u";")
        elif mots[0] in [u"#SPEC",u"#ENTETE_EX",u"#DEBUT_EX"]:
            if debug: print mots[0]
            trailer_question.append(supprime_debut(tampon,mots[0]+u";"))
    elif (len(tampon)==0 or tampon==u";"):
        if debug: print u"ligne vide"
    else:
        if debut_question:
#            mots=tampon.split(';')
            mots=parser_ligne(tampon)
            add_champ(line)
            if titre==u"": titre=mots[0]
            add_debut_question(question)
            debut_question=0
        add_question(line)


debut=0
fin=0
question=0
for line in lines:
    if line==u"":
        fin=1
        debut=0
    elif debut==0:
        question=question+1
        if fin==1:
            add_fin_question()
        add_debut_question(question,line)
        debut=1
        fin=0
    else:
        add_question(line)

add_fin_question()        
add_sortie()

for ligne in xml_lignes:
    if options.outfile:
        xml_file.write(ligne+u"\n")
    else:
        print ligne
