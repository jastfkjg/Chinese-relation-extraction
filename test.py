
from relation_extraction import getRelation
from utils import readFile

para = readFile('./wiki_00')
relations, dict_DSNF = getRelation(para)
print("Finished !")
print("Final result: ")
print(relations)
print(dict_DSNF)

