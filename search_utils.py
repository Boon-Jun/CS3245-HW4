import ast

maxLength = None

def loadPostingList(term, term_dict, postings):
    byteOffset = 0
    try:
        byteOffset = term_dict[term][0]
    except KeyError as e:
        return []
    postings.seek(byteOffset)
    return ast.literal_eval(postings.readline().rstrip())

def getAllDocIds(postings):
    return ast.literal_eval(postings.readline().rstrip())

def getDocFrequency(term, term_dict):
    try:
        return term_dict[term][1]
    except KeyError as e:
        return 0

def getVectorLength(docId, vector_lengths):
    try:
        return vector_lengths[docId]
    except KeyError as e:
        return 0

def getTotalNumberOfDocs(postings):
    global maxLength
    if maxLength == None:
        #Length is computed only once
        maxLength = len(getAllDocIds(postings))
    return maxLength

def filterHighIdf(term, term_dict):
    '''
    Returns frequency of document if frequency is less than threshold
    else return 0 to simulate the non existence of the term in the postings list
    '''
    DOC_COUNT_THRESHOLD = 18000
    freq = getDocFrequency(term, term_dict)
    if (getDocFrequency(term, term_dict) < DOC_COUNT_THRESHOLD):
        return freq
    else:
        return 0
