This is the README file for A0170229J-A0000000X's submission


== Python Version ==

I'm (We're) using Python Version <2.7.1 or replace version number> for
this assignment.


==================== Allocation of work ========================
A0170229J is in charge of the implementation of indexing logic
A0000000X is in charge of implementing the main search logic and query refinement techniques


== General Notes about this assignment ==

Indexing Algorithm:
--------------------

Indexing is done in-memory first and then written into the file at the very end.
The postings are stored in a dictionary where the terms are the keys and a list of postings is the value to each term.
Each posting is a tuple of (document id, term frequency, position list).

The dictionary of terms is stored in a dictionary with the terms as the keys and the
tuple of (byte offset, document frequency, collection frequency) as the values.

The documents are indexed as follows:

1) Python csv module is used to parse the csv file into a dictionary of doc_ids
mapped to dictionaries of documents (whose keys are the fields). There are a handful of document pairs
whose doc_ids are the same, with the only difference between them being the courtnames. For these
documents they are mapped to the same key in the dictionary of documents, with the court name being a
tuple of court names instead of a single court name.

2) Preprocess the text in each document.
	i) Concatenate all the fields in a document into a single text. We did this as there
	was not much purpose to indexing the fields separately except for courtnames.
	Firstly, the courtnames were given to us categorized by their relevance. This could be used
	to sort the results by relevance. Secondly, the small set of courtnames could mean that
	they can be used to preprocess the results before VSM search.

	Dates were also considered for separate indexing. This is because we felt that searching by
	dates may be a common use case in a legal setting. However, extracting dates from each document
	made the indexing process much slower, exceeding the 5 hours indexing time limit. Therefore this idea was abandoned.

	i) Prepare the text by replacing '\n' characters in text with ' '
	ii) Apply the NLTK sentence tokenizer
	iii) Replace all non alphanumeric characters in sentence with space. This step ensures that
	the terms in the sentences are normalized. This has to be done as the word tokenizer fails
	to remove unnecessary symbols from words frequently leading to reduced term frequency
	of a word.
	iv) Word Tokenize each sentence with NLTK sentence tokenizer
	v) Case fold each token
	vi) Apply the NLTK Porter Stemmer
	v) Append the courtname as a separate term to the stemmed tokens, so that it will
	have its own postings list in the index.

3a) For each term, if the term is new, add the term to the dictionary and the postings.
Then add the occurring Document Id (if it has not already been added) and Term frequency
 into the corresponding postings list in the postings and update the document frequency
in the dictionary.

3b) If the term is not a courtname, keep track of the term frequency and the positional list of every term
in the document with a python dictionary. Update the term frequencies and positional list as a term is encountered,
creating new keys in the dictionary as newer terms are encountered.

3c) Using the term frequencies, compute the tf values for every term and then compute the document
vector lengths which will be used for computing document scores in the Vector Space Model.
Vector lengths we calculated by taking the square root of the sum of the squares of the tf values
for a document. Vector lengths are stored in a python dictionary with the keys being the document ids.
Note that courtnames are not part of VSM.

3) Then, add approximately sqrt(document_frequency) evenly spaced skip pointers
to every postings list in the postings, in the form of a list index to a document_id to its right,
accompanying the select Document Ids. Document Ids with skip pointers will be tuples of the form: (document_id, term_frequency, positional list,  skip_index). This way, an entire posting list can be loaded as a python list when searching and skips will be performed by accessing the element in the list at the specified skip index.

4) Write the list of all sorted Document Ids to the top of the postings file.

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
metric here to talk about the performance of our search engine
 as we explain the high level algorithm that we have implemented

====================== Ranking by lnc.ltc ranking scheme ======================
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

=================== Parsing of Boolean to FreeText Queries ====================
From our experimentation with different techniques, we found that treating boolean
queries as FreeText query provides better results in most cases.
To convert a Boolean query to a FreeText query, we simply concatenate all the terms
with a space in between to create a FreeText.

======================= Execution of FreeText Queries =========================
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

Another thing to take note is that during the execution of FreeText Queries, all
stopwords will be removed from the query due to the long query time when trying to
process stopwords.

============================== OUR Baseline ==============================
VSM Model, ranking done with what was described in the previous section. The following
are our performance from the 3 given queries

MAF2: 0.3031148884
MAP: 0.2182651002

=============== Query Expansion with Princeton's Wordnet ===============
When experimenting with Query Expansion of the Princeton’s wordnet.
We started with the generation of synonymous terms without considerations of the context
of the query, and the following are the performance measures of such an implementation.

MAF2:  0.1829879703
MAP: 0.1253270719

This implementation performs worse than our Baseline and the reason for this is that
the generation of synonyms without context results in a lot of synonyms that are actually
unrelated to the query.

