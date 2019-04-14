from nltk.corpus import wordnet as wn
from search_utils import *
from boolean_operations import orPosIndex
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk import pos_tag
stemmer = PorterStemmer()
class ThesaurusTermWrapper():
    '''
    A term wrapper that allows us to perform operations on similar terms
    '''
    def __init__(self, term, context = None):
        self.stemmedTerm = stemmer.stem(term)
        #print self.stemmedTerm
        self.similarTerms = set()
        self.expandTerm(term, context)

    def expandTerm(self, term, context = None):
        filteredWords = set()
        tagged_terms = []
        pos = -1
        if context != None:
            tagged_terms = pos_tag(context)

        #Update part of speech
        for item in tagged_terms:
            if term == item[0]:
                if item[1][0] == 'J':
                    pos = 'a'
                elif item[1][0] == 'N':
                    pos = 'n'
                elif item[1][0] == 'V':
                    pos = 'v'
                break

        synsets = wn.synsets(term)
        for synset in synsets:
            if synset.pos() == pos:
                for lemma in synset.lemmas():
                    filteredWords.add(stemmer.stem(lemma.name()))

        self.similarTerms = filteredWords
    def generatePostingsList(self, term_dict, postings):
        expandedTermSet = set()
        postingsList = loadPostingList(self.stemmedTerm, term_dict, postings)

        #Prepare first docList
        expandedPostingsList = [[item[0], item[1], item[2]]for item in postingsList]
        #print len(expandedPostingsList)
        for term in self.similarTerms:
            expandedPostingsList = orPosIndex(expandedPostingsList, loadPostingList(term, term_dict, postings))
        #print len(expandedPostingsList)
        for posting in expandedPostingsList:
            posting[2].sort()
        return expandedPostingsList

    def generateDocumentFrequency(self, term_dict):
        docFreq = filterHighIdf(self.stemmedTerm, term_dict)
        count = 1
        for word in self.similarTerms:
            count += 1
            docFreq += filterHighIdf(word, term_dict)
        return docFreq * 1.0/count if docFreq * 1.0/count > 0 else 1
