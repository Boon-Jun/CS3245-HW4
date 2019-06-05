import re
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Look for extra packages in nltk_data folder 
nltk.data.path.append("./nltk_data")

stemmer = PorterStemmer()
stopWords = set(stopwords.words('english'))
def queryStringToPhraseAndTermsList(booleanQueryString):
    #Retrieves terms and phrases from query string.
    #This is mainly for the parsing of boolean queries

    #Split the string by double-colons first. This helps us identify the phrases
    termsAndPhraseList = booleanQueryString.split('"')
    termsList = []
    for i in range(len(termsAndPhraseList)):
        if i%2:
            # Every odd index is a phrase, we are going to add that in as a term
            phrase = termsAndPhraseList[i]
            phraseTermsList = phraseToTermsList(phrase)
            termsList.append(phraseTermsList)
        elif termsAndPhraseList[i] != "":
            # Every even index consist of terms and "AND" operators
            # We are only interested in the terms here
            termsList.extend([word.lower() for word in termsAndPhraseList[i].split() if word != "AND" ])
    return termsList

def phraseToTermsList(phrase):
    #Converts a phrase to a list of terms
    termsList = phrase.strip('"').split()
    return termsList

def filterStopWords(termsList):
    #Remove all stop words from list of terms
    filteredList = []
    for term in termsList:
        if term not in stopWords:
            filteredList.append(term)
    return filteredList
