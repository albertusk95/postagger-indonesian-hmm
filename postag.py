from __future__ import division
from collections import Counter
import math

# POS -> POS transition probabilities
# POS -> Word emission probabilities


# make a map for context, emit, and transition
context = dict()
emit = dict()
transition = dict()

# Format training data: word/TAG
filename = 'UI-1M-tagged.txt'

previous = "<s>"
endOfLine = "</s>"
context[previous] = 0
context[endOfLine] = 0

listOfTags = []

strOfWords = ""

print 'Start'

numOfUniqueWords = 39000

'''
# Read the file for the 1st time
with open(filename) as f:
	data = f.read().replace('\n', ' ')
	wordsAndTags = data.split()
	
	print 'Got wordsAndTags'

	for wordAndTag in wordsAndTags:
		wordOnly, tagOnly = wordAndTag.split('/')
		strOfWords = strOfWords + wordOnly + " "
		#print strOfWords

numOfUniqueWords = len(Counter(strOfWords.split()))
'''

print ('Num of unique words: %d' % (numOfUniqueWords))

# Read the file for the 2nd time
with open(filename) as f:
	for line in f:

		previous = "<s>"
		endOfLine = "</s>"
		context[previous] += 1
		context[endOfLine] += 1

		# split line into wordtags with " "
		wordtags = line.split()
        
		for wordtag in wordtags:

			#if wordtag not in listOfWords:
			#	listOfWords.append(wordtag)

			# split wordtag into word, tag with "/"
			word, tag = wordtag.split('/')

			#print 'word, tag'
			#print word
			#print tag
			if tag not in listOfTags:
				listOfTags.append(tag)

			# Count the transition
			transitionKey = previous + " " + tag
			if transitionKey in transition:
				transition[transitionKey] += 1
			else:
				transition[transitionKey] = 1

			# Count the context
			contextKey = tag
			if contextKey in context:
				context[tag] += 1                 
			else:
				context[tag] = 1

			# Count the emission
			emitKey = tag + " " + word
			if emitKey in emit:
				emit[emitKey] += 1
			else:
				emit[emitKey] = 1
			
			previous = tag

		transitionKey = previous + " </s>"
		if transitionKey in transition:
			transition[transitionKey] += 1
		else:
			transition[transitionKey] = 1

		'''
		print transition
		print 'end'

		break
		'''

# Print list of tags
print listOfTags

listOfTags = ['<s>', 'nn', 'nnc', 'nnu', 'jj', 'in', ',', 'vbt', 'cc', 'nnp', 'sym', 'cdp', 'vbi', 'fw', 'sc', '.', 'rb', 'nng', 'cdi', 'cdo', 'neg', 'dt', 'prp', '--', 'md', 'wrb', ':', '-', 'nns', 'prn', 'prl', 'rp', 'vb', 'wp', 'cdc', 'uh', '</s>']

f = open('probs.txt', 'w')

# Print the transition (POS -> POS) probabilities
for key, value in transition.iteritems():
	
	# split key into previous, tag with " "
	previousKey, tagKey = key.split()

	'''
	print key
	print value
	print context[previousKey]
	print value / context[previousKey]
	'''

	# print the probability
	#print ("T %s %f" % (key, value / context[previousKey]))

	transitionInfo = 'T' + ' ' + key + ' ' + str(value / context[previousKey]) + '\n'
	f.write(transitionInfo)

# Print the emission (POS -> Word) probabilities with "E"
for key, value in emit.iteritems():

	# split key into tag, word with " "
	tagEmit, wordEmit = key.split()

	# print the probability
	#print ("E %s %f" % (key, value / context[tag]))

	# Use Laplace Smoothing
	vocabSize = numOfUniqueWords

	# number of occurence of value (pair of tagEmit and wordEmit)
	numOfTimesSymWEmittedAtS = value

	# number of words having tagEmit as the TAG
	totalNumOfSymEmittedByS = context[tagEmit]

	# laplace smoothing probability
	laplaceSmoothingProb = (numOfTimesSymWEmittedAtS + 1) / (totalNumOfSymEmittedByS + vocabSize)

	# emitInfo = 'E' + ' ' + key + ' ' + str(value / context[tagEmit]) + '\n'
	emitInfo = 'E' + ' ' + key + ' ' + str(laplaceSmoothingProb) + '\n'
		
	f.write(emitInfo)

f.close()


# FINDING POS TAGS

print "\n"
print "\n"
print "Input kalimat: "
userInput = raw_input()


# Model Loading

# make a map for transition, emission, possible_tags
possible_tags = dict()
transition = dict()
emit = dict()

# Read the file
modelFile = 'probs.txt'
with open(modelFile) as f:
	for line in f:
		# split line into type, n_context, word, prob
		typeOfProb, n_context, word, prob = line.split()

		# enumerate all tags
		#possible_tags[n_context] = 1  

		if typeOfProb == 'T':
			transitionInfo = n_context + " " + word
			transition[transitionInfo] = float(prob)
		else:
			emitInfo = n_context + " " + word
			emit[emitInfo] = float(prob)



# Forward Step

# split line into words
words = userInput.split()

wordsLen = len(words)

# make maps best_score, best_edge
best_score = dict()
best_edge = dict()


