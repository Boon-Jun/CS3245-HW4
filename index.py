#!/usr/bin/python
import re
import nltk
import sys
import getopt
from indexer import index

def usage():
    print "usage: " + sys.argv[0] + " -i dataset-file -d dictionary-file -p postings-file"

input_file = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
    
for o, a in opts:
    if o == '-i': # input file
        input_file = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"
        
if input_file == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

index(input_file, output_file_dictionary, output_file_postings)

### Test code on smaller number of documents ###
# print(index("./test_docs","test_dictionary.txt", "test_postings.txt"))

