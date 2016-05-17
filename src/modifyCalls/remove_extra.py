# -*- coding: utf-8 -*-

#import nltk
import csv
import math
import string
from os import listdir
from os.path import isfile, join
import re
from collections import Counter

corpusDir = "/PATH/TO/CALLS/";
corpus = [corpusDir + f for f in listdir(corpusDir) if isfile(join(corpusDir, f))]

for filename in corpus:
    outputFile = ''
    startLine = 0
    foundFirstContact = False
    with open(filename, 'r') as file:
        for line in file:
            if( not foundFirstContact ):
                if( line[0:2] == 'D:' ):
                    foundFirstContact = True
                    outputFile = outputFile + line
                startLine = startLine + 1
            else:
                # Removes:  [n/a], [paus]
                line = re.sub(r'\[.*\]', '', line)

                # Removes: ( nurse tillagd )
                line = re.sub(r'\(.*\)', '', line)
                outputFile = outputFile + line

    f = open(filename, 'w')
    f.write(outputFile)

