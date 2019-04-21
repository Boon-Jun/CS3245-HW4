#!/usr/bin/python
from __future__ import division
import re
import nltk
import sys
import getopt
import pickle
import search_logic
import time
import statistics
import matplotlib.pyplot as plt

def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -r file-of-relevant"

dictionary_file = postings_file = file_of_relevant = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:r:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-r':
        file_of_relevant = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_relevant == None:
    usage()
    sys.exit(2)



def evaluateResult(correctList, actualResult):
    evaluateAF2(correctList, actualResult)

def evaluateAF2(correctList, actualResult):
    print correctList
    correctSet = set(correctList)
    relevant = 0
    F2List = []
    precisionList = []
    recallList = []
    MAPList = []
    for x in range(len(actualResult)):
        result = actualResult[x]
        if result in correctSet:
            relevant += 1
            precision = relevant/(x + 1)
            recall = relevant/len(correctList)
            precisionList.append(precision)
            recallList.append(recall)
            F2List.append((5*precision*recall)/(5*precision + recall))
            AF2 = statistics.mean(F2List)
            print "Position: " + str(x)
            print "AF2: " + str(AF2)
            precision = statistics.mean(precisionList)
            print "MAP: " + str(precision)
            print "R-precision: " + str(precision)
            print "==================="
    plt.plot(recallList, precisionList)
    # naming the x axis
    plt.xlabel('Recall')
    # naming the y axis
    plt.ylabel('Precision')

    # giving a title to my graph
    plt.title('Precision-Recall Curve')

    #mngr = plt.get_current_fig_manager()
    #mngr.window.setGeometry(0,0,1, 1)
    # function to show the plot
    plt.show()

relevantFile = open(file_of_relevant, "r")
term_dict = pickle.load(open(dictionary_file, "rb"))
postings = open(postings_file, "r")
vector_lengths = pickle.load(open("lengths.txt", "rb"))

query = relevantFile.readline()
correctList = []
for correctResult in relevantFile:
    correctList.append(int(correctResult))
resultsList = search_logic.executeSearch(query, term_dict, postings, vector_lengths)
evaluateResult(correctList, resultsList)
