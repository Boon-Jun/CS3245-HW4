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
Note: There are some changes to how search.py is used. Refer to the section under
      'Files included with this submission' for more details

Before the documents are being ranked, all non alphanumeric characters in the query
string will be replaced with a space before tokenizing it and stemming it with
PorterStemmer. This is similar to how the the words in the documents are indexed.

The documents will then be ranked according to the lnc.ltc ranking scheme.
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

To retrieve the Top 10 Ranked documents, we utilize the heapq library, nlargest
method.

How the nlargest method selects the top 10 ranked documents:
1) If there are lesser than 10 documents, the method will return all the documents
2) Else:
   2a) Create a heap of size 10 first with 10 documents
   2b) For each document(A) not added into the heap yet
       a)If A has a higher score than the document with the lowest score in the heap
	       or if A has the same score with the document with the lowest score in the heap,
		     but a smaller document ID, then the document within the heap will be removed
		     and A will be added into the heap.
       b)If not, A will not be added to the heap.

Since there is a total of N documents and a heap of size 10, there will be an upperbound
of N additions and N removals. Therefore, the time complexity to retrieve the top
10 documents is O(NLog10)

After the top 10(or lesser) documents are retrieved, the document Ids are then
sorted in order of decreasing score and then by order of increasing document Ids
in the event that 2 documents have the same score.

== Essay Questions ==

1. In this assignment, we didn't ask you to support phrasal queries, which is a
feature that is typically supported in web search engines. Describe how you would
 support phrasal search in conjunction with the VSM model. A sketch of the algorithm
 is sufficient. (For those of you who like a challenge, please go ahead and
 implement this feature in your submission but clearly demarcate it in your
 code and allow this feature to be turned on or off using the command line
 switch "-x" (where "-x" means to turn on the extended processing of phrasal
 queries). We will give a small bonus to submissions that achieve this
 functionality correctly).

 In our opinion, one possible way to perform phrasal queries is to index the documents into
 postings for unigrams and bi-grams, and store both type of grams into the index.
 We can also extend this to higher n-grams as long as space is not an issue.
 Example: "Fight me please" will be indexed as "Fight", "me", "Fight me", "me please"
 etc.

 To perform the search, n-grams from the query will be first obtained.
 When phrasal queries are enabled we could modify the VSM such that the
 axes of a vector for each documents includes the n-grams along with the unigrams.
 We could then implement the same lnc.ltc ranking scheme and rank each
 document accordingly.

 However, this implementation does not consider phrases that has a length
 of more than n, where n is the highest numbered n-gram stored in the index.

2. Describe how your search engine reacts to long documents and long queries as
compared to short documents and queries. Is the normalization you use sufficient
to address the problems (see Section 6.4.4 for a hint)? In your judgement,
is the ltc.lnc scheme (n.b., not the ranking scheme you were asked to implement)
sufficient for retrieving documents from the Reuters-21578 collection?

Firstly, long queries takes a longer time to process.
Longer queries with a lot of words from a particular document give
very accurate results. However, if the query is short, shorter documents might be favoured
although normalization is done. This is due to the fact that the shorter queries often
has limited axes of freedom for the resulting vector. Shorter documents with less diversity
but words matching with the query will tend to have a larger consine similarity as their vectors have
less axes of freedom similar to shorter queries. Longer documents with similar number of matching words,
 on the other hand have more axes of freedom. This means that the presence of other axes for longer
document vectors might "pull" the vector away from the query vector creating a larger angle between them.
Normalization does not solve this as it does not affect the angle between the vectors.


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
