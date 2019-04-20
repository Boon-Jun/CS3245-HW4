from thesaurus_expansion import ThesaurusTermWrapper
from search_utils import getDocVector, getVectorLength, loadPostingList
import math

class PseudoRF():
    def __init__(self, queryVector, results):
        self.queryVector = queryVector
        self.results = results
        self.foundId = set()
        for result in results:
            self.foundId.add(result[0])

    def rocchio(self, doc_vectors, vector_lengths):
        alpha = 0.75
        beta = 0.25
        reweightedQuery = {}
        for result in self.results:
            docId = result[0]
            vector = getDocVector(docId, doc_vectors)
            for component in vector:
                if component[0] not in reweightedQuery:
                    reweightedQuery[component[0]] = 0
                reweightedQuery[component[0]] += (component[1]/getVectorLength(docId,vector_lengths))#component[1] contains tf-idf
                                                                                                     #Divide by doc_vector_length to normalize it
        for term in reweightedQuery:
            reweightedQuery[term] *= beta/len(self.results)

        for term in self.queryVector:
            if term not in reweightedQuery:
                reweightedQuery[term] = 0
            reweightedQuery[term] += self.queryVector[term] * alpha
        return reweightedQuery

    def giveFeedback(self, term_dict, postings, doc_vectors, vector_lengths):
        if len(self.results) == 0:
            #No results to generate extra feedback
            return []
        scores = {}
        reweightedQuery = self.rocchio(doc_vectors, vector_lengths)
        for term in reweightedQuery:
            if reweightedQuery[term] < 0.004:
                continue
            try:
                postingList = loadPostingList(term, term_dict, postings)
            except:
                continue
            for posting in postingList:
                docId = posting[0]
                if docId not in self.foundId:
                    if docId not in scores:
                        scores[docId] = 0
                    scores[docId] += reweightedQuery[term] * (1 + math.log10(posting[1]))

        for docId in scores:
            scores[docId] = scores[docId]/getVectorLength(docId, vector_lengths)

        feedbackResult = self.results
        generatedResult = sorted(([docId, scores[docId]] for docId in scores), key = lambda pair:(-pair[1], pair[0]))
        feedbackResult.extend(generatedResult)

        return feedbackResult
