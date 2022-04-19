import re
import string
import nltk
import numpy as np


class ObjectiveTest:

    def __init__(self, data, noOfQues):

        self.grammar = r"""
            KEYWORD: {<NNP>+}
                {<NNPS>+}
                {<NNP>+<NNS>*}
                {<JJ>+<NN>+}
            """
        self.summary = data
        self.noOfQues = noOfQues

    def sent_preprocessing(self, sentence): #removing punctuations from sentence
        punc_string=""
        for punctuation in string.punctuation:
            if punctuation not in ('\'','.',',','(',')'):
                punc_string += punctuation
        
        for punctuation in punc_string :
            if punctuation in sentence:
                expression = re.compile(re.escape(punctuation))
                sentence = expression.sub(" ",sentence)
                
        sentence = sentence.encode(encoding='ascii',errors= 'ignore')
        sentence = sentence.decode()       
        return sentence

    def find_keywords(self,sentence):
        keywords = list()
        chunker = nltk.RegexpParser(self.grammar)
        words = nltk.word_tokenize(sentence) #separating words from sentence
        tagged_words = nltk.tag.pos_tag(words) # finding parts of speech tags
        tree = chunker.parse(tagged_words) #searching keywords

        for subtree in tree.subtrees():
            if subtree.label() == "KEYWORD":
                keyword = ""
                for sub in subtree:
                    keyword += sub[0]
                    keyword += " "
                keyword = keyword.strip()
                keywords.append(keyword)

        for keyword in keywords:
            if keyword[0]=="'" or len(keyword)<3 or re.search("\d", keyword):
                keywords.remove(keyword)
        
        return keywords
   
    def get_QuestionAnswer_pair(self, sentence):       
        sent_clean = self.sent_preprocessing(sentence)

        if len(nltk.word_tokenize(sent_clean)) < 4:
            return None
        
        keywords = self.find_keywords(sent_clean)        
        length = len(keywords)
        if length == 0:
            return None
        elif length == 1:
            replace_phrase = keywords[0]
        elif length>1:
            rand_num = np.random.randint(0, length) #selecting a random keyword
            replace_phrase = keywords[rand_num]       

        expression = re.compile(replace_phrase,re.IGNORECASE)
        if expression.search(sentence) == None:
            return None
        
        question_answer_pair = {
            "Answer": replace_phrase
        }
        
        blank_phrase = "__________"
        expression = re.compile(re.escape(replace_phrase), re.IGNORECASE)
        sentence = expression.sub(blank_phrase, str(sentence), count=1) #replacing keyword with blank spaces
        question_answer_pair["Question"] = sentence
        return question_answer_pair

    def get_QuestionAnswer(self):
        sentences = nltk.sent_tokenize(self.summary)
        question_answer = list()
        for sentence in sentences:
            question_answer_pair = self.get_QuestionAnswer_pair(sentence)
            if question_answer_pair:
                question_answer.append(question_answer_pair)
            else:
                continue
        return question_answer


    def generate_test(self):
        question_answer = self.get_QuestionAnswer()       
        question = list()
        answer = list()

        if len(question_answer)<int(self.noOfQues) and len(question_answer)!=0:
            question.append("1 : Only "+str(len(question_answer))+" Questions Generated.")
            answer.append(" ")
        
        if len(question_answer)==0:
            question.append("No Questions Generated. Try using another text.")
            answer.append(" ")
        elif len(question_answer)<=int(self.noOfQues):
            for i in range(0,len(question_answer)):
                question.append(question_answer[i]["Question"])
                answer.append(question_answer[i]["Answer"])
        else:
            while len(question) < int(self.noOfQues):
                rand_num = np.random.randint(0, len(question_answer))
                if question_answer[rand_num]["Question"] not in question:
                    question.append(question_answer[rand_num]["Question"])
                    answer.append(question_answer[rand_num]["Answer"])
                else:
                    continue


        return question, answer
