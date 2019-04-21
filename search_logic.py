from query_parser import queryStringToPhraseAndTermsList, phraseToTermsList, filterStopWords
from search_utils import *
import math
import heapq
import time
from operator import itemgetter
from boolean_operations import andV1, andV2
from thesaurus_expansion import ThesaurusTermWrapper
from pseudo_relevance_feedback import PseudoRF

def findDocContainingPartialPhrase(phraseTermsList, size, term_dict, postings):
    # Returns all docIds containing a partialPhrase of length 'size'
    docSet = set()
    for startPos in range(len(phraseTermsList)):
        if startPos + size <= len(phraseTermsList):
            docs_list = []
            endPos = startPos + size
            postingsList = ThesaurusTermWrapper(phraseTermsList[startPos], phraseTermsList).generatePostingsList(term_dict, postings)

            for x in range(len(postingsList)):
                docs_list.append([postingsList[x][0], list(postingsList[x][2])])

            for x in range(startPos + 1, endPos):
                docs_list = andV2(docs_list,
                    ThesaurusTermWrapper(phraseTermsList[x], phraseTermsList).generatePostingsList(term_dict, postings),
                    window = 1)
            for item in docs_list:
                docSet.add(item[0])
        else:
            break
    return docSet

def processSingleWordQuery(term, term_dict, postings, vector_lengths):
    '''
        NOTE: This function is originally used for the processing of boolean
              queries. Since we are processing all boolean queries as FreeText
              queries, this method is no longer used
        After processing single word terms returns a list of [docId, scores]
        sorted in order of increasing relevance. One document is more relevant
        than the other if it has a higher tf-idf scores
    '''
    totalNumberOfDocs = getTotalNumberOfDocs(postings)
    queryTermSet = {}
    scores = {}
    docCount = ThesaurusTermWrapper(term, None).generateDocumentFrequency(term_dict)
    tf_idf = 0
    if docCount != 0:
        #In single word terms, only need to calculate idf since tf = 1
        tf_idf = math.log10(totalNumberOfDocs/docCount)


    postingsList = ThesaurusTermWrapper(term, None).generatePostingsList(term_dict, postings)

    for posting in postingsList:
        docId = posting[0]
        scores[docId] = tf_idf * (1 + math.log10(posting[1]))

    #Normalization for docIds to obtain the final score for each document
    for docId in scores:
        scores[docId] = scores[docId]/getVectorLength(docId, vector_lengths)

    topList = sorted(([scores[docId], docId] for docId in scores), key = lambda pair:(-pair[0], pair[1]))
    return topList

def processFreeTextQuery(termsList, term_dict, postings, vector_lengths):
    filteredTermsList =  filterStopWords(termsList)
    totalNumberOfDocs = getTotalNumberOfDocs(postings)
    queryTermSet = {}
    queryWeights = {}
    #Some preprocessing to prepare for the calculation of query weights
    for term in filteredTermsList:
        if term not in queryTermSet:
            queryTermSet[term] = [1, ThesaurusTermWrapper(term, termsList).generateDocumentFrequency(term_dict)]
        else:
            queryTermSet[term][0] += 1

    for term in queryTermSet:
        #Calculates weights for query without normalization
        #Normalization of the queries will be excluded, Since it does nost affect
        #the overall ranking
        infoPair = queryTermSet[term]
        if infoPair[1] != 0:
            queryWeights[term] = (1 + math.log10(infoPair[0])) * (math.log10(totalNumberOfDocs/infoPair[1]))

    relevantDocsSet = set()
    relevantDocsList = []
    found = 0
    for size in range(min(len(filteredTermsList),4), 0, -1):
        # size is the length of the partial phrase that we are going to search
        # the maximum possible size of the partial phrase is arbitrarily set at 4
        # to ensure that the query can be completed on time
        scores = {}
        docSet = findDocContainingPartialPhrase(filteredTermsList, size, term_dict, postings)

        #Calculates dot product of query length and document length(without normalization)
        #Note that only documents that have matching stems to the query will be considered
        #in the calculation of the dot product.
        for term in queryWeights:
            postingList = ThesaurusTermWrapper(term, termsList).generatePostingsList(term_dict, postings)
            for posting in postingList:
                docId = posting[0]
                if docId in docSet:
                    if docId not in scores:
                        scores[docId] = 0
                    scores[docId] += queryWeights[term] * (1 + math.log10(posting[1]))#tf-idf

        #Normalization for docIds to obtain the final score for each document
        for docId in scores:
            scores[docId] = scores[docId]/getVectorLength(docId, vector_lengths)

        topList = sorted(([scores[docId], docId] for docId in scores), key = lambda pair:(-pair[0], pair[1]))
        for pair in topList:
            docId = pair[1]
            if docId not in relevantDocsSet:
                relevantDocsSet.add(docId)
                # Add the list of relevant documents along with its score to the back of the
                # list of relevant docs
                relevantDocsList.append([docId, scores[docId]])
                found += 1

        if found > 18000:
            # Hard coded 18000 stops the retrieval of documents
            # if all possible documents have already been retrieved
            return relevantDocsList
    return relevantDocsList

    '''
        # The following code is for the implementation of Ranking with Mixture Model
        for term in filteredTermsList:
            postingList = ThesaurusTermWrapper(term, termsList).generatePostingsList(term_dict, postings)
            colTermFreq = ThesaurusTermWrapper(term, termsList).generateCollectionTermFrequency(term_dict)
            #postingList = loadPostingList(term, term_dict, postings)
            for posting in postingList:
                docId = posting[0]
                if docId in docSet:
                    if docId not in scores:
                        scores[docId] = 1
                    #mixture model formula
                    scores[docId] *= 0.99 * (posting[1]/doc_word_count[docId]) + 0.01 * (colTermFreq/119741975)
                    #119741975 is the total number of terms in the collection. It is hard-coded in for testing
    '''

    '''
        # The following code is for the implementation of retrieving relevant documents with PRF
        topList = sorted(([scores[docId], docId] for docId in scores), key = lambda pair:(pair[0], -pair[1])))

        for pair in topList:
            docId = pair[1]
            if docId not in relevantDocsSet:
                relevantDocsSet.add(docId)
                relevantDocsList.append([docId, scores[docId]])
                found += 1

        if found < 10:
            #Found less than 10 results, continue finding more results
            continue

        initialRelevantDocs = relevantDocsList[:10] #Retrieve top 10 documents for PRF

        #Generates relevant documents with PRF
        relevantDocsList = PseudoRF(queryWeights, initialRelevantDocs).giveFeedback(term_dict, postings, doc_vectors, vector_lengths)
    '''


