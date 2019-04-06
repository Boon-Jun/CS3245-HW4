from boolean_operations import notOp, andOp
from search_utils import *

class CombinedTerm(object):
    #Stores query terms for lazy evaluation
    def __init__(self):
        self.termsList = []

    def addNewTerm(self, term):
        self.termsList.append(term)
        return self

    def getTerms(self):
        return self.termsList

    def computeCombinedTerm(self, term_dict, postings, primaryList = None):
        #Treat this like an abstract method
        pass

class AndCombinedTerm(CombinedTerm):
    # A CombinedTerm with an 'AND' operation
    def __init__(self, term):
        super(AndCombinedTerm, self).__init__()
        self.addNewTerm(term)

    def moveSmallestTermToFrontOfList(self, term_dict):
        #Moves smallest term to front of the list so that it will be processed first
        smallestTermCount = 1e9
        smallestTermPos = 0
        for x in range(len(self.termsList)):
            term = self.termsList[x]
            currentTermCount = -1
            if isinstance(term, CombinedTerm):
                currentTermCount = 1e8
            elif type(term) is list:
                currentTermCount = len(term)
            else:
                currentTermCount = getTermCount(term, term_dict)
            if currentTermCount < smallestTermCount:
                smallestTermCount = currentTermCount
                smallestTermPos = x
            self.termsList[0], self.termsList[smallestTermPos] = self.termsList[smallestTermPos], self.termsList[0]

    def computeCombinedTerm(self, term_dict, postings, primaryList = None):
        intermediateList = primaryList
        # Execute AND operations starting with the term with the smallest size within
        # an AndCombinedTerm.
        self.moveSmallestTermToFrontOfList(term_dict)
        for term in self.termsList:
            if isinstance(term, CombinedTerm):
                intermediateList = term.computeCombinedTerm(term_dict, postings, intermediateList)
            else:
                operand = term if type(term) is list else loadPostingList(term, term_dict, postings)
                if intermediateList is None:
                    intermediateList = operand
                else:
                    intermediateList = andOp(operand, intermediateList)
        return intermediateList

class NotCombinedTerm(CombinedTerm):
    # A CombinedTerm with a 'NOT' operation
    def __init__(self, term):
        super(NotCombinedTerm, self).__init__()
        self.addNewTerm(term)

    def computeCombinedTerm(self, term_dict, postings, primaryList = None):
        # Execute 'primaryList' AND NOT 'operand' if primaryList is available,
        # else, perform 'allDocIds' AND NOT 'operand' (Expensive operation)

        term = self.termsList[0]
        operand = None
        if isinstance(term, CombinedTerm):
            operand = term.computeCombinedTerm(term_dict, postings)
        elif type(term) is list:
            operand = term
        else:
            operand = loadPostingList(term, term_dict, postings)
        return notOp(getAllDocIds(postings), operand) if primaryList is None else notOp(primaryList, operand)
