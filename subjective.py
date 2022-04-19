import numpy as np
import nltk
import re
import string

class SubjectiveTest:

    def __init__(self, data, noOfQues):

        self.question_pattern = [
            "Define ",
            "Write a short note on ",
        ]

        self.grammar = r"""
            KEYWORD: {<NNP>+}
                {<NNPS>+}
                {<NN>+}
                {<NNS>+}
                {<NNP>+<NNS>*}
                {<NN>+<NNP>+}
                {<JJ>+<NN>+}
            """
        self.summary = data
        self.noOfQues = noOfQues
    
    def sent_preprocessing(self, sentences): #removing punctuations from sentences, lowercasing
        punc_string=""
        for punctuation in string.punctuation:
            if punctuation not in ('\'','.',',','(',')'):
                punc_string += punctuation
        
        for sentence in sentences:
            for punctuation in punc_string :
                if punctuation in sentence:
                    expression = re.compile(re.escape(punctuation))
                    sentence = expression.sub(" ",sentence)
            sentence = sentence.lower()
        return sentences

        

    def find_keywords(self):
        sentences = nltk.sent_tokenize(self.summary)
        sentences = self.sent_preprocessing(sentences)

        parser = nltk.RegexpParser(self.grammar)
        keyword_dict={}
        
        for sentence in sentences:
            tagged_words = nltk.pos_tag(nltk.word_tokenize(sentence)) #finding parts of speech tags
            tree = parser.parse(tagged_words) #finding keywords
            
            for subtree in tree.subtrees():
                if subtree.label() == "KEYWORD":
                    keyword = ""
                    for sub in subtree:
                        keyword += sub[0]
                        keyword += " "
                    keyword = keyword.strip()
                    
                    if keyword not in keyword_dict: #finding number of occurrences of keywords
                        keyword_dict[keyword]=1
                    else:
                        keyword_dict[keyword]+=1

        del_key = list()
        for keyword in keyword_dict:
            if keyword[0]=='\'' or len(keyword)<3 or re.search("\d", keyword):
                del_key.append(keyword)
        
        for keyword in del_key:
            del keyword_dict[keyword]

        keywords= list()
        for keyword in keyword_dict: #selecting frequently occurring keywords
            if keyword_dict[keyword]>5:
                keywords.append(keyword)
        
        return keywords
    
    def generate_QuestionAnswer(self):
        keywords = self.find_keywords()
        sentences = nltk.sent_tokenize(self.summary)
        keyword_answer_dict = dict()

        for keyword in keywords:
            expression = re.compile(keyword,re.IGNORECASE)
            for sentence in sentences: #finding sentences related to keyword to form answer       
                    if expression.search(sentence)!= None:
                        if len(nltk.word_tokenize(sentence)) > 3:
                            if keyword not in keyword_answer_dict:
                                keyword_answer_dict[keyword] = sentence
                            else:
                                keyword_answer_dict[keyword] += " "+sentence
        
        question_answer = list()

        for n in range(0,len(keywords)):
            selected_key = keywords[n]
            answer = keyword_answer_dict[selected_key]
            rand_num = np.random.randint(0, len(self.question_pattern)) 
            question = self.question_pattern[rand_num] + selected_key + " from paragraph" # forming question
            question_answer.append({"Question": question, "Answer": answer})
        
        return question_answer

    def generate_test(self):      
        question_answer = self.generate_QuestionAnswer()
        question = list()
        answer = list()
        
        if len(question_answer)<int(self.noOfQues) and len(question_answer)!=0:
            question.append("")
            answer.append("1 : Only "+str(len(question_answer))+" Questions Generated.")
        
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