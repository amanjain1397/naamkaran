import argparse
import numpy as np
import os
import sys
import re
from models.MarkovChain import MarkovChain
from models.Nodes import Node

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--dataroot', type=str, required=True, help='location of the text corpus')
parser.add_argument('--order', type= int, default='3', help ='indicates how many previous characters to take into account when picking the next. A lower number represents more random words, whereas a higher number will result in words that match the input words more closely.')
parser.add_argument('--minLength', default='0', help='The minimum length of the generated word')
parser.add_argument('--maxLength', default='-1', help='The maximum length of the generated word')
parser.add_argument('--allowDuplicates', type=bool, default=False, help='Whether generated words are allowed to be the same as words in the input dictionary')
parser.add_argument('--maxAttempts', type=int, default=100, help='The maximum number of attempts to generate a word before failing and throwing an error')
parser.add_argument('--noOfWords', type=int, default=50, help='Number of words to be generated')
parser.add_argument('--toLower', type=bool, default=False, help='lower case the vocabulary')
parser.add_argument('--removeSpecial', type=bool, default=False, help='retains only alphabetic chars')
parser.add_argument('--exceptionSymbols', type=str, default='', help='retain the string of the symbols, e.g. "@$#"')


FLAGS = parser.parse_args()

dataroot = FLAGS.dataroot
order = int(FLAGS.order)    
minLength = int(FLAGS.minLength)
maxLength = int(FLAGS.maxLength)
allowDuplicates = FLAGS.allowDuplicates
maxAttempts = int(FLAGS.maxAttempts)
noOfWords = int(FLAGS.noOfWords)
toLower = FLAGS.toLower
removeSpecial = FLAGS.removeSpecial
exceptionSymbols = FLAGS.exceptionSymbols

if __name__ == "__main__":
    names = open(dataroot).read()
    names = names.split('\n')

    if toLower:
        names = [name.lower() for name in names]
    
    if removeSpecial:
        names = [re.sub('[^A-Za-z' + exceptionSymbols + ']+', '', name) for name in names]

    mc = MarkovChain(order, ''.join(names))
    _ = [mc.addWordToChain(name) for name in names]

    genWords = [] 
    i = 0

    while(i < noOfWords):
        try:
            word = mc.generateWord(minLength, maxLength, allowDuplicates, maxAttempts)
            genWords.append(word)
            i+= 1
        except:
            pass
    #words = [mc.generateWord(minLength, maxLength, allowDuplicates, maxAttempts) for i in range(noOfWords)]
    print((genWords))