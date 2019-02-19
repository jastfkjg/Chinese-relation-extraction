#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import pandas as pd 
import os

def divideSentences(input):
	"""
	input: string: a paragraph
	return: a list of string, each string is a sentence
	"""
	ret = []
	sentence = ""
	stopList = ['。', '！', '？', '\n']
	for i in range(len(input)):
		sentence += input[i]

		if input[i] in stopList:
			if sentence:
				ret.append(sentence)
			sentence = ""
	if sentence:
		ret.append(sentence)
	return ret

def readFile(filename):
	"""
	read data from json file
	return: a list of stirng, each string is a sentence
	"""
	ret = []
	data = pd.read_json(path_or_buf=filename, orient='records', encoding='utf-8', lines=True)
	texts = data['text']
	for i in range(len(texts)):
		if texts[i]:
			ret += divideSentences(texts[i])

	return ret 

def readDir(dirname):
	"""
	read all files from a directory
	"""
	ret = []
	for filename in os.listdir(dirname):
		filepath = dirname + '/' + filename
		ret += readFile(filepath)

	return ret