def processBooleanQuery(termsList, term_dict, postings, vector_lengths):
    '''
    NOTE: This function is originally used for the processing of boolean
          queries. Since we are processing all boolean queries as FreeText
          queries, this method is no longer used
    '''
    #Some preprocessing to prepare for the calculation of query weights
    term_results = []
    for term in termsList:
        if type(term) is list:
            #term is a phrase
            term_results.append(sorted(processFreeTextQuery(term, term_dict, postings, vector_lengths)))
        else:
            #Logic reaches here if its a single term
            term_results.append(sorted(processSingleWordQuery(term, term_dict, postings, vector_lengths, doc_word_count)))

    #"AND" all term_results
    andOutput = term_results[0]
    for x in range(1, len(term_results)):
        andOutput = andV1(andOutput, term_results[x])
    meanScoredOutput = []
    for x in range(len(andOutput)):
        item = andOutput[x]
        sum = 0
        for y in range(1, len(item)):
            #item[0] is the documentId, item[1:] stores the tf-idf weight
            sum += item[y]
        #Take a basic average of all the scores for now
        meanScoredOutput.append([item[0], sum/(len(item) + 1)])
    return [pair[0] for pair in sorted(meanScoredOutput, key = lambda pair:(pair[1], -pair[0]))]

def executeSearch(queryString, term_dict, postings, vector_lengths):

    startTime = time.time()

    newFreeText = []
    for term in queryString.split():
        newTerm = term.strip('"')
        if newTerm != "" and newTerm != "AND":
            newFreeText.append(newTerm)

    result =  [pair[0] for pair in processFreeTextQuery(newFreeText, term_dict, postings, vector_lengths)]

    '''
    #The following code logic is for the processing of boolean logic. But is no longer used
    since we will be treating all boolean queries as freetext and the logic can therefore be simplified
    if isBooleanQuery:
        #Boolean queries with phrases
        termsList = queryStringToPhraseAndTermsList(queryString)
        print "booleanQuery" + str(termsList)
        newFreeText = []

        #Converts boolean to freetext by concatenating the terms
        for term in termsList:
            if type(term) is list:
                for subterm in term:
                    newFreeText.append(subterm)
            else:
                newFreeText.append(term)

        #Returns only the list of docIds
        result =  [pair[0] for pair in processFreeTextQuery(newFreeText, term_dict, postings, vector_lengths)]
    else:
        #Logic reaches here if query is freeText
        termsList = phraseToTermsList(queryString)
        print "freetext" + str(termsList)

        #Returns only the list of docIds
        result = [pair[0] for pair in processFreeTextQuery(termsList, term_dict, postings, vector_lengths)]
    '''
    print "Execution Time:" + str(time.time() - startTime) + "s"
    #Clears list of terms stored within ThesaurusTermWrapper
    ThesaurusTermWrapper.clearTermStorage()
    return result
