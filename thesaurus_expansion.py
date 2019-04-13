from nltk.corpus import wordnet as wn
from search_utils import *
from boolean_operations import orPosIndex
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()
class ThesaurusTermWrapper():
    '''
    A term wrapper that allows us to perform operations on similar terms
    '''
    def __init__(self, term, context = None):
        self.stemmedTerm = stemmer.stem(term)
        self.context = context
        self.similarTerms = set()
        self.expandTerm(term)

    def expandTerm(self, term):
        synsets = wn.synsets(term)
        filteredWords = set()
        for synset in synsets:
            #filteredWords.add(stemmer.stem(synset.name().split()[0]))
            for lemma in synset.lemmas():
                filteredWords.add(stemmer.stem(lemma.name()))

        self.similarTerms = filteredWords
        #print self.similarTerms
    def generatePostingsList(self, term_dict, postings):
        expandedTermSet = set()
        postingsList = loadPostingList(self.stemmedTerm, term_dict, postings)

        #Prepare first docList
        expandedPostingsList = [[item[0], item[1], item[2]]for item in postingsList]
        #print len(expandedPostingsList)
        for term in self.similarTerms:
            expandedPostingsList = orPosIndex(expandedPostingsList, loadPostingList(term, term_dict, postings))
        #print len(expandedPostingsList)
        #for posting in expandedPostingsList:
            #posting
        return expandedPostingsList

    def generateDocumentFrequency(self, term_dict):
        docFreq = filterHighIdf(self.stemmedTerm, term_dict)
        count = 1
        for word in self.similarTerms:
            count += 1
            docFreq += filterHighIdf(word, term_dict)
        return docFreq/count if docFreq/count > 0 else 1
