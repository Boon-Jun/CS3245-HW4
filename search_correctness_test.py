#!/usr/bin/python
import re
import nltk
import sys
import getopt
import pickle
import search_logic

def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries"

dictionary_file = postings_file = file_of_queries = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None:
    usage()
    sys.exit(2)

queriesFile = open(file_of_queries, "r")
term_dict = pickle.load(open(dictionary_file, "rb"))
postings = open(postings_file, "r")

for query in queriesFile:
    resultsList1 = search_logic.executeBasicSearch(query, term_dict, postings)
    resultsList2 = search_logic.executeOptimizedSearch(query, term_dict, postings)
    if resultsList1 != resultsList2:
        print "Error with " + query
        print resultsList1
        print resultsList2
        print "======================"
