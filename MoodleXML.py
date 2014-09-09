class MoodleClozes:
    def __init__(self,category):
        self.category=category
        self.header= [
                    u'<question type="category">',
                        u'<category>',
                            u'<text>',
                                category,
                            u'</text>',
                        u'</category>',
                    u'</question>'
                    ]
        self.trailer=[u'']
        self.Clozes=[]
    def addQuestion(self,cloze):
        self.Clozes.append(u'<question type="cloze"><name><text>%s</text></name>'%cloze[0])
        self.Clozes.append(u'<questiontext><text><![CDATA[%s]]></text></questiontext>'%cloze[1])            
        self.Clozes.append(u'<generalfeedback><text>Bien reçu.</text></generalfeedback>\n<shuffleanswers>1</shuffleanswers>\n</question>\n')
    def addQuestions(self,clozes):
        for cloze in clozes:
            self.addQuestion(cloze)
    def getClozes(self):
        result=u"\n".join(self.header)+u"\n"+u"\n".join(self.Clozes)+u"\n"+u"\n".join(self.trailer)
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
