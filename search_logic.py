from query_parser import queryStringToPhraseAndTermsList, phraseToTermsList
from search_utils import *
import math
import heapq
import time
from operator import itemgetter
from boolean_operations import andPosIndex, andDocLists
from thesaurus_expansion import ThesaurusTermWrapper

def findDocContainingPartialPhrase(phraseTermsList, size, term_dict, postings, strict = False):
    #Returns all docs containing a partialPhrase of length 'size'
    docSet = set()
    for startPos in range(len(phraseTermsList)):
        if startPos + size <= len(phraseTermsList):
            docs_list = []
            endPos = startPos + size
            postingsList = ThesaurusTermWrapper(phraseTermsList[startPos], phraseTermsList).generatePostingsList(term_dict, postings)
            #postingsList = loadPostingList(phraseTermsList[startPos], term_dict, postings)

            for x in range(len(postingsList)):#Prepare first doc List
                docs_list.append([postingsList[x][0], list(postingsList[x][2])])

            for x in range(startPos + 1, endPos):
                docs_list = andPosIndex(docs_list,
                    ThesaurusTermWrapper(phraseTermsList[x], phraseTermsList).generatePostingsList(term_dict, postings),
                    window = (1 if strict else 1))
                #docs_list = andPosIndex(docs_list, loadPostingList(phraseTermsList[x], term_dict, postings), window = (1 if strict else 3))
            for item in docs_list:
                docSet.add(item[0])
        else:
            break
    return docSet

def processSingleWordQuery(term, term_dict, postings, vector_lengths):
    '''
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
        tf_idf = math.log10(totalNumberOfDocs/docCount)
        #tf_idf = math.log10(totalNumberOfDocs/filterHighIdf(term, term_dict))
    #In single word terms, only need to calculate idf since tf = 1

    postingsList = ThesaurusTermWrapper(term, None).generatePostingsList(term_dict, postings)
    #postingsList = loadPostingList(term, term_dict, postings)

    for posting in postingsList:
        docId = posting[0]
        scores[docId] = tf_idf * (1 + math.log10(posting[1]))

    #Normalization for docIds to obtain the final score for each document
    for docId in scores:
        scores[docId] = scores[docId]/getVectorLength(docId, vector_lengths)

    #Retrieve Top 20 Documents with a heap

    # Top 100 items will be retrieved from the heap, first by highest score
    # and then by smallest docId, in the event that 2 documents have the same score.
    topList = heapq.nlargest(18000, ([docId, scores[docId]] for docId in scores), key = lambda pair:(pair[1], -pair[0]))
    #print topList
    return topList

def processFreeTextQuery(termsList, term_dict, postings, vector_lengths, strict = False):
    totalNumberOfDocs = getTotalNumberOfDocs(postings)
    queryTermSet = {}
    queryWeights = {}
    #Some preprocessing to prepare for the calculation of query weights
    for term in termsList:
        if term not in queryTermSet:
            queryTermSet[term] = [1, ThesaurusTermWrapper(term, termsList).generateDocumentFrequency(term_dict)]
            #queryTermSet[term] = [1, filterHighIdf(term, term_dict=)]
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
    for size in range(len(termsList), len(termsList) - 1 if strict else 0 , -1):#size is the length of the partial phrase that we are going to search
        scores = {}
        docSet = findDocContainingPartialPhrase(termsList, size, term_dict, postings, strict)
        #Calculates dot product of query length and document length(without normalization)
        #Note that only documents that have matching stems to the query will be considered
        #in the calculation of the dot product.
        for term in queryWeights:
            postingList = ThesaurusTermWrapper(term, termsList).generatePostingsList(term_dict, postings)
            #postingList = loadPostingList(term, term_dict, postings)
            for posting in postingList:
                docId = posting[0]
                if docId in docSet:
                    if docId not in scores:
                        scores[docId] = 0
                    scores[docId] += queryWeights[term] * (1 + math.log10(posting[1]))

        #Normalization for docIds to obtain the final score for each document
        for docId in scores:
            scores[docId] = scores[docId]/getVectorLength(docId, vector_lengths)

        #Retrieve Top 20 Documents with a heap
        # Top 20 items will be retrieved from the heap, first by highest score
        # and then by smallest docId, in the event that 2 documents have the same score.
        topList = heapq.nlargest(18000, ([scores[docId], docId] for docId in scores), key = lambda pair:(pair[0], -pair[1]))

        for pair in topList:
            docId = pair[1]
            if docId not in relevantDocsSet:
                relevantDocsSet.add(docId)
                relevantDocsList.append([docId, scores[docId]])
                found += 1

        if found > 18000:
            return relevantDocsList
    return relevantDocsList

def processBooleanQuery(termsList, term_dict, postings, vector_lengths):
    #Some preprocessing to prepare for the calculation of query weights
    term_results = []
    for term in termsList:
        if type(term) is list:
            #term is a phrase, the whole phrase will be processed as a stricter version of free text query
            #where the WHOLE phrase must exist in a document
            term_results.append(sorted(processFreeTextQuery(term, term_dict, postings, vector_lengths, strict = False)))
        else:
            term_results.append(sorted(processSingleWordQuery(term, term_dict, postings, vector_lengths)))

    andOutput = term_results[0]
    for x in range(1, len(term_results)):
        andOutput = andDocLists(andOutput, term_results[x])
    meanScoredOutput = []
    for x in range(len(andOutput)):
        item = andOutput[x]
        sum = 0
        for y in range(1, len(item)):
            sum += item[y]
        #Take a basic average of all the scores for now
        meanScoredOutput.append([item[0], sum/len(item) - 1])
    return [pair[0] for pair in sorted(meanScoredOutput, key = lambda pair:(pair[1], -pair[0]))]

def executeSearch(queryString, term_dict, postings, vector_lengths):
    isBooleanQuery = False
    termsList = queryString.split()

    startTime = time.time()
    if termsList and "AND" in termsList and "AND" != termsList[-1] and "AND" != termsList[0]:
        #Determines whether if query is free text query or boolean query with phrases/terms
        isBooleanQuery = True

    if isBooleanQuery:
        #Boolean queries with phrases
        termsList = queryStringToPhraseAndTermsList(queryString)
        print "booleanQuery" + str(termsList)
        newFreeText = []
        for term in termsList:
            if type(term) is list:
                for subterm in term:
                    newFreeText.append(subterm)
            else:
                newFreeText.append(term)
        result =  [pair[0] for pair in processFreeTextQuery(newFreeText, term_dict, postings, vector_lengths, strict = False)]
        #result = processBooleanQuery(termsList, term_dict, postings, vector_lengths)
    else:
        #We will treat this as a free text query
        termsList = phraseToTermsList(queryString)
        print "freetext" + str(termsList)
        #result = processFreeTextQuery(termsList, term_dict, postings, vector_lengths, strict = False)
        result = [pair[0] for pair in processFreeTextQuery(termsList, term_dict, postings, vector_lengths, strict = False)]

    print "Execution Time:" + str(time.time() - startTime) + "s"
    ThesaurusTermWrapper.clearTermStorage()
    return result