# make maps transition, emission
transition_score = dict()
emission_score = dict()


# start with <s>
best_score["0 <s>"] = 0
best_edge["0 <s>"] = None


for i in range(0, wordsLen):
	for prev in listOfTags:
		for next in listOfTags:
			best_score_key = str(i) + " " + prev
			transition_key = prev + " " + next
			emit_key = next + " " + words[i]

			print '\n'
			print ('i: %d' % (i))
			print ('prev tag: %s' % (prev))
			print ('next tag: %s' % (next))
			print ('best_score_key: %s' % (best_score_key))
			print ('emit: %s' % (emit_key))
			
			if best_score_key in best_score and transition_key in transition:
				
				print 'OK'
				print ('best_score_key_0: %s' % (best_score_key))
				print ('transition_key: %s' % (transition_key))

				if emit_key not in emit:

					print 'Use Laplace Smoothing'

					# compute emission probability using Laplace Smoothing
					vocabSize2 = numOfUniqueWords

					# number of occurence of value (pair of tagEmit and wordEmit)
					numOfTimesSymWEmittedAtS2 = 0

					# number of words having tagEmit as the TAG
					totalNumOfSymEmittedByS2 = context[next]

					# laplace smoothing probability
					emit[emit_key] = (numOfTimesSymWEmittedAtS2 + 1) / (totalNumOfSymEmittedByS2 + vocabSize2)

				
				score = best_score[best_score_key] - math.log(transition[transition_key]) - math.log(emit[emit_key])

				best_score_key = str(i+1) + " " + next
				best_edge_key = str(i+1) + " " + next

				transProb_key = str(i+1) + " " + next
				emitProb_key = str(i+1) + " " + next

				print ('best_score_key_1: %s' % (best_score_key))
				print ('best_edge_key: %s' % (best_edge_key))


				if best_score_key not in best_score:
					print 'best_score_key not in best_score'
					best_score[best_score_key] = score
					best_edge[best_edge_key] = str(i) + " " + prev

					transition_score[transProb_key] = transition[transition_key];
					emission_score[emitProb_key] = emit[emit_key];

					print ('best_score[%s]: %f' % (best_score_key, score))
					print ('best_edge[%s]: %s' % (best_edge_key, str(i)+" "+prev))
				elif best_score_key in best_score and best_score[best_score_key] > score:
					print 'best_score > score'
					best_score[best_score_key] = score
					best_edge[best_edge_key] = str(i) + " " + prev

					transition_score[transProb_key] = transition[transition_key];
					emission_score[emitProb_key] = emit[emit_key];

					print ('best_score[%s]: %f' % (best_score_key, score))
					print ('best_edge[%s]: %s' % (best_edge_key, str(i)+" "+prev))
				

'''
print 'score'		
print best_score
print 'edge'
print best_edge
'''


listOfTagsBeforeEnd = []
listOfProbTagsBeforeEnd = []

for tag in listOfTags:
	best_score_key = str(wordsLen) + " " + tag
	transition_key = tag + " " + "</s>"
	
	if best_score_key in best_score and transition_key in transition:
		listOfTagsBeforeEnd.append(tag)
		listOfProbTagsBeforeEnd.append(best_score[best_score_key] - math.log(transition[transition_key]))


best_score_key = str(wordsLen + 1) + " " + "</s>"
best_edge_key = str(wordsLen + 1) + " " + "</s>"
best_score[best_score_key] = min(listOfProbTagsBeforeEnd)
best_edge[best_edge_key] = str(wordsLen) + " " + listOfTagsBeforeEnd[listOfProbTagsBeforeEnd.index(min(listOfProbTagsBeforeEnd))]



# BACKWARD STEP
tags = []
bestscores = []
transitions = []
emissions = []


#best_edge_key = str(wordsLen + 1) + " " + "</s>"
best_edge_key = str(wordsLen+1) + " " + "</s>"
next_edge = best_edge[best_edge_key]

# append the last best_score to bestscores
bestscores.append(best_score[best_edge_key]);

while next_edge != "0 <s>":
	# Add the substring for this edge to the words
	
	# split next_edge into position, tag
	position, tag = next_edge.split()

	# append tag to tags
	tags.append(tag)

	# append bestscore to bestscores
	bestscores.append(best_score[next_edge]);

	# append transition and emission to transitions and emissions
	transitions.append(transition_score[next_edge]);
	emissions.append(emission_score[next_edge]);

	next_edge = best_edge[next_edge]

tags.reverse()
bestscores.reverse()
transitions.reverse()
emissions.reverse()

# join tags into a string and print
print "\n"

print "User input"
print userInput

print "\n"

print "Sequence of tags"
print tags

print "\n"

print "Best score of each word"
print bestscores
print "\n"
print "Total of best score"
totalVal = 1
for vl in bestscores:
	totalVal = totalVal * vl
print totalVal
print "\n"

print "Transition probabilities"
print transitions
print "\n"
print "Total of transition probabilities"
totalVal = 1
for vl in transitions:
	totalVal = totalVal * vl
print totalVal
print "\n"

print "Emission probabilities"
print emissions
print "\n"
print "Total of emission probabilities"
totalVal = 1
for vl in emissions:
	totalVal = totalVal * vl
print totalVal

