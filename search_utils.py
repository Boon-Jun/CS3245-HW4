import ast
from nltk.stem.porter import PorterStemmer

maxLength = None
stemmer = PorterStemmer()

highPrioritySet = {
    'SG Court of Appeal',
    'SG Privy Council',
    'UK House of Lords'
    'UK Supreme Court',
    'High Court of Australia',
    'CA Supreme Court]'
}

mediumPriorityList = {
    'SG High Court',
    'Singapore International Commercial Court',
    'HK High Court',
    'HK Court of First Instance',
    'UK Crown Court',
    'UK Court of Appeal',
    'UK High Court',
    'Federal Court of Australia',
    'NSW Court of Appeal',
    'NSW Court of Criminal Appeal',
    'NSW Supreme Court'
}

def getCourtsPriority(docId, courts_dict):
    try:
        courts = courts_dict[str(docId)]
        if courts in highPrioritySet:
            return 2
        elif courts in mediumPriorityList:
            return 1
        else:
            return 0
    except KeyError as e:
        return 0
def loadPostingList(term, term_dict, postings):
    stemmedTerm = stemmer.stem(term)
    byteOffset = 0
    try:
        byteOffset = term_dict[stemmedTerm][0]
    except KeyError as e:
        return []
    postings.seek(byteOffset)
    return ast.literal_eval(postings.readline().rstrip())

def getAllDocIds(postings):
    return ast.literal_eval(postings.readline().rstrip())

def getDocFrequency(term, term_dict):
    stemmedTerm = stemmer.stem(term)
    try:
        return term_dict[stemmedTerm][1]
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

def getDocVector(docId, doc_vectors):
    try:
        return doc_vectors[str(docId)]
    except KeyError as e:
        print "error"
        return 0

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

def getCollectionFrequency(term, term_dict):
    stemmedTerm = stemmer.stem(term)
    try:
        return term_dict[stemmedTerm][2]
    except KeyError as e:
        return 0