Next, we decide to implement query expansion with Lesk Algorithm(NLTK). Using our whole query
as the context, we then pass both a term and the context into the algorithm to generate
a set of synonyms. Because of the extra context, the set of generated synonyms are now
much more relevant to the query, and the following are the performance measure for
this specific implementation.

MAF2: 0.2872533973
MAP: 0.1844737291

While the performance measure still seem to indicate that this algorithm is performing
slightly worse than our Baseline, this implementation is still able to perform
reasonably well within the competition framework. Also, our performance measures
is only estimated according to the 3 relevance judgements given to us, and hence,
it is hard to conclude whether this implementation is better/worse than our Baseline.

============== Post processing of generated terms from Query Expansion ==================
To process the generated terms after query expansion, one of the approach is to
execute the search on the different generated terms directly after query expansion.
For example if a term "A" expands into "B", "C" and "D", queries "A L", "B L", "C L"
and "D L" will be executed separately.

However, the previous approach could result in a query that takes a long time to process,
especially if each term in a query can be expanded into many terms, resulting in
many possible combinations of the query

Therefore, our approach after generating to this is to merge the postings list of terms
'A', 'B', 'C' and 'D' together before performing the query.

However the latter approach itself also has some issues and that is after merging the terms
together into one postings list, we will no longer be able to differentiate the document_frequencies
for each term individually since the new postings-list is a postings-list not for a single term,
but for multiple terms.

Summing up all the document-frequencies of each term and treating the sum as the "document-frequnecy"
of the new posting list is also problematic as it would affect the overall ranking of the documents
by changing the IDF weighting. To account for this problem we decided to take the average document-frequency
to generate a new "document-frequency" for this new posting list and it seems like this approach is able
to work moderately well within the competition framework.

============================== Zones and Fields ==============================
In our implementation of the search engine, we did not consider any zones as we are
unable to identify any which could be potentially significant that could affect
the ranking of documents. However, we still implemented some sorting according
to the Courts Hierarchy.

While sorting according to the Courts Hierarchy, we wanted to ensure that the ranking of the
documents estimated via the VSM is not largely distorted by the Courts Hierarchy.
To do so, we chose to sort the list of documents(After ranking with the VSM)
partially with 10 passes of bubble sort.

The reason we chose to use bubble sort is because in most_situations, one pass
of bubble sort only affects the ranking of the documents in close proximity to each other.
We assume that documents that are in close proximity to each other to be largely equivalent
in relevance, and therefore, sorting them with the first few passes of bubble sort
will affect the ranking of the documents via the VSM minimally.

There is no specific reason why we chose to have 10 bubble sort passes and it
is a number that was arbitrarily chosen.

The following are the performance measures after the implementation:
MAF2: 0.2975042902
MAP: 0.2453292886

MAF2 is still slightly worse when compared to the Baseline. However the accuracy
of our search engine has clearly improved by taking Courts Hierarchy into account.

In our opinion, we feel that the same thing to sort the documents chronologically.
However we did not have the chance to implement this due to time constraints.


=============== Other things we tried =================
- Language Model(Mixture Model)
We also tried implementing a probabilistic model for our search engine, building upon the
Mixture model discussed within the lecture notes.

However, it seems like the VSM approach is able to perform slightly better than the mixture model,
even after some attempts at tuning it. Therefore, we chose to discard this approach.

MAF2: 0.2232954263
MAP: 0.2138418508

- Pseudo Relevance Feedback
Our results will be discussed in Bonus.docx


== Files included with this submission ==
README.txt - This file

index.py - Required file for submission
indexer.py - Perfoms the indexing of directory of documents.
dictionary.txt - Pickled dictionary of terms from the Reuters Training Dataset
postings.txt - Postings List of each term specified in dictionary.txt
postings_plaintext.txt - Contains a human readable index with dictionary word and
			corresponding posting list
lengths.txt - Stores a dictionary of document vector lengths
doc_id_to_courts.txt - Stores a mapping of each document to the "Courts" field

search.py - Required file for submission
search_logic.py - Main implementation of search logic
query_parser.py - Contains simple query parser to split and stem a query string
search_utils.py - Commonly used utility methods for searching
boolean_operations.py - Contains boolean operations used throughout the program
thesaurus_expansion.py - Contains main code logic that performs query expansion with Princeton's wordnet
pseudo_relevance_feedback.py - Contains main code logic that performs pseudo relevance feedback. Not used in actual implementation
Bonus.docx - Some records of our query refinement effort


== Statement of individual work ==

Please initial one of the following statements.

[x] I, A0170229J-A0000000X, certify that I have followed the CS 3245 Information
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
CS3245 lecture notes for the indexing and search algorithm
Stack Overflow for Lesk Algorithm
