#!/usr/bin/env python
# coding: utf-8

"""
classes.py
Scope: Defines the major classes used by the module.
Authors: Jeffrey Smith, Bill Cramer, Evan French
"""

import re

#Author: Jeffrey Smith
class SentenceStructure:
	"""
	SentenceStructure represents a sentence taken from an input file. It splits the string based on whitespace and adds an END tag.
	"""
	def __init__(self, inString, label = None):
		"""
		Constructor for SentenceStructure.
		
		:param inString: The string that this object will represent.
		:return: Nothing.
		:var originalSentence: Copy of the original string.
		:var originalSentenceArray: An array of [string,string] tuples. The first string is a token, and the second is a holder for tags.
		"""
		self.originalSentence = inString
		self.originalSentenceArray = []
		
		#Split the string by whitespace and add it to the array.
		for x in inString.split():
			if label == None:
				token = [x,""]
			else:
				token = [x,label]
			self.originalSentenceArray.append(token)
			
		#Add an end tag to the end of the array.
		if label == None:
			self.originalSentenceArray.append(["END",""])
		else:
			self.originalSentenceArray[0][1] = label + ":Start"
			self.originalSentenceArray.append(["END",label + ":End"])

	"""
	ModifiedSentenceArray creator for SentenceStructure.
	
	:param inString: The string that this object will represent.
	:return: Nothing.
	:var modifiedSentenceArray: An array of [string,string,int] tuples. The first string is a token, and the second is a holder for tags. The int represents the position in the original string.
	"""
	def generateModifiedSentenceArray(self):
		self.modifiedSentenceArray = []
		
		#Split the string by whitespace and add it to the array.
		counter = 0
        
		for x in self.modifiedSentence.split():
			token = [x,"",counter]
			self.modifiedSentenceArray.append(token)
			counter += 1
		self.modifiedSentenceArray.append(["END",""])
						
		assert(len(self.originalSentenceArray) == len(self.modifiedSentenceArray)), "Assertion failed, sentences don't match. Original Sentence: " + self.originalSentence +" Modified Sentence: " + self.modifiedSentence

#Author: Jeffrey Smith
class BatchContainer:
	"""
	BatchContainer represents a container for running network batches through Tensorflow
	"""
	def __init__(self, bx, by, bs, mapping=None):
		self.bx = bx
		self.by = by
		self.bs = bs
		self.mapping = mapping

#Author: Evan French
class Annotation:
	"""
	Annotation represents a line from the annotation file.
	"""
	def __init__(self, inString):
		"""
		Constructor for Annotation.
		
		:param inString: The string that this object will represent.
		:return: Nothing.
                :var original: Original annotation
                :var concept: String representing concept (i.e. "the sickness").
		:var label: Classification label (i.e. "problem").
		:var line: Line number on which the concept appears.
		:var startWord: Index of first word in the concept.
		:var endWord: Index of the word after the concept ends.
		"""
		self.original = inString

		#Clean up inString into segments we can use
		parse = re.sub(r'c="', '', inString)
		concept = re.sub(r'" \d+:\d+.*$', '', parse)
		after_concept = re.sub(r'c=".*" ', '', inString)
		segments = after_concept.replace(':', ' ').replace('||t=', ' ').replace('"', '').split()

		#Define Annotation properties
		self.concept = concept.strip()	
		self.line = int(segments[0])
		self.startWord = int(segments[1])
		self.endWord = int(segments[3])
		self.label = segments[4]
