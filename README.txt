This is the README file for A0000000X-A0000000X's submission


== Python Version ==

I'm (We're) using Python Version <2.7.1 or replace version number> for
this assignment.

== General Notes about this assignment ==

Indexing Algorithm:
--------------------

Indexing is done in- memory first and then written into the file at the very end.
The postings are stored in a dictionary with the terms are the keys and a list of postings is the value to each term.
The dictionary of terms is stored in a dicitonary with the terms as the keys and the
tuple of (byte_offset, document_frequency) as the values.

The documents are indexed as follows:

1) Document Ids in the directory are are parsed to integers and sorted

2) Preprocess the text in each document.
	i) Prepare the text by replacing '\n' characters in text with ' '
	ii) Apply the NLTK sentence tokenizer
	iii) Replace all non alphanumeric characters in sentence with space. This step ensures that
	the terms in the sentences are normalized. This has to be done as the word tokenizer fails
	to remove unnecessary symbols from words frequently leading to reduced term frequency
	of a word.
	iv) Word Tokenize each sentece with NLTK sentence tokenizer
	v) Case fold each token
	vi) Apply the NLTK Porter Stemmer

3a) For each term, if the term is new, add the term to the dictionary and the postings.
Then add the occuring Document Id (if it has not already been added) and Term frequency
 into the corresponding postings list in the postings and update the document frequency
in the dictionary.

3b) Keep track of the term frequency of every term in the document with a python dictionary.
Update the term  frequencies as a term is encountered, creating new keys in the dictionary as newer
terms are encountered.

3c) Using the term frequencies, compute the tf values for every term and then compute the document
vector lengths which will be used for computing document scores in the Vector Space Model.
Vector lengths we calculated by taking the square root of the sum of the squares of the tf values
for a document. Vector lengths are stored in a python dicitonary with the keys being the document ids.

3) Then, add approximately sqrt(document_frequency) evenly spaced skip pointers
to every postings list in the postings, in the form of a list index to a document_id to its right,
accompanying the select Document Ids. Document Ids with skip pointers will be tuples
of the form: (document_id, term_frequency,  skip_index). This way, an entire posting list can be loaded as a python list
when searching and skips will be performed by accessing the element in the list at the specified skip index.


4) Write the list of all sorted Document Ids to the top of the postings file. This will be used
for NOT queries.

5) While writing the postings list for each term in the postings file, fill the byte_offset value of
where it is written in the file from the start, in each corresponding term in the dictionary. This
makes finding the postings list to be loaded into the memory more efficient, during the search.

6) Pickle the dictionary and write the it to the dictionary file. The entire dictionary can
be unpickled in the memory during the search as it is relatively small compared to the postings,
which will only be loaded list by list for every search query.

7) Pickle the vector lengths dicitonary and write it to the lengths file. The dicitonary
can be unpickled during the search when the document score computation takes place.


Searching Algorithm:
---------------------
In the main implementation of the Search Algorithm, we will be ranking the documents
by lnc.ltc ranking scheme(similar to that of HW3). However, as an addition, we will
also be ranking a document higher if a phrase within the original query exists
within a document. The longer the phrase, the higher the document will rank.
Ranking of the documents by phrase will take precedence of lnc.ltc

We will also document both the MAF2(Mean Average F2) and MAP(Mean Average Precision)
metric here to talk about our progress as we explain the high level algorithm that
we have implemented

====================Ranking by lnc.ltc ranking scheme================
The documents will be ranked according to the lnc.ltc ranking scheme.
That is to say that the weights of each term in the document will be calculated as :
(1 + log10(term_frequency_in_documents))
whereas the weights of each term in the query will be calculated as:
tf-idf = (1 + log(term_frequency_in_query)) * log(number_of_documents/document_frequency)

After that, cosine normalization will be applied to the weights of each term in both
the query and the document, and the dot product of the weights of the terms in the
query and the weights of the terms in the documents will give us a score.

However, in our actual implementation, we omit the step of computing the cosine
normalization for the query since the computation of the cosine normalization
for the query will reduce the calculated scores by the same factor, and the
actual ranking of the documents will not be affected.

===============Parsing of Boolean to FreeText Queries==================
From our experimentation with different techniques, we found that treating boolean
queries as FreeText query provides better results in most cases.
To convert a Boolean query to a FreeText query, we simply concatenate all the terms
with a space in between to create a FreeText.

===============Execution of FreeText Queries====================
Since all types of queries are now considered as FreeText, we can execute all of
them in the same manner. The High level algorithm is as follows

1. First we find all documents with that contains partial phrases up to a size of 4
   (We limit the size of phrases here due to the possiblity of long queries which can greatly increase query time)
	 1.1 With the list of documents that have partial phrases up to a size of 4, we will
	 		 then rank only these documents via the lnc.ltc ranking scheme

	 1.2 Any documents returned will be appended to a relevant documents list by the
	     lnc.ltc ranking scheme

2. Next we find all documents with that contains partial phrases up to a size of 3
		2.1 With the list of documents that have partial phrases up to a size of 3, we will
		    then rank only these documents via the lnc.ltc ranking scheme
    2.2 Any documents returned will be appended to a relevant documents list by the
		    lnc.ltc ranking scheme. Since the documents are appended to the list, the
				order of documents already within the list will not be affected

3. Repeat the whole process for partial phrases of the size of 2 and 1

=============Baseline================
VSM Model, ranking done with what was described in the previous section. The following
are our results from the 3 given queries

MAF2: 0.3031148884
MAP: 0.2126508143

=============== Query Expansion with Princeton's Wordnet ==============
We will be expanding each query term

=============== Language Model(Mixture Model) ==============




== Files included with this submission ==
README.txt - This file

index.py - Required file for submission
indexer.py - Perfoms the indexing of directory of documents.
dictionary.txt - Pickled dictionary of terms from the Reuters Training Dataset
postings.txt - Postings List of each term specified in dictionary.txt
postings_plaintext.txt - Contains a human readable index with dictionary word and
			corresponding posting list
lengths.txt - Stores a dictionary of document lengths
search.py - Required file for submission
            Usage of search.py now slightly differs from the original due to the
						addition of lengths.txt file
						As such, the correct usage of search.py file will now be:
						python search.py -d dictionary-file -p postings-file -l length-file -q file-of-queries -o output-file-of-results
search_logic.py - Main implementation of search logic
query_parser.py - Contains simple query parser to split and stem a query string
search_utils.py - Commonly used utility methods for searching


== Statement of individual work ==

Please initial one of the following statements.

[x] I, A0000000X-A0000000X, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:

<Please fill in>

== References ==

Forums on IVLE - Compare Search Results
python's heapq documentation and source code - Helps us understand the nlargest method
CS3245 lecture note 7 for the indexing and search algorithm for VSM
