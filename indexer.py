import csv
import math
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.util import bigrams, trigrams
import os
from os import listdir
from os.path import join, isfile
import pickle
import sys
import traceback

def index(input_file, output_file_dictionary, output_file_postings):
	# List of document_ids of all docs
	doc_ids = []
	# Map document_id to dictionaries of documents
	documents = {}
	
	reload(sys)
	sys.setdefaultencoding('utf8')
	csv.field_size_limit(sys.maxsize)		
	# Store each document as a dictionary whose keys are the fields
	# of the document.
	fields = ('document_id','title','content','date_posted','court')
	with open(input_file, "r") as csv_file:
		csv_reader = csv.DictReader(csv_file)
		for row in csv_reader:
			if int(row['document_id']) not in doc_ids:
				doc_ids.append(int(row['document_id']))
				documents[str(row['document_id'])] = row
	
	doc_ids.sort();
	print(str(doc_ids))
	# Every term in the dictionary is mapped to a tuple (byte_offset, doc_freq)
	dictionary = {}
	# Every term in the index is mapped to a postings list
	# Every posting in a postings list is the following tuple :
	# (doc_id, term_freq, list of positions)
	index = {}
	# Every doc_id is mapped to document vector length
	lengths = {}

	# For every term in every document, add the document_id of the occuring term
	# to the respective posting list in the index. If term is new, add new key 
	# in dictionary and index
	for doc_id in doc_ids:
		print("Indexing document " + str(doc_id) + " ...")
		# Combine all fields in doc into one text
		document = documents[str(doc_id)]
		text = ""
		for field in fields:
			text = " ".join((text, document[field]))
		#### Preprocess Text ###
		text = text.replace('\n', ' ')
		# tokenize
		sentences = sent_tokenize(text.decode('utf-8'))
		
		# Replace all non-alphanum, non-space chars in each sentence with space
		tokens = []
		for sent in sentences:
			new_sent = []  
			for c in sent:
				if c.isalnum() or c.isspace():
					new_sent.append(c)
				else: 
					new_sent.append(' ')
			sent = ''.join(new_sent)
			tokens.extend([token.lower() for token in word_tokenize(sent)])	
		
		# stem the tokens
		ps = nltk.stem.PorterStemmer()
		stemmed_tokens = [ps.stem(token) for token in tokens]
		
		# maps every unique term in doc to its frequency
		term_to_freq = {}
		# Update the dictionary and postings in the document with every term encountered
		for position in range(0, len(stemmed_tokens)):
			term = stemmed_tokens[position]
			if term not in dictionary:
				dictionary[term] = (None, 1)
				index[term] = [(doc_id, 1, [position])]
				term_to_freq[term] = 1	
			# if doc_id is not already added to term's postings
			elif index[term][dictionary[term][1]- 1][0] != doc_id: 
				# increment df for term
				dictionary[term] = (None, dictionary[term][1] + 1)
				index[term].append((doc_id, 1, [position]))
				term_to_freq[term] = 1	
			# if doc_id is already added to term's postings, increment tf and add the new position of the term in that document
			else:
				term_doc_freq = dictionary[term][1]
				# The last posting in the posting list for this term which is the posting for this doc
				last_posting = index[term][term_doc_freq - 1]
				last_posting[2].append(position)
				index[term][term_doc_freq - 1] = (last_posting[0], last_posting[1] + 1, last_posting[2])
				term_to_freq[term] = term_to_freq[term] + 1	
			
		# calculate and store vector magnitude of doc
		mag_square = 0
		for term in term_to_freq:
			mag_square += math.pow(1 + math.log10(term_to_freq[term]),2)
		vector_len = math.sqrt(mag_square)
 		lengths[doc_id] = vector_len
	
	print("In memory indexing complete!")

	# Add skip pointers to every postings list
	for term in index:
		doc_freq = dictionary[term][1]
		skip_pointers_count = int(math.sqrt(doc_freq))
		skip_size = int(doc_freq / skip_pointers_count)
		# Replace select posting tuples with posting tuples with skip pointers
		for i in range(0, (doc_freq - skip_size - 1)):
			if i % skip_size == 0:
				index[term][i] = (index[term][i][0], index[term][i][1], index[term][i][2], i + skip_size)
	
	print("Skip pointers added in memory!")	

	# Write dictionary and index
	offset = 0
	postings_file = open(output_file_postings, "w")
	sorted_terms = dictionary.keys()
	sorted_terms.sort()

	print("Sorted dictionary terms!")

	# Write all document ids at top of postings file
	postings_file.write(str(doc_ids) + '\n')	
	offset = postings_file.tell()
	
	print("Wrote all doc_ids at top of postings file!")

	# Write index to postings file and corresponding
        # byte offset to dictionary file
	for k in sorted_terms:
		dictionary[k] = (offset,dictionary[k][1])
		postings_file.write(str(index[k]) + '\n')
		offset = postings_file.tell()
	postings_file.flush()
	postings_file.close()
	
	print("Postings file written! Dictionary offset updated in memory!")

	# Write dictionary to dictionary file			
	dictionary_file = open(output_file_dictionary, "wb")
	pickle.dump(dictionary, dictionary_file)		
	dictionary_file.flush()
	dictionary_file.close()

	print("Dictionary file written!")
	
	# Write document vector lengths to lengths file
	lengths_file = open("lengths.txt", "wb")
	pickle.dump(lengths, lengths_file)
	lengths_file.flush()
	lengths_file.close()
	
	print("Lengths file written!")
				
	plaintext_postings_file = open("plaintext_postings.txt", "wb")
	for term in sorted_terms:
		plaintext_postings_file.write(str(term) + "\n")
		plaintext_postings_file.write(str(index[term]) + "\n")

	print("Plaintext_postings file written!")
