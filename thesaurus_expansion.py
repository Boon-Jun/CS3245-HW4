from nltk.corpus import wordnet as wn
from search_utils import *
from boolean_operations import orV2
from nltk.tokenize import word_tokenize
from nltk.wsd import lesk
from nltk import pos_tag

class ThesaurusTermWrapper():
    '''
    A term wrapper that allows us to perform operations on similar terms
    '''
    termDictionary = {}
    def __init__(self, term, context = None):
        if term in self.__class__.termDictionary:
            #Load from termDictionary, if term has already been expanded previously within the query
            self.term = self.__class__.termDictionary[term].term
            self.similarTerms = self.__class__.termDictionary[term].similarTerms
            self.documentFreq = self.__class__.termDictionary[term].documentFreq
            self.collectionTermFreq = self.__class__.termDictionary[term].collectionTermFreq
            self.postingsList = self.__class__.termDictionary[term].postingsList
        else:
            self.term = term
            self.similarTerms = None
            self.documentFreq = None
            self.collectionTermFreq = None
            self.postingsList = None
            self.expandTerm(term, context)
            self.__class__.termDictionary[self.term] = self

    def expandTerm(self, term, context = None):
        if self.similarTerms == None:
            filteredWords = set()
            tagged_terms = []
            POS = None
            if context != None:
                tagged_terms = pos_tag(context)

        #Update part of speech
            for item in tagged_terms:
                if term == item[0]:
                    if item[1][0] == 'J':
                        POS = 'a'
                    elif item[1][0] == 'N':
                        POS = 'n'
                    elif item[1][0] == 'V':
                        POS = 'v'
                    elif item[1][0] == 'R':
                        POS = 'r'
                        break

            '''
            #This was used when we were previously generating similar words without Lesk algorithm
            if POS != None:
                synsets = wn.synsets(term, POS)
                for synset in synsets:
                    for lemma in synset.lemmas():
                        filteredWords.add(stemmer.stem(lemma.name()))
            '''
            if context != None:
                #Find similar words with Lesk algorithm
                synset = lesk(context, term, pos = POS)
                if synset is not None:
                    for lemma in synset.lemmas():
                        filteredWords.add(lemma.name())

            self.similarTerms = filteredWords
            self.__class__.termDictionary[self.term] = self

    def generatePostingsList(self, term_dict, postings):
        # Returns a merged postings list of the original term and
        # the other terms similar(synonymous) to it.
        if self.postingsList == None:
            expandedTermSet = set()
            postingsList = loadPostingList(self.term, term_dict, postings)

            expandedPostingsList = [[item[0], item[1], item[2]]for item in postingsList]
            for term in self.similarTerms:
                expandedPostingsList = orV2(expandedPostingsList, loadPostingList(term, term_dict, postings))
            for posting in expandedPostingsList:
                posting[2].sort()

            self.postingsList = expandedPostingsList
            self.__class__.termDictionary[self.term] = self
        return self.postingsList

    def generateDocumentFrequency(self, term_dict):
        #generates average document frequency(number of documents with these terms)
        if self.documentFreq == None:
            docFreq = getDocFrequency(self.term, term_dict)
            count = 1
            for word in self.similarTerms:
                count += 1
                docFreq += getDocFrequency(word, term_dict)
            self.documentFreq = docFreq * 1.0/count if docFreq * 1.0/count > 0 else 1
            self.__class__.termDictionary[self.term] = self
        return self.documentFreq

    def generateCollectionTermFrequency(self, term_dict):
        #Generates average collection frequency(number of terms in the whole collection)
        #Used for Ranking with Language Model. Unused in actual implementation
        if self.collectionTermFreq == None:
            colFreq = getCollectionFrequency(self.term, term_dict)
            count = 1
            for word in self.similarTerms:
                count += 1
                colFreq += getCollectionFrequency(word, term_dict)
            self.collectionTermFreq = colFreq * 1.0/count
            self.__class__.termDictionary[self.term] = self
        return self.collectionTermFreq

    @classmethod
    def clearTermStorage(cls):
        #Used for clearing termDictionary after a query
         cls.termDictionary.clear()
