import re
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize

stemmer = PorterStemmer()

def insertSpaceBeforeAndAfterBrackets(queryString):
    pat = re.compile(r"([()])")
    return pat.sub(" \\1 ", queryString)

def queryStringToTermsList(queryString):
	# Replace all non-alphanum, non-space chars in each query with space
	tokens = []
	new_query = []
	for c in queryString:
		if c.isalnum() or c.isspace():
			new_query.append(c)
		else:
			new_query.append(' ')
	new_query = ''.join(new_query)
	tokens.extend([token.lower() for token in word_tokenize(new_query)])

        #Query string will be split and have each individual terms stemmed with PorterStemmer
        return [stemmer.stem(word) for word in tokens]
