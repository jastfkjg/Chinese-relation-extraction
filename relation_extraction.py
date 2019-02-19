#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
this code is based on the paper: 
Chinese Open Relation Extraction and Knowledge Base Establishment
"""

import sys, os
import argparse
from utils import divideSentences, readFile, readDir
from pyltp import SentenceSplitter, Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller

# parser = argparse.ArgumentParser()
# parser.add_argument("model_dir", help="your own model path")
# parser.add_argument("--file", help="test file path")

# args = parser.parse_args()

# ROOTDIR = os.path.join(os.path.dirname(__file__), os.pardir)
# sys.path = [os.path.join(ROOTDIR, "lib")] + sys.path

# Set your own model path
MODELDIR = "/Users/oushu/Documents/test/pyltp/ltp_data_v3.4.0"
# MODELDIR=os.path.join(ROOTDIR, "./ltp_data")

def divideSentences(input):
	"""
	input: string: a paragraph
	return: a list of string, each string is a sentence
	"""
	ret = []
	sentence = ""
	stopList = ['。', '！', '？']
	for i in range(len(input)):
		sentence += input[i]

		if input[i] in stopList:
			ret.append(sentence)
			sentence = ""
	if sentence:
		ret.append(sentence)
	return ret

def findEntities(netags):
	"""
	return: a list of entities index
	"""
	ret = []
	for i in range(len(netags)):
		if netags[i] != 'O':
			if netags[i][0] == 'S':
				ret.append([i])
			elif netags[i][0] == 'B':
				l = []
				j = i
				while j < len(netags) and netags[j][0] != 'E':
					l.append(j)
					j += 1
				if j < len(netags):
					l.append(j)
					ret.append(l)

	return ret


def DSNF1(arcs, entityList, words, netags):
	ret = []
	for i in range(len(entityList) - 1):
		if arcs[entityList[i][-1]].relation == 'ATT':
			index = arcs[entityList[i][-1]].head - 1
			if index < 0:
				continue
			elif arcs[index].relation == 'ATT' and (netags[arcs[index].head - 1] != 'O'):
				firstEntity = ""
				for n in entityList[i]:
					firstEntity += words[n]
				ret.append([ firstEntity, words[arcs[index].head - 1], words[index] ])
	return ret



def DSNF2(arcs, entityList, words):
	"""
	combine DSNF2, DSNF5, DSNF6
	"""
	ret = []
	for i in range(len(entityList) - 1):
		if arcs[entityList[i][-1]].relation == 'SBV':
			index = arcs[entityList[i][-1]].head - 1
			for j in range(i + 1, len(entityList)):
				if arcs[entityList[j][-1]].relation == 'VOB' and arcs[entityList[j][-1]].head - 1 == index:
					firstEntity1, firstEntity2, secondEntity1, secondEntity2 = "", "", "", ""
					for k in range(i + 1, j):
						if arcs[entityList[k][-1]].relation == 'COO' and arcs[entityList[k][-1]].head - 1 == i:
							for n in entityList[k]:
								firstEntity2 += words[n]
					for k in range(j + 1, len(entityList)):
						if arcs[entityList[k][-1]].relation == 'COO' and arcs[entityList[k][-1]].head - 1 == j:
							for n in entityList[k]:
								secondEntity2 += words[n]
					for n in entityList[i]:
						firstEntity1 += words[n]
					for n in entityList[j]:
						secondEntity1 += words[n]

					if firstEntity2 != "":
						ret.append([ firstEntity2, secondEntity1, words[index] ])
						if secondEntity2 != "":
							ret.append([ firstEntity2, secondEntity2, words[index] ])

					ret.append([ firstEntity1, secondEntity1, words[index] ])
					if secondEntity2 != "":
						ret.append([ firstEntity1, secondEntity2, words[index] ])

	return ret

def DSNF3(arcs, entityList, words, postags):
	"""
	combine DSNF3, DSNF4, DSNF5 and DSNF6
	"""
	ret = []
	for i in range(len(entityList) - 1):
		if arcs[entityList[i][-1]].relation == 'SBV':
			index = arcs[entityList[i][-1]].head - 1
			if index > 0 and index + 1 < len(words) and postags[index + 1][0] == 'n':
				relation = words[index] + words[index + 1]
			else:
				relation = words[index]

			for j in range(i + 1, len(entityList)):
				if arcs[entityList[j][-1]].relation == 'POB':
					prep = arcs[entityList[j][-1]].head - 1
					if (arcs[prep].relation == 'ADV' or arcs[prep].relation == 'CMP') and arcs[prep].head - 1 == index:
						firstEntity1, firstEntity2, secondEntity1, secondEntity2 = "", "", "", ""
						for k in range(i + 1, j):
							if arcs[entityList[k][-1]].relation == 'COO' and arcs[entityList[k][-1]].head - 1 == i:
								for n in entityList[k]:
									firstEntity2 += words[n]
						for k in range(j + 1, len(entityList)):
							if arcs[entityList[k][-1]].relation == 'COO' and arcs[entityList[k][-1]].head - 1 == j:
								for n in entityList[k]:
									secondEntity2 += words[n]

						for n in entityList[i]:
							firstEntity1 += words[n]
						for n in entityList[j]:
							secondEntity1 += words[n]

						if firstEntity2 != "":
							ret.append([ firstEntity2, secondEntity1, relation ])
							if secondEntity2 != "":
								ret.append([ firstEntity2, secondEntity2, relation ])

						ret.append([ firstEntity1, secondEntity1, relation ])
						if secondEntity2 != "":
							ret.append([ firstEntity1, secondEntity2, relation ])
	return ret

# DSNF4 is similar to DSNF3
# def DSNF4(arcs, entityList, words):
# 	ret = []
# 	for i in range(len(entityList) - 1):
# 		if arcs[entityList[i]].relation == 'SBV':
# 			index = arcs[entityList[i]].head - 1
# 			for j in range(i + 1, len(entityList)):
# 				if arcs[entityList[j]].relation == 'POB':
# 					prep = arcs[entityList[j]].head - 1
# 					if arcs[prep].relation == 'CMP' and arcs[prep].head - 1 == index:
# 						ret.append([ words[entityList[i]], words[entityList[j]], words[index] ])
# 	return ret

# DSNF5 is similar to DSNF2 or DSNF3
def DSNF5(arcs, entityList, words):
	pass

# DSNF6 is similar to DSNF2 or DSNF3
def DSNF6(arcs, entityList, words):
	pass

def DSNF7(arcs, entityList, words):
	ret = []
	for i in range(len(entityList) - 1):
		if arcs[entityList[i][-1]].relation == 'SBV':
			index = arcs[entityList[i][-1]].head - 1
			for j in range(i + 1, len(entityList)):
				if arcs[entityList[j][-1]].relation == 'VOB':
					prep = arcs[entityList[j][-1]].head - 1
					if arcs[prep].relation == 'COO' and arcs[prep].head - 1 == index:
						firstEntity, secondEntity = "", ""
						for n in entityList[i]:
							firstEntity += words[n]
						for m in entityList[j]:
							secondEntity += words[m]

						ret.append([ firstEntity, secondEntity, words[prep] ])
	return ret

# paragraph = '中国进出口银行与中国银行加强合作。中国进出口银行与中国银行加强合作！'
# paragraph = '德国总统高克'  # DSNF1
# paragraph = '高克访问中国'  # DSNF2
# paragraph = '习近平在上海视察'  # DSNF3
# paragraph = '奥巴马毕业于哈佛大学' # DSNF4
# paragraph = '教师节那天，习近平在北京八一学校看望师生'
# paragraph = '中国共产党第十八届中央委员会第四次全体会议，于2014年10月20日至23日在北京举行。'
# paragraph = '在15日举行的外交部例行记者会上，有记者问及中美贸易谈判的最新进展。'
# paragraph = ['对此，中国外交部发言人耿爽用一句话这样回应称，“耐心稍等，答案很快会揭晓。']

def getRelation(paragraph):
	"""
	paragraph: a list of string, each string is a sentence
	return: a list of relations and a dict which records the number of occurrence of differents DSNF
	"""
	relations = []
	dict_DSNF = {'num_DSNF1': 0, 'num_DSNF2': 0, 'num_DSNF3': 0, 'num_DSNF7': 0, }

	segmentor = Segmentor()
	segmentor.load(os.path.join(MODELDIR, "cws.model"))
	postagger = Postagger()
	postagger.load(os.path.join(MODELDIR, "pos.model"))
	parser = Parser()
	parser.load(os.path.join(MODELDIR, "parser.model"))
	recognizer = NamedEntityRecognizer()
	recognizer.load(os.path.join(MODELDIR, "ner.model"))

	for iteration, sentence in enumerate(paragraph):
		print ("evaluate the " + str(iteration + 1) + "-th sentences")

		sentence = SentenceSplitter.split(sentence)[0]

		words = segmentor.segment(sentence)
		# print("\t".join(words))
		
		postags = postagger.postag(words)
		# list-of-string parameter is support in 0.1.5
		# postags = postagger.postag(["中国","进出口","银行","与","中国银行","加强","合作"])
		# print("\t".join(postags))

		arcs = parser.parse(words, postags)

		# print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))

		netags = recognizer.recognize(words, postags)
		# print("\t".join(netags))

		# labeller = SementicRoleLabeller()
		# labeller.load(os.path.join(MODELDIR, "pisrl.model"))
		# roles = labeller.label(words, postags, arcs)
		# for role in roles:
		#     print(role.index, "".join(
		#             ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))

		entityList = findEntities(netags)
		# print(entityList)
		entities = []
		for i in entityList:
			l = ''
			for j in i:
				l += words[j]
			entities.append(l)
		print("entities in " + str(iteration + 1) + "-th sentence : ", entities)

		DSNF1_ret = DSNF1(arcs, entityList, words, netags)
		DSNF2_ret = DSNF2(arcs, entityList, words)
		DSNF3_ret = DSNF3(arcs, entityList, words, postags)
		DSNF7_ret = DSNF7(arcs, entityList, words)
		# print("DSNF1 result: ", DSNF1_ret)
		# print("DSNF2 result: ", DSNF2_ret)
		# print("DSNF3 result: ", DSNF3_ret)
		# print("DSNF7 result: ", DSNF7_ret)
		relation = []
		for r in DSNF1_ret:
			dict_DSNF['num_DSNF1'] += 1
			relation.append(r)
			relations.append(r)
		for r in DSNF2_ret:
			dict_DSNF['num_DSNF2'] += 1
			relation.append(r)
			relations.append(r)
		for r in DSNF3_ret:
			dict_DSNF['num_DSNF3'] += 1
			relation.append(r)
			relations.append(r)
		for r in DSNF7_ret:
			dict_DSNF['num_DSNF7'] += 1
			relation.append(r)
			relations.append(r)
		print("with entities relation: ", relation)
		print("--" * 30)


	segmentor.release()
	postagger.release()
	parser.release()
	recognizer.release()
	# labeller.release()

	return relations, dict_DSNF

if __name__ == '__main__':

	# getRelation(paragraph)
	
	while True:
		paragraph = input("输入测试句子：")
		if paragraph:
			relations = getRelation(divideSentences(paragraph))
			print ("输入句子中所有的实体关系： ")
			for r in relations:
				print (r)










